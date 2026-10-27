"""P4-D436 (lane HX5): whole numbers each on one row, or in sequence, asked the identifier question.

WHAT WAS MEASURED (lane E0c's strict twin scan, planning-notes/work-2026-10/
wave6/E0c-repair2.md, 'NEW' item 1, on ccebc947): the zoo's
`titled_report.report_ref` -- `RPT` and six figures, one a row, counting up
-- was read as an affixed number and asked nothing. Its description
published the run's percentile ladder and its twin wrote the sequence
again: 598 of 600 real references at 600 rows, 19,998 of 20,000 at 20,000.
The same tree published plain figures counting up across a power of ten
(`99701` up, read as a count: 97 real values in the description and 598 twin
cells at 600 rows) and `ACC` and six figures on about four rows in three (50
real record numbers as rungs), each with nothing asked: every route of the
person rule (plan P4-D401) asks from two rows a value on average, and the
width question asks plain figures of one width only.

THE RULE (`asking._whole_numbers_each_on_one_row`). A column read as a
count, a measurement, numbers too large for a float, an affixed number or
numbers beside labels, whose present cells are words and placeholders (set
aside whatever their share) and whole numbers -- figures alone, or one to
six letters, an optional `-`, `_` or `#`, and figures -- filling the floor's
cells and standing on fewer than two rows a value, and every one different,
or running in sequence under one opening, or letters and five figures or
more, is put P4-D401's identifier question (`keep`, `code`, `identifier`)
where no other question is put to it, and held whole until answered. A
cell carrying a decimal, a unit or any mark after its figures takes the
column out, and so do values that repeat on two rows each or more.

Each case runs the product's own command line, nobody at the keyboard (the
library's small-table switch off, so the 600-row legs stand below the
command's floor: identifier rules hold at every size), and each is red on
the mutant its docstring or the lane's mutants log names (planning-notes/
work-2026-10/wave6/HX5/mutants.log).
"""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from synthtwin import asking, cli, taxonomy

import health_zoo as zoo
import unanswered_identifier_shapes as shapes

_ROWS = 600
_FLOOR_ROWS = 20000

# CHANCE, NOT COPY (stated in plan P4-D436; owner lane ID-ROOM, plan
# P4-D432, whose guarantee covers held blocks by the orchestrator's ruling
# 2 of 2026-10-25). A held column publishes no value, so its twin writes
# made-up record numbers in the column's layouts, and where the real
# values fill a layout's room densely -- 600 or 20,000 references counting
# up among a million six-figure spellings -- a made-up one can carry the
# figures of a real one. The count of such cells is about the share of the
# room the real values fill times the rows; a twin that copies the column
# (the mutant: the rule switched off) writes nearly every row real. The
# bound is a twentieth of the rows: far above chance on every shape here,
# far below a copy.
_CHANCE_SHARE = 20


@pytest.fixture(scope="module")
def ran(tmp_path_factory: pytest.TempPathFactory):
    """Each 600-row shape profiled, generated and validated ONCE for the file.

    The suite's time (the orchestrator's rule of 2026-10-26: a file adds at
    most three minutes): the cases reading the same run share it, and none
    writes into its folder.
    """
    done: "dict[str, tuple[pathlib.Path, dict[str, object]]]" = {}

    def run(kind: str) -> "tuple[pathlib.Path, dict[str, object]]":
        if kind not in done:
            folder = tmp_path_factory.mktemp(kind)
            done[kind] = (folder, shapes.run(folder, kind, _ROWS))
        return done[kind]

    return run


def _check_held(seen: "dict[str, object]", kind: str, rows: int) -> None:
    """0 real values or fragments published, held as record numbers, asked once."""
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    if kind not in shapes.VALIDATION_LIMITS:
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    twin = seen["twin_cells"]
    assert isinstance(twin, int) and twin * _CHANCE_SHARE <= rows, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, seen
    assert asking.ANSWER_IDENTIFIER in asked[0]
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ())
    assert "COLUMNS HELD BACK UNTIL YOU ANSWER" in f"{seen['screen']}"
    # ...and the screen says what the question is about, never that the
    # column is averaged (red on the mutant "falls to the measurements block").
    # Codex's review, item 7: the third shape is named too.
    assert ("THESE COLUMNS HOLD WHOLE NUMBERS THAT EACH STAND ON ONE ROW, RUN IN SEQUENCE, OR "
            "CARRY LETTERS BEFORE FIVE FIGURES OR MORE") in f"{seen['screen']}".replace("\n", " ")
    assert seen["forced_identifiers"] == [kind]


@pytest.mark.parametrize("kind", shapes.ONE_A_ROW)
def test_a_column_of_whole_numbers_each_on_one_row_is_held(ran, kind: str) -> None:
    """Every shape at 600 rows: nothing real published, held, asked once.

    Red on the mutant "the rule switched off" (`_whole_numbers_each_on_one_row`
    false): `refseq` publishes 97 references and its twin writes 598.
    """
    _check_held(ran(kind)[1], kind, _ROWS)


def test_at_the_floor_size_the_column_is_held(tmp_path: pathlib.Path) -> None:
    """The live shape at 20,000 rows, the owner's table floor: one case.

    Every other shape at 20,000 and 200,000 rows is K-S3-64's (its driver,
    kpi_run --slow), as the orchestrator's rule of 2026-10-26 keeps the
    suite's 20,000-row checks to one case a writer. Red on the mutant "the
    rule switched off": `refseq` publishes its ladder and the twin writes
    19,998 of 20,000 real references.
    """
    _check_held(shapes.run(tmp_path, "refseq", _FLOOR_ROWS), "refseq", _FLOOR_ROWS)


def test_a_placeholder_of_nines_at_the_floor_size_is_held(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 3 at 20,000 rows: the run beside `-9999` on one row in fifty.

    Red on the mutant "-1 to -999 only": read as a count, its ladder printed
    and 19,224 of 20,000 twin cells real (wave6/HX5-sk1-work). The other
    shapes repair 1 adds are measured at 20,000 rows by K-S3-64's driver
    (kpi_run --slow), the orchestrator's rule of 2026-10-26 keeping the
    suite's 20,000-row checks to a case or two a writer.
    """
    _check_held(shapes.run(tmp_path, "seqnines", _FLOOR_ROWS), "seqnines", _FLOOR_ROWS)


def test_the_question_is_the_identifier_question_with_keep_first(ran) -> None:
    """`keep`, `code`, `identifier`, the reason named, and no value in its words."""
    folder = ran("refseq")[0]
    entries = _asked_of(folder, "refseq")
    assert len(entries) == 1
    entry = entries[0]
    assert [choice["answer"] for choice in entry["answers_you_can_give"]] == [
        asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER,
    ]
    words = json.dumps(entry)
    assert "RPT" not in words and "3000" not in words
    assert "every one is different" in words
    screen = (folder / "refseq_long-profile.txt").read_text(encoding="utf-8")
    assert "RPT3" not in screen


@pytest.mark.parametrize("kind", ("refseq", "seqcross"))
def test_the_linear_count_is_the_pairwise_count(
    ran, tmp_path: pathlib.Path, kind: str
) -> None:
    """`shapes.count_real` read by its linear counter counts what the pairwise search counts.

    The linear counter is what K-S3-64 reads at 20,000 rows and more (20,000
    real values by 20,000 twin cells); here both read the product's own
    600-row run, and a copy of the column written as the twin, so every
    count is non-zero.
    """
    folder = ran(kind)[0]
    _table, real = shapes.write_table(tmp_path, kind, _ROWS)
    texts = [(folder / f"{kind}_long-{page}").read_text(encoding="utf-8")
             for page in ("profile.json", "profile.txt", "questions.json")]
    with open(folder / f"{kind}_long-twin.csv", encoding="utf-8") as handle:
        cells = [line.split(",")[0] for line in handle.read().splitlines()[1:]]
    # The pairwise search reads 40 cells of each twin (600 by 600 pairs
    # take about 26 seconds).
    for twin in (cells[:40], real[:40], [f"x{value}." for value in real[100:140]]):
        published = texts + [f"p50 {real[3]} and {real[5][:5]}"]
        pairwise = shapes.count_real(real, published, twin, linear=False)
        assert shapes.count_real(real, published, twin, linear=True) == pairwise
    assert shapes.count_real(real, texts, real, linear=True)["twin_cells"] == len(real)


def test_the_linear_count_is_the_pairwise_count_on_every_shape(tmp_path: pathlib.Path) -> None:
    """Every shape K-S3-64 counts, no product run: the two counters agree.

    Each shape's real values are written into texts and cells whole, as a
    number, wrapped in other characters, cut to a fragment and beside a
    point, with cells of no real value between; the pairwise search reads
    the first 60 real values against 90 cells. Red on the mutant "the
    linear counter reads only runs of figures" (`wave6/HX5/mutants-d.log`).
    """
    kinds = (shapes.HELD + shapes.BESIDE + shapes.COUNTED + shapes.LISTED
             + shapes.ONE_A_ROW + shapes.STATED)
    for kind in kinds:
        folder = tmp_path / kind
        folder.mkdir()
        _table, everything = shapes.write_table(folder, kind, _ROWS)
        real = everything[:60]
        if not real:
            continue
        texts = [
            f"p50 {real[0]}, tail [{real[-1]}], mode {real[len(real) // 2][:6]}",
            f"{{\"x\": \"a{real[1]}b\", \"y\": 0.{real[2]}, \"z\": \"{real[3][2:]}\"}}",
            "nothing real here: 12345 and ABCDE",
        ]
        cells = ([f"{value}" for value in real[:30]] + [f"<{value}>" for value in real[30:45]]
                 + [f"{value[:5]}" for value in real[45:]]
                 + [f"Z{place:09d}" for place in range(15)] + real[:15])
        pairwise = shapes.count_real(real, texts, cells, linear=False)
        assert shapes.count_real(real, texts, cells, linear=True) == pairwise, kind
    # ...and the readings lane HX's gate pins on the pairwise search: a value
    # wrapped, a prefix alone, figures printed as a number, and figures
    # inside a decimal or a longer number, which never count.
    for real, texts, cells in (
        (["REC10000000", "REC10000007"], ["nothing here", "RECORD HELD BACK"], ["APT07388860"]),
        (["REC10000000", "REC10000007"], ["a summary naming xxREC10000007yy"],
         ["ZZREC10000000ZZ", "APT07388860"]),
        (["REC10000000", "REC10000007"], ['"layout_prefixes": {"REC": 40}'], []),
        (["02100"], ['"p50": 2100.0', '"rows": 21000'], ["2100", "21000"]),
        (["123,456,789"], ["mode 123456789"], ["123456789.5"]),
        (["ACC30000484"], ['"mode": 30000484.0', '"p50": 130000484.0', "0.30000484"],
         ["KXA30000484"]),
        (["100000"], ['"p53": 82.34100000000001'], ["x100000", "1000001"]),
    ):
        pairwise = shapes.count_real(real, texts, cells, linear=False)
        assert shapes.count_real(real, texts, cells, linear=True) == pairwise, real


# -- the reach: what is asked, and what is not --------------------------------

_DRAW = random.Random(20261025)
# 450 record numbers, 150 of them on a second row: no run, not all different.
_ACC = _DRAW.sample(range(100000, 1000000), 450)


def _run(start: int, count: int, opening: str = "") -> "list[str]":
    return [f"{opening}{start + place}" for place in range(count)]


_REACHED = {
    "the live shape": _run(300001, 600, "RPT"),
    "references at random": [f"RPT{value}" for value in _DRAW.sample(range(100000, 1000000), 600)],
    # A table at the owner's floor: 1 to 20,000 is five figures wide for the most part.
    "row numbers at the floor size": _run(1, 20000),
    "plain across a power of ten": _run(99701, 600),
    "plain at random": [f"{value}" for value in _DRAW.sample(range(100000, 10000000), 600)],
    "a run with one number twice": _run(99701, 599) + ["99701"],
    "ACC on four rows in three": [f"ACC{value}" for value in _ACC] + [f"ACC{value}" for value in _ACC[:150]],
    "letters, a mark and figures": _run(10001, 600, "ACC-"),
    "beside words and placeholders": _run(99701, 400) + ["UNKNOWN"] * 150 + ["-1"] * 50,
    "written as whole decimals": [f"{value}.0" for value in range(99701, 100301)],
    "the floor's cells exactly": _run(99701, 11),
    # Repair 1, skeptic 1's item 2 (red on the mutant "one to six letters,
    # an optional mark, figures"): openings of up to twelve letters, letters
    # with figures and a mark, a mark and letters after the figures.
    "eight letters before the figures": _run(300001, 600, "SPECIMEN"),
    "twelve letters before the figures": _run(300001, 600, "ABCDEFGHIJKL"),
    "an accession with its year": _run(10001, 600, "S24-"),
    "letters, two figures and a mark": _run(300001, 600, "AB12_"),
    "a mark and a letter after the figures": [f"{value}-A" for value in range(300001, 300601)],
    "a mark and two letters after the figures": [f"ACC{value}_XY" for value in range(300001, 300601)],
    # Item 3 (red on the mutant "-1 to -999 only"): a repeated negative
    # placeholder of four figures or more, and minus nines of any width.
    "beside -9999 on one row in fifty": [("-9999" if place % 50 == 7 else f"{99701 + place}")
                                         for place in range(600)],
    "beside -99999 once": _run(99701, 599) + ["-99999"],
    "beside -12345 on the floor's rows": _run(99701, 589) + ["-12345"] * 11,
    # Item 4 (red on the mutant "every cell read"): one stray cell in a hundred.
    "a negative of four figures": _run(99701, 599) + ["-1234"],
    "one decimal among a run": _run(99701, 599) + ["99708.5"],
    "one glued letter among references": _run(300001, 599, "RPT") + ["RPT300008A"],
    # Item 5 (red on the mutant "every one different"): all but one value in a hundred.
    "at random with one twice": (lambda drawn: [f"{value}" for value in drawn] + [f"{drawn[0]}"])(
        _DRAW.sample(range(10000, 10000000), 599)),
    "a register with gaps and one twice": (
        lambda drawn: [f"{value}" for value in drawn] + [f"{drawn[3]}"])(
        sorted(_DRAW.sample(range(99000, 99000 + 1200), 599))),
    # Codex's item 1 (red on the mutant "every placeholder closes a gap"):
    # a run on about four rows in three, beside a `0` or nines outside it.
    "a repeating run beside a 0": _run(99701, 450) + _run(99701, 150) + ["0"],
    "a repeating run beside 999999": _run(99701, 450) + _run(99701, 150) + ["999999"],
    # Codex's item 2 (red on the mutant "the width read after the noughts"):
    # padded references on about four rows in three.
    "padded references that repeat": [f"RPT{value:06d}" for value in range(1, 451)]
    + [f"RPT{value:06d}" for value in range(1, 151)],
}

_NOT_REACHED = {
    "readings with decimals": [f"{value / 100:.2f}" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a unit after the figures": [f"{value} mg" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a currency sign": [f"${value}" for value in _DRAW.sample(range(1000, 99999), 600)],
    "a letter after the figures": [f"{value}A" for value in range(300001, 300601)],
    "a unit glued to the figures": [f"{value}mg" for value in range(12345, 12945)],
    "decimals on two cells in a hundred": _run(99701, 588) + [f"{99000 + place}.5" for place in range(12)],
    # Repair 1, skeptic 1's item 1: what the whole suite measured reached.
    # Under five figures for the most part (route four's line, CODES-3's
    # plain keys, P4-D428 (d)): readings, row numbers of a short table.
    "row numbers of a short table": _run(1, 600),
    "readings 1 to 199 beside -999": _run(1, 199) + ["-999"] * 15,
    "1 to 599 with one twice": _run(1, 599) + ["1"],
    "four figures counting by sevens": [f"{1000 + place * 7:,}" for place in range(40)],
    "ages that repeat": [f"{_DRAW.randint(18, 90)}" for _row in range(600)],
    "years that repeat": [f"{_DRAW.randint(2000, 2024)}" for _row in range(600)],
    "a run on two rows a value": [f"{99701 + place // 2}" for place in range(600)],
    "fewer than the floor's cells": _run(99701, 10),
    "thirteen letters before the figures": _run(300001, 600, "ABCDEFGHIJKLM"),
    "one value alone": ["12345"] * 600,
    # K-P4-24's decision-7 column: `10` to `99` on 114 rows covers its range.
    "a two-figure run that repeats": [f"{10 + place % 90}" for place in range(114)],
}


@pytest.mark.parametrize("label", sorted(_REACHED))
def test_the_rule_reaches(label: str) -> None:
    """Each column the rule asks, read as a count (the role is read apart)."""
    assert asking._whole_numbers_each_on_one_row(_REACHED[label], taxonomy.ROLE_COUNT)


@pytest.mark.parametrize("label", sorted(_NOT_REACHED))
def test_the_rule_leaves_measurements(label: str) -> None:
    """True measurements, repeats, units and decimals are not asked (the owner's principle)."""
    assert not asking._whole_numbers_each_on_one_row(_NOT_REACHED[label], taxonomy.ROLE_COUNT)


def test_a_writers_row_index_is_left_out() -> None:
    """Skeptic 1's item 1 (a): `Unnamed: 0` holding 0..n-1 or 1..n in file order is the file's numbering.

    It carries no fact beyond the row count, and the twin writes it as the
    row sequence (plan P4-D76). Red on the mutant "no row index set aside".
    """
    for start in (0, 1):
        index = _run(start, 20000)
        assert not asking._whole_numbers_each_on_one_row(index, taxonomy.ROLE_COUNT, False, "Unnamed: 0")
        assert not asking._whole_numbers_each_on_one_row(index, taxonomy.ROLE_COUNT, False, "rownames")
        # ...its own name, or another order, is the table's data and is asked.
        assert asking._whole_numbers_each_on_one_row(index, taxonomy.ROLE_COUNT, False, "record_id")
        assert asking._whole_numbers_each_on_one_row(index[::-1], taxonomy.ROLE_COUNT, False, "Unnamed: 0")


def test_a_declared_decimal_comma_reads_decimals() -> None:
    """Codex's item 4: `9,701` up under `--decimal-comma` are readings, not whole numbers.

    Red on the mutant "the comma read as a mark between thousands whatever
    was declared".
    """
    readings = [f"{value // 1000},{value % 1000:03d}" for value in range(9701, 29701)]
    assert asking._whole_numbers_each_on_one_row(readings, taxonomy.ROLE_CONTINUOUS)
    assert not asking._whole_numbers_each_on_one_row(readings, taxonomy.ROLE_CONTINUOUS, True)


def test_the_run_is_read_in_one_pass() -> None:
    """Codex's item 6: the run arm reads the smallest, the largest and the count, and sorts nothing."""
    assert "sorted" not in asking._each_on_one_row_arm.__code__.co_names
    shuffled = _run(100000, 5000)
    random.Random(6).shuffle(shuffled)
    assert asking._each_on_one_row_arm(shuffled + shuffled[:1000])[0] == "sequence"


def test_keep_says_what_numbers_beside_labels_publish() -> None:
    """Codex's item 5: `keep` of numbers beside labels names their numbers' statistics and their words."""
    choices = asking._each_on_one_row_choices(taxonomy.ROLE_COMPOUND, 11)
    kept = choices[0].publishes
    assert "points along its range" in kept and "rows share" in kept and "its words" in kept


@pytest.mark.parametrize(
    "role",
    (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_TEXT, taxonomy.ROLE_IDENTIFIER,
     taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK, taxonomy.ROLE_LONG_TAIL),
)
def test_the_rule_reads_only_the_number_roles(role: str) -> None:
    """Labels publish no value held by one row; dates and clock times are not keys."""
    assert not asking._whole_numbers_each_on_one_row(_REACHED["the live shape"], role)


# -- never a second question ---------------------------------------------------


def test_a_column_of_one_width_keeps_the_width_question(tmp_path: pathlib.Path) -> None:
    """Plain figures of one width, one a row, are the width question's, as before."""
    table = tmp_path / "width.csv"
    table.write_text(
        "width,value\n" + "".join(f"{300001 + row},{row % 7}\n" for row in range(_ROWS)),
        encoding="utf-8", newline="\n",
    )
    _profile(table, tmp_path)
    entries = _asked_of_file(tmp_path / "width-questions.json", "width")
    assert len(entries) == 1 and _saw(entries[0], asking._FIGURES_ALL_ONE_WIDTH)


def test_a_repeating_key_keeps_the_person_question(tmp_path: pathlib.Path) -> None:
    """A key on two rows a value or more is the person rule's, as before."""
    shapes.run(tmp_path, "randkey", _ROWS)
    entries = _asked_of(tmp_path, "randkey")
    assert len(entries) == 1 and "different value(s) over" in f"{entries[0]['what_synthtwin_saw']}"


def test_a_count_of_dates_asked_with_this_shape_is_held(tmp_path: pathlib.Path) -> None:
    """One question, the date-count question (Q3), merged with this shape, and held.

    Days in Unix seconds (each at the start of its day), one a row, crossing 1,000,000,000 (two
    widths, so no width question): Q3's rule B asks it, and the merged
    question offers `identifier`, so the column is held until answered as
    the width question's merge is. Red on the mutant "only the width
    question merges into Q3" (its values published, no hold).
    """
    start = 1_000_000_000 - 1_000_000_000 % 86400 - 300 * 86400
    table = tmp_path / "stamps.csv"
    table.write_text(
        "stamp,value\n" + "".join(f"{start + 86400 * row},{row % 7}\n" for row in range(_ROWS)),
        encoding="utf-8", newline="\n",
    )
    _profile(table, tmp_path)
    entries = _asked_of_file(tmp_path / "stamps-questions.json", "stamp")
    assert len(entries) == 1 and _saw(entries[0], asking._EACH_ON_ONE_ROW_OPENING)
    offered = [choice["answer"] for choice in entries[0]["answers_you_can_give"]]
    assert asking.ANSWER_IDENTIFIER in offered and len(offered) > 3
    document = json.loads((tmp_path / "stamps-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "stamp"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    published = (tmp_path / "stamps-profile.json").read_text(encoding="utf-8")
    assert f"{start + 86400 * 300}" not in published and f"{start}" not in published


def _dated_table(folder: pathlib.Path, rows: int, words: str) -> pathlib.Path:
    """Days written YYYYMMDD, one a row, then `words` cells of no figure (Codex's item 3)."""
    import datetime

    start = datetime.date(2023, 1, 1)
    count = rows * 49 // 50 if words == "codes" else rows * 3 // 5
    cells = [(start + datetime.timedelta(days=place)).strftime("%Y%m%d") for place in range(count)]
    if words == "codes":
        cells += ["OTHER"] * (rows - count)
    else:
        cells += [f"note{chr(97 + place % 26)}{chr(97 + place // 26 % 26)}" for place in range(rows - count)]
    table = folder / "dated.csv"
    table.write_text("lab,arm\n" + "".join(f"{cell},{place % 3}\n" for place, cell in enumerate(cells)),
                     encoding="utf-8", newline="\n")
    return table


def _one_merged_question(folder: pathlib.Path, offered_too: str) -> None:
    entries = _asked_of_file(folder / "dated-questions.json", "lab")
    assert len(entries) == 1, entries
    offered = [choice["answer"] for choice in entries[0]["answers_you_can_give"]]
    assert offered[-1] == asking.ANSWER_IDENTIFIER and offered_too in offered, offered
    assert _saw(entries[0], asking._EACH_ON_ONE_ROW_OPENING)
    published = (folder / "dated-profile.json").read_text(encoding="utf-8")
    block = [one for one in json.loads(published)["columns"] if one["name"] == "lab"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert "2023" not in published and "2024" not in published


def test_dates_beside_codes_put_one_question_and_hold(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: the codes question (Q2) carries this shape and `identifier`, one question, held.

    Red on the mutant "HX5 beside Q2" (two questions, Q2's `keep` leaving
    the hold); answering that one question `keep` releases the column.
    """
    table = _dated_table(tmp_path, _ROWS, "codes")
    _profile(table, tmp_path)
    _one_merged_question(tmp_path, asking.ANSWER_REAL_VALUE)
    questions = json.loads((tmp_path / "dated-questions.json").read_text(encoding="utf-8"))
    for entry in questions["asked"]:
        if entry["column"] == "lab":
            entry["your_answer"] = asking.ANSWER_KEEP
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    answered = tmp_path / "answered"
    answered.mkdir()
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{table}", "--out-dir", f"{answered}", "--answers", f"{answers}"],
                        small_tables_refused=False) == 0
    block = [one for one in json.loads((answered / "dated-profile.json").read_text(
        encoding="utf-8"))["columns"] if one["name"] == "lab"][0]
    assert block["role"] != taxonomy.ROLE_IDENTIFIER


def test_mostly_dates_put_one_question_and_hold(tmp_path: pathlib.Path) -> None:
    """Codex's item 3, at 20,000 rows: 12,000 days beside 8,000 words, Q6 carries this shape, held.

    Red on the mutant "HX5 beside Q6" (two questions on one column).
    """
    _profile(_dated_table(tmp_path, _FLOOR_ROWS, "words"), tmp_path)
    _one_merged_question(tmp_path, asking.ANSWER_DATES)


def test_a_declared_decimal_comma_is_asked_nothing(tmp_path: pathlib.Path) -> None:
    """Codex's item 4: readings `9,701` up under `--decimal-comma` stay readings, asked nothing."""
    table = tmp_path / "lab.csv"
    table.write_text("lab,arm\n" + "".join(f'"{value // 1000},{value % 1000:03d}",{value % 3}\n'
                                           for value in range(9701, 9701 + _ROWS)),
                     encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--decimal-comma", "lab"],
                        small_tables_refused=False) == 0
    assert _asked_of_file(tmp_path / "lab-questions.json", "lab") == [] if (
        tmp_path / "lab-questions.json").exists() else True
    block = [one for one in json.loads((tmp_path / "lab-profile.json").read_text(
        encoding="utf-8"))["columns"] if one["name"] == "lab"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS
    screen = (tmp_path / "lab-profile.txt").read_text(encoding="utf-8")
    assert "EACH STAND ON ONE ROW" not in screen


# -- the answers give back the description as each reading writes it ---------


@pytest.mark.parametrize(
    ("answer", "typed"),
    [
        (asking.ANSWER_KEEP, []),
        (asking.ANSWER_CODE, ["--code", "refseq"]),
        (asking.ANSWER_IDENTIFIER, ["--identifier", "refseq"]),
    ],
)
def test_each_answer_gives_the_description_of_its_reading(
    ran, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, answer: str, typed: "list[str]"
) -> None:
    """Byte for byte the description the rule-off tree writes with that reading typed."""
    folder = ran("refseq")[0]
    questions = json.loads((folder / "refseq_long-questions.json").read_text(encoding="utf-8"))
    for entry in questions["asked"]:
        if entry["column"] == "refseq":
            entry["your_answer"] = answer
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    answered = tmp_path / "answered"
    answered.mkdir()
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{folder / 'refseq_long.csv'}", "--out-dir", f"{answered}",
                         "--answers", f"{answers}"], small_tables_refused=False) == 0
    before = tmp_path / "before"
    before.mkdir()
    with monkeypatch.context() as patched:
        patched.setattr(asking, "_whole_numbers_each_on_one_row", lambda *_args: False)
        with shapes.nobody_at_the_keyboard():
            assert cli.main(["profile", f"{folder / 'refseq_long.csv'}", "--out-dir",
                             f"{before}"] + typed, small_tables_refused=False) == 0
    for page in ("refseq_long-profile.json", "refseq_long-profile.txt"):
        assert (answered / page).read_bytes() == (before / page).read_bytes(), page
    block = [one for one in json.loads((answered / "refseq_long-profile.json").read_text(
        encoding="utf-8"))["columns"] if one["name"] == "refseq"][0]
    if answer == asking.ANSWER_KEEP:
        assert block["role"] == taxonomy.ROLE_AFFIXED
    elif answer == asking.ANSWER_IDENTIFIER:
        assert block["role"] == taxonomy.ROLE_IDENTIFIER


# -- the zoo's live column ------------------------------------------------------


def test_the_zoo_report_reference_is_held_unanswered(tmp_path: pathlib.Path) -> None:
    """The zoo's `titled_report`, unanswered: report_ref asked, and no reference anywhere.

    Its title rows are not answered either, so the run reads its header where
    it can; the reference column is asked wherever it stands.
    """
    table = [one for one in zoo.TABLES if one.name == "titled_report"][0]
    header, rows = table.build(_ROWS, 20261016)
    names = ["report_ref", "ward", "admitted", "went_home"]
    assert header == names
    source = tmp_path / "titled_report.csv"
    source.write_text(
        ",".join(names) + "\n" + "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8", newline="\n",
    )
    _profile(source, tmp_path)
    real = [row[0] for row in rows]
    texts = [(tmp_path / f"titled_report-{page}").read_text(encoding="utf-8")
             for page in ("profile.json", "profile.txt", "questions.json")]
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["generate", f"{tmp_path / 'titled_report-profile.json'}", "--out-dir",
                         f"{tmp_path}", "--seed", "0", "--replace"]) == 0
    with open(tmp_path / "titled_report-twin.csv", encoding="utf-8") as handle:
        cells = [line.split(",")[0] for line in handle.read().splitlines()[1:]]
    counted = shapes.count_real(real, texts, cells)
    assert counted["description_values"] == 0 and counted["description_fragments"] == 0, counted
    assert counted["twin_cells"] * _CHANCE_SHARE <= _ROWS, counted
    entries = _asked_of_file(tmp_path / "titled_report-questions.json", "report_ref")
    assert len(entries) == 1 and _saw(entries[0], asking._EACH_ON_ONE_ROW_OPENING)


# -- helpers -------------------------------------------------------------------


def _profile(table: pathlib.Path, folder: pathlib.Path) -> None:
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"],
                        small_tables_refused=False) == 0


def _saw(entry: "dict[str, object]", opening: str) -> bool:
    """Whether what the entry says synthtwin saw opens with these words."""
    return f"{entry['what_synthtwin_saw']}".startswith(opening)


def _asked_of_file(path: pathlib.Path, column: str) -> "list[dict[str, object]]":
    asked = json.loads(path.read_text(encoding="utf-8"))["asked"]
    return [entry for entry in asked if entry["column"] == column]


def _asked_of(folder: pathlib.Path, kind: str, stem: str = "") -> "list[dict[str, object]]":
    return _asked_of_file(folder / f"{stem or kind + '_long'}-questions.json", kind)
