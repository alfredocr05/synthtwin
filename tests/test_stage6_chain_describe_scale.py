"""Lane CHs (plan P4-D462): the chain's describe at scale, behind its switch, held to the bytes it wrote.

THE GATE OF LANE CHs. `chain.describe` holds every per-row structure of
the switched describe in one byte or one machine word a row: the row
hashes in one buffer of 32 bytes a row, the tabled rows as the short list
of the rows set aside, each column's starting bands in one byte a row,
the levels read by mapping one byte a row, and the self-test's sample
kept by a bounded selection whose occurrences are counted without a
dictionary over every row. The description is a function of the data,
not of how it is read, so this file holds:

- THE BYTES: the switched description and the private notes of an
  invented table raising the chain's paths (numbers with blanks, a pair
  blank together, a binary with 40 % blanks, labels, dates, a held record
  number, duplicate rows at the sample's cut, records holding nothing) are
  the bytes the code without this lane wrote (its base 5220c90c; since
  batch 4q's merge, the line it merged onto), read whole and one column a
  group; a table whose held column repeats keeps the chain off with that
  code's bytes;
- THE SAMPLE: the bounded selection equals the full sort of every row's
  key on adversarial ties (rows of one hash, rows sharing the bits the
  occurrences are marked by, rows set aside);
- THE HASHES: the buffer holds the listed hashes, and the content hash
  reads either alike;
- ONE BYTE A ROW: `read_column` holds about a byte a row beside its
  dictionaries over distinct texts, traced at 10,000 rows, so a list a
  row restored is red.

Every table is invented here; the key is a fixed test key. Every check at
20,000 rows or more is the driver's (`tools/measurements/
kpi_chain_describe_scale.py`, K-S6-15, under `kpi_run --slow`).
"""

import dataclasses
import gc
import hashlib
import json
import pathlib
import random
import tracemalloc
import typing

import pytest

from synthtwin import asking, chain, chain_rules, cli, reading

TEST_KEY = bytes(range(32))
ROWS = 3000
# The self-test's sample lowered so that it cuts this table (the sample's
# ties then decide which rows the screen reads, and so the seeds).
SAMPLE = 500

# The bytes of the line without this lane (the switched command, this file's
# tables, each run saying one row a person): the description's sha256, the
# private notes' sha256 and the families. Re-taken at batch 4q's merge of
# the lane on that line's head `fd29238b`, read whole and one column a group,
# and the merged head writes them exactly. The lane's base `5220c90c` wrote
# `9b71d6a3...` for the paths table's description and `9de74a6d...` for the
# held table's private notes (the other two digests the same): between the
# two trees lane CHa2's `procedure.l2_cut` and `w_te` (plan P4-D451) moved the
# first, and lane GRa's reason for keeping the chain off beside a held column
# that repeats (`OFF_HELD_REPEATS`, plan P4-D449) the second, measured there.
FROZEN = {
    "paths": (
        "93f7599d15c30d6afab698b6c202906491545140c73d3854865a4c2a4609a6a5",
        "3d7b6c328b88a07d8ee7585d76e7a3a6aa9f96533a13cd5aae21327503f07aa1",
        8,
    ),
    "held_repeats": (
        "7292b9265e512c2227ed47d030493b8ef9d7e84fdc1391527a7a14d781b1ab69",
        "41062874cbb1e9d50e99dd11c9f469df7b8d94c56aca8069c0b03acc72084f11",
        0,
    ),
}


def _paths_rows(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An invented table of one row a person raising the chain's paths."""
    draw = random.Random(seed)
    header = ["level_a", "level_b", "count_c", "flag", "group", "kind", "seen_on", "score"]
    groups = ("north", "south", "east", "west")
    kinds = ("one", "two", "three", "four", "five", "six")
    out: "list[list[str]]" = []
    for row in range(rows):
        base = draw.gauss(120, 15)
        blank = draw.random() < 0.05
        both = blank and draw.random() < 0.5
        group = draw.choice(groups)
        out += [[
            "" if blank else f"{base:.1f}",
            "" if both else f"{0.6 * base + draw.gauss(30, 6):.1f}",
            f"{min(int(draw.expovariate(0.4)), 12)}",
            "" if draw.random() < 0.4 else ("1" if draw.random() < 0.3 + 0.1 * groups.index(group) else "0"),
            group,
            kinds[min(int(draw.expovariate(0.5)), 5)],
            f"2022-{1 + draw.randrange(12):02d}-{1 + draw.randrange(28):02d}",
            f"{draw.randrange(20, 80)}",
        ]]
    # Duplicate rows, one to three more of a row, so the occurrences reach
    # 3 near the sample's cut.
    for at in range(60):
        for _copy in range(1 + at % 3):
            out[200 + 3 * at + _copy] = list(out[at])
    return header, out


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]", blank_records: int) -> pathlib.Path:
    lines = [",".join(header)] + [",".join(row) for row in rows] + ["," * (len(header) - 1)] * blank_records
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _switched(folder: pathlib.Path, table: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> "tuple[str, str, int]":
    """The switched command's description and private notes, as sha256, and its families."""
    data = folder / "installation"
    data.mkdir(mode=0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    key.write_bytes(TEST_KEY)
    captured: "list[chain.Chained]" = []
    describe = chain.describe

    def capturing(*arguments, **keywords):  # type: ignore[no-untyped-def]
        found = describe(*arguments, **keywords)
        captured.append(found)
        return found

    monkeypatch.setattr(chain, "describe", capturing)
    monkeypatch.setattr(chain_rules, "SELFTEST_SMALL", SAMPLE)
    (folder / "out").mkdir()
    # Every table here is one row a person, and the run says so (lane GRa's
    # subject question, plan P4-D449, holds the chain while it is open; batch
    # 4q's merge of this lane, as the line's other chain tests answer it).
    code = cli.main(
        ["profile", str(table), "--out-dir", str(folder / "out"), "--replace"],
        chain=cli.ChainRun(folder=str(data), rows_per_person=asking.ANSWER_ONE_ROW_EACH),
        small_tables_refused=False,
    )
    assert code == 0
    written = sorted((folder / "out").glob("*-profile.json"))
    assert len(written) == 1 and len(captured) == 1
    found = captured[0]
    private = json.dumps(
        {
            "notes": list(found.notes),
            "seeds": [list(seed) for seed in found.seeds],
            "chosen": [[child, list(parents), list(levels)] for child, parents, levels in found.chosen],
            "content": found.content,
            "moments": found.moments,
        },
        sort_keys=True,
    ).encode("utf-8")
    families = len(found.statistical["chain"]) if isinstance(found.statistical, dict) else 0
    return hashlib.sha256(written[0].read_bytes()).hexdigest(), hashlib.sha256(private).hexdigest(), families


@pytest.mark.parametrize("way", ["whole", "one column a group"])
def test_the_switched_description_holds_the_base_s_bytes_read_whole_and_one_column_a_group(tmp_path, monkeypatch, capsys, way):
    if way != "whole":
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
        monkeypatch.setattr(reading, "WALK_BYTES", 1)
    header, rows = _paths_rows(ROWS, 7)
    table = _write(tmp_path / "paths.csv", header, rows, 11)
    found = _switched(tmp_path, table, monkeypatch)
    capsys.readouterr()
    assert found[2] > 0
    assert found == FROZEN["paths"]


def _held_rows(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The paths table beside a record number that repeats (900 numbers): the open question holds it."""
    header, body = _paths_rows(rows, seed)
    return ["record_no"] + header, [[f"V{1000000 + at % 900:07d}"] + body[at] for at in range(len(body))]


def test_a_held_column_that_repeats_keeps_the_chain_off_with_the_base_s_bytes(tmp_path, monkeypatch, capsys):
    header, rows = _held_rows(ROWS, 8)
    table = _write(tmp_path / "held.csv", header, rows, 0)
    found = _switched(tmp_path, table, monkeypatch)
    capsys.readouterr()
    assert found[2] == 0
    assert found == FROZEN["held_repeats"]


def _full_sort(hashes: "list[bytes]", tabled: "list[int]", size: int) -> "list[int]":
    """The first build's sample: every tabled row keyed, all sorted, the smallest kept (contract 4.6b.8)."""
    seen: "dict[bytes, int]" = {}
    keyed: "list[tuple[bytes, bytes, int, int]]" = []
    for at in range(len(tabled)):
        one = hashes[tabled[at]]
        occurrence = seen[one] if one in seen else 0
        seen[one] = occurrence + 1
        word = occurrence.to_bytes(8, "big")
        keyed += [(hashlib.blake2b(one + word, digest_size=8, person=b"synthtwin.smp.1").digest(), one, occurrence, at)]
    keyed = sorted(keyed)
    return [entry[3] for entry in keyed[: min(size, len(keyed))]]


def test_the_bounded_sample_is_the_full_sort_s_rows_in_its_order_on_ties():
    draw = random.Random(11)
    for trial in range(40):
        rows = draw.choice([1, 2, 40, 900, 5000])
        if trial % 4 == 0:
            # Rows that share the 25 bits the occurrences are marked by.
            hashes = [bytes([9, 8, 7, 6]) + bytes([draw.randrange(3)]) + bytes(27) for _ in range(rows)]
        elif trial % 4 == 1:
            hashes = [bytes(32)] * rows
        else:
            pool = [hashlib.blake2b(bytes([kind % 251, kind // 251]), digest_size=32).digest() for kind in range(draw.choice([2, 50, rows]))]
            hashes = [draw.choice(pool) for _ in range(rows)]
        excluded = sorted(draw.sample(range(rows), min(rows - 1, draw.choice([0, 1, 11]))))
        tabled = [row for row in range(rows) if row not in set(excluded)]
        size = draw.choice([1, 7, 400, 20000])
        expected = _full_sort(hashes, tabled, size)
        assert chain.sample_rows(hashes, tabled, size) == expected
        buffer = bytearray(b"".join(hashes))
        assert chain.sample_rows(buffer, tabled, size) == expected
        walked = chain._selection(buffer, chain._rows_of(rows, excluded), chain._rows_of(rows, excluded), min(size, len(tabled)))
        assert walked == expected


def test_the_row_hashes_in_one_buffer_are_the_listed_hashes(tmp_path):
    header, rows = _paths_rows(400, 3)
    table = reading.read_table(str(_write(tmp_path / "h.csv", header, rows, 2)), small_cell_floor=11)
    held, filled = chain.row_hash_buffer(table)
    listed, filled_too = chain.row_hashes(table)
    assert bytes(held) == b"".join(listed) and filled == filled_too and len(held) == 32 * table.n_rows
    assert chain.content_hash(held, filled) == chain.content_hash(listed, filled)
    assert chain.content_hash(held) == chain.content_hash(listed)


def test_read_column_keeps_about_one_byte_a_row(tmp_path):
    """A column of 10,000 rows and 40 distinct texts: what `read_column` hands back holds a few bytes a row.

    The first build handed back the codes as a list, a Python number a row
    (8 bytes a row of pointers and the list's slack); this build hands back
    one byte a row for the codes and one for the blank marks, beside the
    moment layer's three. The bound, 6.5 bytes a row, is red on a list a
    row restored. (Its PEAK is the classifier's own reading of the column,
    about 53 bytes a row at its most on base and head alike, measured in
    P4-D462: `taxonomy`'s, not the chain's.)
    """
    count = 10000
    draw = random.Random(4)
    cells = [f"{draw.randrange(40) * 2.5:.1f}" for _ in range(count)]
    path = tmp_path / "one.csv"
    path.write_text("x\n" + "\n".join(cells) + "\n", encoding="utf-8", newline="\n")
    from synthtwin import profile, taxonomy

    table = reading.read_table(str(path), small_cell_floor=11)
    settings = taxonomy.Settings(small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    block = document["columns"][0]
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    reading.column_values(table, 0)
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    found = chain.read_column(table, 0, block, settings, declared, "", 0)
    kept = tracemalloc.get_traced_memory()[0] - before
    tracemalloc.stop()
    assert found is not None and found.agrees and isinstance(found.codes, bytearray)
    assert kept / count < 6.5, kept / count


def _held_at_the_columns_end(folder: pathlib.Path, rows: int, monkeypatch: pytest.MonkeyPatch) -> int:
    """The bytes the chain's modules allocated and still hold where describe has read every column, at `rows` rows.

    Read at the stage probe's "ladder and codes" (`chain._probed`), from a
    `tracemalloc` snapshot of the blocks whose allocating line is in
    `chain.py` or `chain_moments.py`: the classifier's own reading and the
    table's cells are other modules' and do not count.
    """
    folder.mkdir()
    header, body = _paths_rows(rows, 7)
    table = _write(folder / f"paths-{rows}.csv", header, body, 11)
    seen: "dict[str, int]" = {}

    def probe(stage: str, counts: "dict[str, int]") -> None:
        if stage == "ladder and codes":
            # The garbage collected first: what a collection has not yet
            # reached moved this reading from -2.1 to 8.6 bytes a row a
            # column with the collector's state alone (the whole suite read
            # -2.14); collected, it reads 2.82 in every state (MEASURED).
            gc.collect()
            mine = tracemalloc.take_snapshot().filter_traces(
                [tracemalloc.Filter(True, "*synthtwin/chain.py"), tracemalloc.Filter(True, "*synthtwin/chain_moments.py")]
            )
            seen[stage] = sum(stat.size for stat in mine.statistics("filename"))

    monkeypatch.setattr(chain, "_probed", probe)
    tracemalloc.start()
    try:
        _switched(folder, table, monkeypatch)
    finally:
        tracemalloc.stop()
    return seen["ladder and codes"]


def test_the_chain_holds_a_few_bytes_a_row_a_column_where_it_has_read_every_column(tmp_path, monkeypatch, capsys):
    """What describe holds once it has read every column, beyond what it holds at its start, a row a column.

    Read as the rise between 2,000 and 4,000 rows of one invented table of
    eight columns, so what does not grow with the rows cancels, after a
    first run that warms the process, and with the garbage collected before
    each reading. The first build held a list of 32-byte hashes (about 81
    bytes a row), the tabled rows' places (about 36) and three levels a
    column: 26.6 bytes a row a column here; this build holds one level a
    column beside the moment layer's codes: 2.8 (MEASURED, plan P4-D462).
    A GATE DEVICE at 2,000 to 4,000 rows, below the table floor: it counts
    what the chain holds, not the chain phase's traced peak at 200,000 rows
    (owed to a named window). The bound, 10 bytes a row a column, is red
    on the first build's structures.
    """
    # A first run, unmeasured, so that what the process makes once (its
    # first reading of the shapes and the screen's margins) counts in neither.
    _held_at_the_columns_end(tmp_path / "w", 1000, monkeypatch)
    small = _held_at_the_columns_end(tmp_path / "a", 2000, monkeypatch)
    large = _held_at_the_columns_end(tmp_path / "b", 4000, monkeypatch)
    capsys.readouterr()
    rise = (large - small) / (2000 * 8)
    print(f"held {rise:.2f} bytes a row a column")
    assert 0 < rise < 10.0, rise


def test_the_chain_reads_no_column_again_where_the_description_kept_its_reading(tmp_path, monkeypatch, capsys):
    """THE SETTLED READING HANDED OVER (LANE CHs RULINGS 2 (2)): the chain's column reading re-runs no decision.

    Before this lane the switched describe read every eligible column twice:
    once to describe it, once for the chain (taxonomy's whole decision
    again, 96 per cent of the chain's column reading). Now the chain takes
    the description's own reading, kept as one entry a distinct spelling,
    wherever it was read under the chain's own arguments: on the paths
    table not one column is read again once the description is done (red
    if the chain re-reads), and the bytes are the base's (the first case).
    """
    from synthtwin import taxonomy

    header, rows = _paths_rows(ROWS, 7)
    table = _write(tmp_path / "paths.csv", header, rows, 11)
    phase = {"chain": False, "reads": 0}
    read_the_column = taxonomy._read_the_column

    def counting(*arguments, **keywords):  # type: ignore[no-untyped-def]
        if phase["chain"]:
            phase["reads"] += 1
        return read_the_column(*arguments, **keywords)

    def probe(stage: str, counts: "dict[str, int]") -> None:
        if stage == "start":
            phase["chain"] = True

    monkeypatch.setattr(taxonomy, "_read_the_column", counting)
    monkeypatch.setattr(chain, "_probed", probe)
    found = _switched(tmp_path, table, monkeypatch)
    capsys.readouterr()
    assert found == FROZEN["paths"]
    assert phase["chain"] and phase["reads"] == 0


def test_a_kept_reading_is_taken_only_under_the_chain_s_own_arguments():
    """`taxonomy.spellings_read` takes a kept reading only where every argument it reads under is the kept one's.

    A kept map that is not the column's (a stand-in here) is returned when
    the arguments match, so the case sees which map was taken, and the
    column is read again when any argument differs: a declaration, the
    decimal comma, how a workbook stores it, the rows, or the settings
    beyond the person columns. Red on a check that always takes the kept
    reading.
    """
    from synthtwin import taxonomy

    cells = ["1.5", "2.5", "", "4.0"] * 50
    settings = taxonomy.Settings(small_cell_floor=11)
    narrowed = taxonomy.counted_for_the_column(taxonomy.for_the_column(settings, "x"), "x")
    fresh = taxonomy.spellings_read(cells, "x", settings)
    stand_in: "dict[str, tuple[str, float | None, str]]" = {"1.5": ("stand-in", None, "1.5")}
    kept = taxonomy.KeptSpellings(len(cells), narrowed, False, False, False, "", stand_in)
    assert taxonomy.spellings_read(cells, "x", settings, kept=kept) is stand_in
    assert taxonomy.spellings_read(cells, "x", dataclasses.replace(settings, person_columns=("x",)), kept=kept) is stand_in
    for changed in (
        {"forced_code": True},
        {"forced_measurement": True},
        {"forced_decimal_comma": True},
        {"stored_as": "number"},
    ):
        assert taxonomy.spellings_read(cells, "x", settings, kept=kept, **changed) is not stand_in
    shorter = taxonomy.KeptSpellings(len(cells) - 1, narrowed, False, False, False, "", stand_in)
    assert taxonomy.spellings_read(cells, "x", settings, kept=shorter) == fresh
    other = taxonomy.KeptSpellings(len(cells), dataclasses.replace(narrowed, small_cell_floor=12), False, False, False, "", stand_in)
    assert taxonomy.spellings_read(cells, "x", settings, kept=other) == fresh


def test_a_reading_is_kept_for_the_chain_only_where_it_was_read_under_the_chain_s_own_arguments():
    """`taxonomy.keep_spellings` keeps no reading taken under an argument the chain does not read under.

    THE READING HANDED OVER IS THE ONE THE DESCRIPTION IS BUILT FROM
    (LANE CHs RULINGS 2 (2)). The chain reads a column with no identifier,
    pair, placeholder-day, judged-candidate, counted-unit, affixed or
    kept-unit argument, and over every row: a reading taken under any of
    them is refused, so the chain reads such a column again under its own.
    One reading at every default is kept. Red on any refusal dropped
    (skeptic 1's mutants M2 and M2b).
    """
    from synthtwin import taxonomy

    values = ["1.5", "2.5", "", "4.0", "7", "9.25"] * 40
    settings = taxonomy.Settings(small_cell_floor=11)
    read = taxonomy._read_the_column(values, len(values), settings)
    held = taxonomy.HeldReading(values, len(values), settings, False, False, False, False, False, (), (), read)
    kept = taxonomy.keep_spellings(held)
    assert isinstance(kept, taxonomy.KeptSpellings)
    assert kept.spellings == taxonomy.spellings_read(values, "x", settings)
    for changed in (
        {"forced_identifier": True},
        {"described_as_pair": True},
        {"kept_placeholder_days": ("9999-01-01",)},
        {"judged_candidates": ("x",)},
        {"counted_unit": 7},
        {"described_as_affixed": True},
        {"units_kept": "mg"},
        {"n_rows": len(values) + 1},
    ):
        assert taxonomy.keep_spellings(dataclasses.replace(held, **changed)) is None, changed


def _with_ineligible_rows(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The paths table after a written row index and a row number counted from one, and before a column of free text."""
    header, body = _paths_rows(rows, seed)
    draw = random.Random(seed + 100)
    words = ("seen", "today", "follow", "up", "in", "two", "weeks", "stable", "pain", "less", "after", "rest")
    return ["Unnamed: 0", "row_no"] + header + ["remark"], [
        [f"{at}", f"{at + 1}"] + body[at] + [" ".join(draw.choice(words) for _ in range(3 + draw.randrange(9)))] for at in range(len(body))
    ]


def test_the_chain_lets_go_of_every_kept_reading_ineligible_columns_included(tmp_path, monkeypatch, capsys):
    """Every reading the description kept is let go by the chain's loop over the columns, before the search.

    The search carries the switched describe's peak, so a kept reading
    of a column the chain sets aside only once the description is done (a
    written row index, which the written form names a sequence) is let go
    as the loop passes it, as an eligible column's is once read (the
    statistics skeptic's item 6); free text is never kept at all (the
    next case). Red on the ineligible column's reading kept.
    """
    header, rows = _with_ineligible_rows(ROWS, 9)
    table = _write(tmp_path / "ineligible.csv", header, rows, 0)
    seen: "dict[str, object]" = {}
    describe = chain.describe

    def watching(*arguments, **keywords):  # type: ignore[no-untyped-def]
        kept = arguments[8] if len(arguments) > 8 else keywords["kept"]
        seen["before"] = sorted(kept)
        found = describe(*arguments, **keywords)
        seen["after"] = sorted(kept)
        seen["ineligible"] = sorted(header.index(f"{entry['column']}") for entry in found.statistical["ineligible"])
        return found

    monkeypatch.setattr(chain, "describe", watching)
    found = _switched(tmp_path, table, monkeypatch)
    capsys.readouterr()
    assert found[2] > 0
    ineligible = seen["ineligible"]
    assert isinstance(ineligible, list) and ineligible
    assert set(ineligible) & set(seen["before"]), seen
    assert seen["after"] == [], seen


def _notes_rows(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The paths table beside two columns of notes, every row's its own, and two of longer notes, 150 a column, each written many times."""
    header, body = _paths_rows(rows, seed)
    draw = random.Random(seed + 200)
    words = ("seen", "today", "follow", "up", "in", "two", "weeks", "stable", "pain", "less", "after", "rest")
    repeated = [[" ".join(draw.choice(words) for _ in range(40)) + f" {column}-{at}" for at in range(150)] for column in range(2)]
    return header + ["note_0", "note_1", "long_0", "long_1"], [
        body[at]
        + [" ".join(draw.choice(words) for _ in range(12)) + f" {column}-{at}" for column in range(2)]
        + [repeated[column][at % 150] for column in range(2)]
        for at in range(len(body))
    ]


def test_no_reading_of_free_text_is_kept_and_every_kept_byte_is_counted(tmp_path, monkeypatch, capsys):
    """CODEX'S CASE, SMALL (LANE CHs RULINGS 7 (1)): no reading the chain never reads is kept, and what is kept counts its bytes.

    Columns of long notes: at 2,000,000 rows twenty columns of 100,000
    notes of 2,000 characters passed both spelling counts, and their kept
    maps would have held about 4.3 GB. Notes of every row's own are free
    text, which the chain's own classifier sets aside, so no reading of
    them is built for the chain; long notes each written many times are
    labels the chain reads, kept with the bytes their spellings retain
    (`retained`) counted against the table's bound, past which the column
    is read again by the chain, the same description and private notes.
    A GATE DEVICE at 2,000 rows (the measured claim is plan P4-D462's).
    Red on the free-text reading kept, and on the bound in bytes not
    checked.
    """
    from synthtwin import taxonomy

    header, rows = _notes_rows(2000, 12)
    table = _write(tmp_path / "notes.csv", header, rows, 0)
    seen: "dict[str, object]" = {}
    describe = chain.describe

    def watching(*arguments, **keywords):  # type: ignore[no-untyped-def]
        kept = arguments[8] if len(arguments) > 8 else keywords["kept"]
        seen["kept"] = {place: (one.retained, sum(taxonomy._kept_bytes(text) for text in one.spellings)) for place, one in kept.items()}
        found = describe(*arguments, **keywords)
        seen["set_aside"] = {f"{entry['column']}": f"{entry['reason']}" for entry in found.statistical["ineligible"]}
        return found

    monkeypatch.setattr(chain, "describe", watching)
    (tmp_path / "kept").mkdir()
    found = _switched(tmp_path / "kept", table, monkeypatch)
    kept = seen["kept"]
    assert isinstance(kept, dict)
    notes = {header.index("note_0"), header.index("note_1")}
    long_notes = [header.index("long_0"), header.index("long_1")]
    assert not notes & set(kept), sorted(kept)
    assert seen["set_aside"] == {"note_0": "free_text", "note_1": "free_text"}, seen["set_aside"]
    assert set(long_notes) <= set(kept), sorted(kept)
    assert all(retained == counted > 0 for retained, counted in kept.values()), kept
    whole = sum(retained for retained, _counted in kept.values())
    assert whole <= taxonomy.KEPT_BYTES_A_TABLE
    # The bound in bytes one byte short of what the table's kept readings
    # retain: the last column kept is read again by the chain.
    monkeypatch.setattr(taxonomy, "KEPT_BYTES_A_TABLE", whole - 1)
    (tmp_path / "bound").mkdir()
    bounded = _switched(tmp_path / "bound", table, monkeypatch)
    assert set(seen["kept"]) == set(kept) - {max(kept)}, (sorted(seen["kept"]), sorted(kept))
    capsys.readouterr()
    assert found[2] > 0
    assert found == bounded


def _bounded_rows(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Columns of known spellings: 40, 150, 40, 40, 40, 50 and 5 different ones, in that order."""
    words = ("north", "south", "east", "west", "mid")
    header = ["k0", "wide", "k1", "k2", "k3", "late", "small"]
    return header, [
        [
            f"{(at % 40) * 1.5:.1f}",
            f"{(at % 150) * 0.7 + 300:.1f}",
            f"{(at * 7 % 40) * 0.5 + 200:.1f}",
            f"{(at * 11 % 40) * 0.3 + 7:.1f}",
            f"{(at * 3 % 40) * 2.5 + 300:.1f}",
            f"{(at % 50) * 1.1:.1f}",
            words[at % 5],
        ]
        for at in range(rows)
    ]


def test_the_kept_bounds_hold_and_a_column_past_them_is_read_again(tmp_path, monkeypatch, capsys):
    """THE BOUNDS PINNED (the lane's combined verify, finding B): a column past either bound is not kept, and the chain reads it.

    The column bound lowered to 64 spellings and the table's to 200: of
    columns of 40, 150, 40, 40, 40, 50 and 5 spellings, the second passes
    its column's bound and the sixth the room the first five leave (40),
    so neither is in the kept map `chain.describe` receives, and the
    chain reads both again (`taxonomy.spellings_read` handed no kept
    map); the last fits the room left. The description and the private
    notes are the run's at the shipped bounds, where every column is
    kept. Red on the table's bound not checked in `profile` and on the
    column's bound not checked in `taxonomy.keep_spellings`.
    """
    from synthtwin import taxonomy

    header, rows = _bounded_rows(ROWS)
    table = _write(tmp_path / "bounded.csv", header, rows, 0)
    seen: "dict[str, object]" = {"read": []}
    describe = chain.describe
    spellings_read = taxonomy.spellings_read

    def watching(*arguments, **keywords):  # type: ignore[no-untyped-def]
        kept = arguments[8] if len(arguments) > 8 else keywords["kept"]
        seen["kept"] = sorted(kept)
        seen["read"] = []
        return describe(*arguments, **keywords)

    def reading_again(values, name, *arguments, **keywords):  # type: ignore[no-untyped-def]
        if keywords.get("kept") is None:
            seen["read"] += [name]  # type: ignore[operator]
        return spellings_read(values, name, *arguments, **keywords)

    monkeypatch.setattr(chain, "describe", watching)
    monkeypatch.setattr(taxonomy, "spellings_read", reading_again)
    (tmp_path / "shipped").mkdir()
    shipped = _switched(tmp_path / "shipped", table, monkeypatch)
    assert seen["kept"] == list(range(len(header))) and seen["read"] == [], seen
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_COLUMN", 64)
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_TABLE", 200)
    (tmp_path / "lowered").mkdir()
    lowered = _switched(tmp_path / "lowered", table, monkeypatch)
    capsys.readouterr()
    places = [header.index(name) for name in ("k0", "k1", "k2", "k3", "small")]
    assert seen["kept"] == places, seen
    assert seen["read"] == ["wide", "late"], seen
    assert lowered == shipped


def test_a_kept_reading_is_built_only_into_its_room(monkeypatch):
    """THE BOUNDS CHECKED AS THE MAP IS BUILT (LANE CHs RULINGS 7 (2)): a column refused makes at most about its room.

    A column of 20,000 different spellings, traced with `tracemalloc`:
    under a column bound of 64 its map stops at the 65th spelling, so what
    the refusal made stays under four times 64 spellings' bytes (built
    whole first, it made the 20,000 entries' map: Codex measured
    189,516,400 bytes made and dropped at two million); with no room left
    in the table nothing is begun, and with 100 spellings left at most
    about 100 are made. AT THE SHIPPED BOUNDS (LANE CHs RULINGS 8 (1), the
    lane's second verify): where the table's kept readings hold no
    spelling and leave the bytes of 100, the column is refused having
    made about that room, where built into its own bound and held to the
    room only afterwards it made its whole map (1,695,760 bytes, the
    verify's). Red on either bound checked only once the map is built,
    and on the table's room in bytes compared only once the column is
    built while some room is left (the table's spelling bound cannot bind
    at the shipped figures: P4-D462's stated limit (i)).
    """
    from synthtwin import profile, taxonomy

    count = 20000
    values = [f"{at * 0.37:.2f}" for at in range(count)]
    settings = taxonomy.Settings(small_cell_floor=11)
    gathered: "list[taxonomy.HeldReading]" = []
    described = taxonomy.profile_column("x", 1, values, count, settings, kept=gathered)
    held = gathered[0]
    entry = taxonomy.KEPT_SLOT_BYTES + 16

    def made(call: "typing.Callable[[], object]") -> "tuple[object, int]":
        tracemalloc.start()
        try:
            found = call()
            most = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        return found, most

    # The shipped bounds, before any is lowered: the room in bytes of 100
    # spellings left, every spelling's room left.
    shipped = {0: taxonomy.KeptSpellings(count, settings, False, False, False, "", {}, taxonomy.KEPT_BYTES_A_TABLE - 100 * entry)}
    _none, most = made(lambda: profile._keep_for_the_chain(shipped, 1, held, described, []))
    assert sorted(shipped) == [0], sorted(shipped)
    assert most < 4 * 100 * entry, most
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_COLUMN", 64)
    found, most = made(lambda: taxonomy.keep_spellings(held))
    assert found is None and most < 4 * 64 * entry, most
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_COLUMN", 1 << 18)
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_TABLE", 1000)
    for left in (0, 100):
        stand_in = {f"{at}": ("", None, f"{at}") for at in range(1000 - left)}
        kept = {0: taxonomy.KeptSpellings(count, settings, False, False, False, "", stand_in, 0)}
        _none, most = made(lambda: profile._keep_for_the_chain(kept, 1, held, described, []))
        assert sorted(kept) == [0], sorted(kept)
        assert most < 4 * max(left, 4) * entry, (left, most)
    kept = {}
    profile._keep_for_the_chain(kept, 1, held, described, [])
    assert sorted(kept) == [], "20,000 spellings pass a table's bound of 1,000"
    monkeypatch.setattr(taxonomy, "KEPT_SPELLINGS_A_TABLE", 1 << 21)
    profile._keep_for_the_chain(kept, 1, held, described, [])
    assert sorted(kept) == [1] and kept[1].spellings == taxonomy.spellings_read(values, "x", settings)


def test_the_ledger_never_calls_k_s6_15_improved_while_a_shape_is_over_its_bar():
    """K-S6-15 BINDS EVERY SHAPE (Codex's item 4 on the lane's repair 1, LANE CHs RULINGS 7 (4)).

    Its rule asks the projected peak under 1,900 MB and the CPU under 4
    hours on each of the three shapes, and its bounds held the numeric
    shape's alone, so a value over its bar on the code-heavy or mixed
    shape was judged IMPROVED, asking for GREEN. With every shape's two
    keys bound, a value inside every bar is the only one IMPROVED, one
    key over its bar on any shape is OPEN-WORSE, and the recorded value
    keeps the entry OPEN with its excesses. Red on a shape's keys left
    out of the bounds.
    """
    import kpi_rules

    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-S6-15"]
    within: "dict[str, float]" = {}
    for shape in ("numeric", "mixed", "codes"):
        within[f"{shape}_peak_mb_2m_projected"] = 1800.0
        within[f"{shape}_cpu_hours_2m_projected"] = 3.8
    assert set(entry["expected"]) == set(entry["target"]) == set(within)
    assert kpi_rules.judge(entry, within, seconds_count=True).word == kpi_rules.IMPROVED
    for key in within:
        over = dict(within, **{key: 2000.0 if "_peak_mb_" in key else 4.5})
        assert kpi_rules.judge(entry, over, seconds_count=True).word == kpi_rules.OPEN_WORSE, key
    assert entry["status"] == "OPEN"
    assert kpi_rules.judge(entry, entry["value_at"]["value"], seconds_count=True).word == kpi_rules.OPEN_WORSE


def _driver() -> typing.Any:
    """The KPI driver of this lane, `tools/measurements/kpi_chain_describe_scale.py`, read from beside this file."""
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_chain_describe_scale.py"
    spec = importlib.util.spec_from_file_location("kpi_chain_describe_scale", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_cpu_target_reads_the_screen_at_the_sample_the_projected_size_draws():
    """THE SAMPLE'S JUMP (Codex's item 5 on the lane's repair 1, LANE CHs RULINGS 7 (5)).

    Every measured size draws the self-test's 20,000-row sample and a
    table of 2,000,000 rows draws 200,000, which the screen reads: the
    key the target judges takes the screen's seconds at the largest size
    times the samples' ratio in place of the screen's own line. On the
    numeric shape's record (219.0, 1,479.3 and 3,715.0 CPU s, the screen
    26.3, 26.8 and 27.0) the line gives 4.14 hours and the adjusted
    reading 4.20, as the plan states; with no screen the two agree. Red
    on the adjustment dropped.
    """
    driver = _driver()
    sizes = [200_000, 500_000]
    adjusted, line = driver.projected_cpu_seconds(sizes, [1479.3, 3715.0], [26.8, 27.0], 2_000_000)
    assert abs(line - 14893.5) < 0.01 and round(line / 3600, 2) == 4.14
    assert abs(adjusted - (14893.5 - 28.0 + 270.0)) < 0.01 and round(adjusted / 3600, 2) == 4.2
    assert driver.projected_cpu_seconds(sizes, [1479.3, 3715.0], [0.0, 0.0], 2_000_000) == (line, line)
    # Below 1,000,000 tabled rows the sample stays at 20,000: the screen stands at its largest size's seconds.
    below, line_below = driver.projected_cpu_seconds(sizes, [1479.3, 3715.0], [26.8, 27.0], 800_000)
    assert abs(below - (line_below - 27.2 + 27.0)) < 0.01


def test_a_run_cut_short_returns_its_record_and_lets_go_of_its_installation(tmp_path, capsys):
    """THE DRIVER'S CUT (Codex's items 6 and 7 on the lane's repair 1, LANE CHs RULINGS 7 (6) and (7)).

    A run past its cut stopped at its first stage's end, and the
    bookkeeping's own last reading raised the cut again, outside its
    handler: no record and no clean-up. Cut at once, the run now returns
    its record, says the stage it reached, and removes its installation
    folder. Its counting metric is named for what it counts: the levels
    each table counted over the rows was asked at. A GATE DEVICE of 600
    rows. Red on the cut left armed.
    """
    driver = _driver()
    header, rows = _paths_rows(600, 5)
    table = _write(tmp_path / "cut.csv", header, rows, 0)
    found = driver.run(str(table), tmp_path / "out", 0, 0, False, 1e-9, "")
    capsys.readouterr()
    assert found["cut_at"] == "plain description", found["cut_at"]
    assert [row["stage"] for row in found["stages"]] == ["plain description", "written document"]
    assert not (tmp_path / "out" / "installation").exists()
    assert found["members_asked_at_l0_l1_l2"] == [0, 0, 0] and "members_counted_at_l0_l1_l2" not in found
    assert chain._probed is not None and chain.describe.__module__ == "synthtwin.chain"
