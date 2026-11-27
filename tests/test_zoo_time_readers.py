"""P4-D473 (lane TR): time readers -- zone words after a stamp.

WHAT WAS MEASURED (step 0 of the lane, on 820d55c3 at 20,000 rows, the
owner's table floor on, through the zoo's own `run_table`: profile, the
answer rounds, generate at seed 0, validate). The zoo's `zoned_stamps`
table writes Eastern stamps followed by their zone word
(`2024-10-29 09:28:34 EDT`); no layout read the word, so the column was
free text and its twin wrote filler on 20,000 of 20,000 cells: the analyst's
pattern, forms and shapes checks of `dst_zones_and_words` failed there.

THE RULE (plan P4-D473, item (c)). A stamp followed by ONE space and a zone
word of a closed list is read with the offset the word names, as `UTC` and
`GMT` already were: `EST EDT CST CDT MST MDT PST PDT AKST AKDT HST` and
`WET WEST CET CEST EET EEST`, each in its family, its standard word first
(`parsing._LAYOUT_ZONE_FIELDS`). A layout names the family (`{EST/EDT}`),
so a column's EDT and EST are its two offsets, its instants are read as
any column of two offsets is, and its twin writes, for every offset it
writes, the family's word for that offset. `IST` and `BST`, which name two
zones each, are never read; nor is a column mixing families. No zone
database is consulted: the words and offsets are the table. Which offset
is in force on a date is lane DST's (plan P4-D474): the word follows the
offset, so the zoo's check that each word is the one in force on its date
passes once DST's offsets follow the date.

Each case is red on the mutant its docstring names.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random
import re

from synthtwin import cli, parsing

import unanswered_identifier_shapes as shapes

# The closed list, family by family, as the reader must read it.
FAMILIES = {
    "EST/EDT": (("EST", "-05:00"), ("EDT", "-04:00")),
    "CST/CDT": (("CST", "-06:00"), ("CDT", "-05:00")),
    "MST/MDT": (("MST", "-07:00"), ("MDT", "-06:00")),
    "PST/PDT": (("PST", "-08:00"), ("PDT", "-07:00")),
    "AKST/AKDT": (("AKST", "-09:00"), ("AKDT", "-08:00")),
    "HST": (("HST", "-10:00"),),
    "WET/WEST": (("WET", "+00:00"), ("WEST", "+01:00")),
    "CET/CEST": (("CET", "+01:00"), ("CEST", "+02:00")),
    "EET/EEST": (("EET", "+02:00"), ("EEST", "+03:00")),
}
# How the date and clock before the word may be written: strftime forms a
# generator writes, each a production of the layout grammar.
STAMP_FORMS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%Y%m%d %H%M%S",
    "%d-%b-%Y %H:%M:%S",
)


def _stamp_layout(cell: str, family: str) -> "str | None":
    """The first layout `layouts_of` gives the cell whose offset field is the family and which reads it, as a format name."""
    for text in parsing.layouts_of(cell):
        name = parsing.layout_format(text)
        items = parsing.layout_items(name)
        if (
            parsing.layout_offset_field(name) == family
            and items is not None
            and parsing.layout_reading(cell, items) is not None
        ):
            return name
    return None


def _write(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return path


def run(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    column: str,
    typed: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Profile (nobody at the keyboard), generate at seed 0 and validate; what one column came to."""
    path = _write(folder, header, rows)
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace", *typed])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir",
                                  f"{folder}", "--seed", "0", "--replace"])
            validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                  f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}", "--replace"])
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == column][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    place = table[0].index(column)
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "settings": document["settings"],
        "cells": [row[place] for row in table[1:]],
        "real": [row[header.index(column)] for row in rows],
    }


# -- (c) zone words ---------------------------------------------------------


def test_every_zone_word_reads_with_the_offset_it_names() -> None:
    """Each word of the closed list, after a stamp and one space, reads at its own offset and writes back.

    Mutant: `parsing._layout_offsets` without its zone-word production
    (no layout reads the word: every cell here unread).
    """
    assert parsing.zone_words() == tuple(word for family in FAMILIES for word, _offset in FAMILIES[family])
    for family, words in FAMILIES.items():
        for word, offset in words:
            cell = f"2024-07-01 10:15:00 {word}"
            name = _stamp_layout(cell, family)
            assert name == f"layout {{YYYY}}-{{MM}}-{{DD}} {{HH}}:{{MI}}:{{SS}} {{{family}}}", (cell, name)
            assert parsing.is_layout_format(name)
            items = parsing.layout_items(name)
            assert items is not None
            read = parsing.layout_reading(cell, items)
            assert read is not None and read[1] == offset, (cell, read)
            assert parsing.layout_cell(items, read[0], offset, read[2], 0) == cell
            assert parsing.layout_offset_writable(name, offset)
            assert not parsing.layout_offset_writable(name, "Z")


def test_words_of_two_meanings_and_other_spellings_do_not_read() -> None:
    """`IST` and `BST` name two zones each and are never read; nor is a word without its space, in lower case, or unlisted.

    Mutant: `IST` added to `parsing._LAYOUT_ZONE_FIELDS` (it reads).
    """
    for cell in (
        "2024-07-01 10:15:00 IST",
        "2024-07-01 10:15:00 BST",
        "2024-07-01 10:15:00EDT",
        "2024-07-01 10:15:00 edt",
        "2024-07-01 10:15:00  EDT",
        "2024-07-01 10:15:00 ET",
        "2024-07-01 10:15:00 EDTX",
        "2024-07-01 10:15:00 JST",
    ):
        assert parsing.layouts_of(cell) == (), cell


def test_a_generated_sweep_of_zone_stamps_reads_and_writes_back() -> None:
    """THE CLASS, CLOSED BY A SWEEP (LANE I4r RULINGS 1 (4)): 5,100 generated stamps, every family, word and form.

    Each cell is read under its family's layout at the offset its word
    names, written back byte for byte, and written again at every other
    offset of its family with that offset's own word, which reads back at
    that offset; an offset the family names no word for is refused by
    `layout_offset_writable` and by `layout_offset_added`. Mutant: the
    writer's zone arm writing the standard word whatever the offset (every
    daylight word written back as its standard one).
    """
    draw = random.Random(20261109)
    checked = 0
    start = datetime.datetime(2001, 1, 1)
    for _round in range(50):
        for family, words in FAMILIES.items():
            for word, offset in words:
                for form in STAMP_FORMS:
                    moment = start + datetime.timedelta(seconds=draw.randrange(25 * 365 * 86400))
                    cell = f"{moment.strftime(form)} {word}"
                    name = _stamp_layout(cell, family)
                    assert name is not None, cell
                    items = parsing.layout_items(name)
                    assert items is not None
                    read = parsing.layout_reading(cell, items)
                    assert read is not None and read[1] == offset, (cell, read)
                    assert parsing.layout_cell(items, read[0], offset, read[2], 0) == cell
                    for other, other_offset in words:
                        again = parsing.layout_cell(items, read[0], other_offset, read[2], 0)
                        assert again.endswith(f" {other}"), (cell, again)
                        back = parsing.layout_reading(again, items)
                        assert back is not None and back[1] == other_offset
                    assert not parsing.layout_offset_writable(name, "+05:30")
                    checked += 1
    assert checked == 50 * 17 * len(STAMP_FORMS)


def _eastern_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Event stamps with their Eastern zone word, the word the one in force on the date (US rules from 2007)."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        day = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(730))
        moment = datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))
        second_sunday_march = datetime.date(day.year, 3, 8) + datetime.timedelta(days=(6 - datetime.date(day.year, 3, 8).weekday()) % 7)
        first_sunday_november = datetime.date(day.year, 11, 1) + datetime.timedelta(days=(6 - datetime.date(day.year, 11, 1).weekday()) % 7)
        word = "EDT" if second_sunday_march < day < first_sunday_november else "EST"
        rows += [[f"EV{500000 + index}", f"{moment:%Y-%m-%d %H:%M:%S} {word}", f"{draw.randint(1, 9)}"]]
    return ["event_ref", "seen_at", "grade"], rows


def test_a_zone_word_column_is_read_and_its_twin_writes_the_word_of_each_offset(tmp_path: pathlib.Path) -> None:
    """A column of Eastern stamps with EDT and EST: dates and times read at two offsets, its twin in the same words.

    The column is `datetime` under `{EST/EDT}`, its offsets census names
    `-04:00` and `-05:00`, every twin cell is a stamp followed by EDT or
    EST that reads back under the layout, the twin holds both words, and
    validate exits 0. Mutants: the reader's zone arm removed (the column
    free text); the writer's zone arm writing the standard word (no EDT in
    the twin, validate missing the offsets census).
    """
    header, rows = _eastern_rows(1200, 5)
    seen = run(tmp_path / "zone", header, rows, "seen_at")
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    block = seen["block"]
    assert block["role"] == "datetime"
    assert block["format"] == "layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {EST/EDT}"
    assert sorted(block["utc_offsets"]) == ["-04:00", "-05:00"]
    items = parsing.layout_items(block["format"])
    assert items is not None
    pattern = re.compile(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d (EDT|EST)")
    words = {"EDT": 0, "EST": 0}
    for cell in seen["cells"]:
        assert pattern.fullmatch(cell), cell
        read = parsing.layout_reading(cell, items)
        assert read is not None and read[1] == ("-04:00" if cell.endswith("EDT") else "-05:00")
        words[cell[-3:]] += 1
    assert words["EDT"] > 0 and words["EST"] > 0


def test_a_column_mixing_two_families_is_not_read_as_one(tmp_path: pathlib.Path) -> None:
    """Eastern and Central European words in one column: no one layout reads them, so no zone is guessed.

    Mutant: a field reading every word of the list (the column read as
    dates, its European cells written with American words).
    """
    header, rows = _eastern_rows(600, 7)
    for index in range(0, 600, 2):
        rows[index][1] = rows[index][1][:19] + (" CET" if rows[index][1].endswith("EST") else " CEST")
    seen = run(tmp_path / "mixed", header, rows, "seen_at")
    assert seen["exits"][0] == 0
    assert seen["block"]["role"] != "datetime"


# -- (b) clock times written as figures -------------------------------------


def run_answered(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    column: str,
    answers: "dict[str, str]",
) -> "dict[str, object]":
    """Profile (nobody at the keyboard), answer the questions file as given, profile again, generate, validate.

    Each answer is written where the column's entry offers it; what the
    first run asked of `column` and every text each run wrote are kept,
    so a case reads what was published before and after the answer.
    """
    path = _write(folder, header, rows)
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            first = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"])
    questions_path = folder / "t-questions.json"
    unanswered = [(folder / name).read_text(encoding="utf-8")
                  for name in ("t-profile.json", "t-profile.txt", "t-questions.json")]
    questions = json.loads(unanswered[2])
    offered: "list[list[str]]" = []
    entries = list(questions["asked"]) + list((questions.get("checklist") or {}).get("columns") or [])
    for entry in entries:
        if "answers_you_can_give" not in entry:
            continue
        choices = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if entry["column"] == column:
            offered += [choices]
        if entry["column"] in answers and answers[entry["column"]] in choices:
            entry["your_answer"] = answers[entry["column"]]
    questions_path.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            second = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace",
                               "--answers", f"{questions_path}"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir",
                                  f"{folder}", "--seed", "0", "--replace"])
            validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                  f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}", "--replace"])
    answered = [(folder / name).read_text(encoding="utf-8")
                for name in ("t-profile.json", "t-profile.txt", "t-questions.json")]
    document = json.loads(answered[0])
    block = [one for one in document["columns"] if one["name"] == column][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    place = table[0].index(column)
    return {
        "exits": (first, second, generated, validated),
        "offered": offered,
        "block": block,
        "settings": document["settings"],
        "unanswered": unanswered + [screen.getvalue()],
        "answered": answered,
        "cells": [row[place] for row in table[1:]],
        "real": [row[header.index(column)] for row in rows],
    }


def _clock_rows(n: int, seed: int, fraction: int = -1) -> "tuple[list[str], list[list[str]]]":
    """Chart times as a flowsheet writes them: `0742` (or `074512.123456` with a fraction of the figures given), beside a reading."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        second = draw.randrange(86400)
        hours, minutes, seconds = second // 3600, second % 3600 // 60, second % 60
        if fraction < 0:
            cell = f"{hours:02d}{minutes:02d}"
        else:
            cell = f"{hours:02d}{minutes:02d}{seconds:02d}" + (
                "." + "".join(draw.choice("0123456789") for _ in range(fraction)) if fraction else "")
        rows += [[f"R{300000 + index}", cell, f"{draw.randint(60, 140)}"]]
    return ["row_ref", "chart_time", "pulse"], rows


def test_a_military_time_answered_clock_figures_is_read_as_clock_times(tmp_path: pathlib.Path) -> None:
    """`0742` answered `clock-figures`: a column of clock times in `hh-mm figures`, its twin four figures on the grid.

    The padded question offers `clock-figures` beside its three answers;
    answered, the column is `time_of_day`, every twin cell is four
    figures with hours 00 to 23 and minutes 00 to 59, some keep their
    leading nought, and validate exits 0. Mutants: rule 5c removed from
    `taxonomy._decide` (the answer reads nothing, the column held);
    `parsing.written_clock` writing the colon form for the figures face
    (the twin's cells `07:42`).
    """
    header, rows = _clock_rows(1200, 3)
    seen = run_answered(tmp_path / "hhmm", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["exits"] == (0, 0, 0, 0), seen["exits"]
    assert seen["offered"] == [["measurement", "code", "identifier", "clock-figures"]]
    block = seen["block"]
    assert block["role"] == "time_of_day"
    assert block["clock_form"] == "hh-mm figures"
    grid = re.compile(r"([01]\d|2[0-3])[0-5]\d")
    assert all(grid.fullmatch(cell) for cell in seen["cells"]), [c for c in seen["cells"] if not grid.fullmatch(c)][:5]
    assert any(cell.startswith("0") for cell in seen["cells"])
    assert "chart_time" not in seen["settings"]["forced_identifiers"]


def test_a_time_with_a_fraction_answered_clock_figures_keeps_its_width(tmp_path: pathlib.Path) -> None:
    """`074512.123456` answered `clock-figures` on its checklist entry: `hh-mm-ss figures.6`, every twin cell six figures, a point and six.

    No identity question is put to the column, so Q-CLOCK is one more
    answer of the checklist's entry for a measurement, which holds
    nothing; answered, the twin writes each time with its fraction as
    noughts at the published width (lane SS writes fractions), and
    validate exits 0. Mutant: `parsing.clock_figure_form` refusing a
    fraction (no such answer, the column a decimal number).
    """
    header, rows = _clock_rows(1200, 5, fraction=6)
    seen = run_answered(tmp_path / "tm", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["exits"] == (0, 0, 0, 0), seen["exits"]
    assert seen["offered"] == [["measurement", "code", "identifier", "clock-figures"]]
    block = seen["block"]
    assert block["role"] == "time_of_day"
    assert block["clock_form"] == "hh-mm-ss figures.6"
    shape = re.compile(r"([01]\d|2[0-3])[0-5]\d[0-5]\d\.000000")
    assert all(shape.fullmatch(cell) for cell in seen["cells"]), seen["cells"][:5]


def test_unanswered_clock_figures_publish_no_value(tmp_path: pathlib.Path) -> None:
    """HIPAA FIRST: unanswered, a padded column of figures on the grid is held -- no value in any file or the twin.

    The padded question's hold stands until it is answered (rule I):
    `chart_time` is described as record numbers and no real time, nor a
    fragment of one, is printed or written. Mutant: rule 5c taken
    without the answer (the column read as clock times unanswered, its
    rungs real values).
    """
    header, rows = _clock_rows(600, 7)
    seen = run(tmp_path / "open", header, rows, "chart_time")
    assert seen["exits"][0] == 0
    assert seen["block"]["role"] == "identifier"
    assert "chart_time" in seen["settings"]["forced_identifiers"]
    texts = [(tmp_path / "open" / name).read_text(encoding="utf-8")
             for name in ("t-profile.json", "t-profile.txt", "t-questions.json")]
    counted = shapes.count_real(seen["real"], texts, seen["cells"])
    assert counted["description_values"] == 0 and counted["twin_cells"] == 0, counted


# The seven key shapes of rule 5c's measured price (ZR.1): padded keys numbered
# in order stay on the clock's grid, so only the answer may read them.
KEY_SHAPES = {
    "0001_to_0040": [f"{1 + index % 40:04d}" for index in range(300)],
    "0001_to_0059": [f"{1 + index % 59:04d}" for index in range(500)],
    "0100_to_0159": [f"{100 + index % 60:04d}" for index in range(500)],
    "sites_by_patients_6x40": [f"{1 + index // 40 % 6:02d}{1 + index % 40:02d}" for index in range(600)],
    "0001_to_0020": [f"{1 + index % 20:04d}" for index in range(100)],
    "0101_to_0140": [f"{101 + index % 40:04d}" for index in range(300)],
    "sites_by_patients_4x30": [f"{1 + index // 30 % 4:02d}{1 + index % 30:02d}" for index in range(600)],
}


def test_padded_keys_on_the_grid_stay_held_unanswered(tmp_path: pathlib.Path) -> None:
    """The seven key shapes, each on the clock's grid, each held unanswered with 0 values published.

    `clock-figures` is offered (the shape alone cannot tell), and nothing
    is read until somebody answers. Mutant: rule 5c taken without the
    answer.
    """
    for name, keys in KEY_SHAPES.items():
        rows = [[key, f"{index % 7}"] for index, key in enumerate(keys)]
        seen = run(tmp_path / name, ["key", "visit"], rows, "key")
        assert seen["exits"][0] == 0, name
        assert seen["block"]["role"] == "identifier", (name, seen["block"]["role"])
        texts = [(tmp_path / name / one).read_text(encoding="utf-8")
                 for one in ("t-profile.json", "t-profile.txt", "t-questions.json")]
        counted = shapes.count_real(seen["real"], texts, seen["cells"])
        assert counted["description_values"] == 0 and counted["twin_cells"] == 0, (name, counted)


def test_codes_off_the_grid_are_never_offered_clock_figures(tmp_path: pathlib.Path) -> None:
    """Four-figure codes with a value off the clock's grid (`0360`) are never offered `clock-figures`, and read as before.

    Mutant: `parsing._figure_clock_second` reading minutes past 59.
    """
    codes = ("0450", "0120", "0730", "0360", "0250", "0300", "0636", "0981")
    rows = [[codes[index % len(codes)], f"{index % 9}"] for index in range(800)]
    seen = run(tmp_path / "codes", ["revenue_code", "units"], rows, "revenue_code")
    questions = json.loads((tmp_path / "codes" / "t-questions.json").read_text(encoding="utf-8"))
    for entry in list(questions["asked"]) + list((questions.get("checklist") or {}).get("columns") or []):
        offered = [choice["answer"] for choice in entry.get("answers_you_can_give") or []]
        assert "clock-figures" not in offered, entry["column"]
    assert seen["block"]["role"] != "time_of_day"


def test_a_clock_figures_answer_that_does_not_read_holds_the_column(tmp_path: pathlib.Path) -> None:
    """Answered on one export, kept, and handed back with a table one cell of which is off the grid: held, never numbers.

    Contract NF127's treatment (ZR.1 rule 5c): the column is described as
    record numbers, its name among the forced identifiers, and no value
    is published. Mutant: `profile._counted_dates_declined` without its
    clock arm (the column read as a decimal number, its statistics
    published).
    """
    header, rows = _clock_rows(800, 11, fraction=6)
    first = run_answered(tmp_path / "first", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert first["block"]["role"] == "time_of_day"
    rows[17][1] = "250000.000599"
    folder = tmp_path / "second"
    path = _write(folder, header, rows)
    kept = tmp_path / "first" / "t-questions.json"
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace",
                                 "--answers", f"{kept}"])
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir",
                                  f"{folder}", "--seed", "0", "--replace"])
    assert (profiled, generated) == (0, 0)
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "chart_time"][0]
    assert block["role"] == "identifier"
    assert "chart_time" in document["settings"]["forced_identifiers"]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    cells = [row[1] for row in table[1:]]
    texts = [(folder / name).read_text(encoding="utf-8") for name in ("t-profile.json", "t-profile.txt")]
    counted = shapes.count_real([row[1] for row in rows], texts, cells)
    assert counted["description_values"] == 0 and counted["twin_cells"] == 0, counted


def test_every_shape_of_figures_reads_on_the_grid_and_nowhere_else() -> None:
    """THE CLASS, CLOSED BY A SWEEP: every four- and six-figure string, and 6,000 with fractions, read exactly on the grid.

    Each of the 10,000 four-figure strings reads in `hh-mm figures` where
    its hours are 00 to 23 and its minutes 00 to 59 (1,440 of them) and
    nowhere else; each of the 1,000,000 six-figure strings likewise in
    `hh-mm-ss figures` (86,400); a fraction of one to six figures reads
    in its own form and in no other width; and no shape of figures is
    read by inference (`clock_form` answers none). Mutant: the grid test
    of `_figure_clock_second` dropped (minutes past 59 read).
    """
    four = [f"{value:04d}" for value in range(10000)]
    read = [text for text in four if parsing.clock_ordinal(text, "hh-mm figures") is not None]
    assert len(read) == 1440
    assert all(int(text[:2]) < 24 and int(text[2:]) < 60 for text in read)
    six = 0
    for value in range(1000000):
        text = f"{value:06d}"
        if parsing.clock_ordinal(text, "hh-mm-ss figures") is not None:
            six += 1
    assert six == 86400
    draw = random.Random(20261109)
    for _case in range(6000):
        figures = draw.randint(1, 6)
        second = draw.randrange(86400)
        base = f"{second // 3600:02d}{second % 3600 // 60:02d}{second % 60:02d}"
        text = base + "." + "".join(draw.choice("0123456789") for _ in range(figures))
        form = f"hh-mm-ss figures.{figures}"
        assert parsing.clock_figure_form(text) == form
        assert parsing.clock_ordinal(text, form) == second
        assert parsing.clock_spelling(second, form) == base + "." + "0" * figures
        assert parsing.clock_form(text) is None
        other = f"hh-mm-ss figures.{figures % 6 + 1}"
        assert parsing.clock_ordinal(text, other) is None


def test_the_keyboard_has_a_key_for_clock_figures() -> None:
    """Q-CLOCK can be answered at the keyboard as in the file (a missing key stopped T1's first run)."""
    from synthtwin import asking

    key = cli._KEY_OF[asking.ANSWER_CLOCK_FIGURES]
    assert cli._ANSWER_KEYS[key] == asking.ANSWER_CLOCK_FIGURES


def _oracle() -> "dict[str, object]":
    """The generation oracle's own namespace, as the vectors' test loaded it (it imports no synthtwin).

    Read off `tests/test_generation_reference.py`'s module, as lane L3's
    test reads it, so no new route runs a file of source
    (tests/test_version_reach.py names each one).
    """
    from tests import test_generation_reference as reference

    return vars(reference.gen)


def test_the_oracle_writes_and_reads_every_form_of_figures_as_the_product_does() -> None:
    """A-P4-59: method G7A.1's eight forms of figures, written out a second time in the oracle, agree at every place.

    Every minute of `hh-mm figures` and every seventh second of the seven
    forms at the second (every residue of the minute): the product's
    spelling is the oracle's, each reads back to its place in both, and
    the oracle refuses a minute past 59 and the colon form. Mutant: the
    product's fraction written with one nought too few.
    """
    oracle = _oracle()
    spelling_of = oracle["clock_spelling_of"]
    ordinal_of = oracle["clock_ordinal_of"]
    capacity = oracle["clock_capacity"]
    for form in parsing.CLOCK_FIGURE_FORMS:
        assert capacity(form) == parsing.CLOCK_CAPACITY[form], form  # type: ignore[operator]
        stride = 1 if parsing.clock_step(form) == 60 else 7
        for ordinal in range(0, parsing.CLOCK_CAPACITY[form], stride):
            text = parsing.clock_spelling(ordinal, form)
            assert spelling_of(ordinal, form) == text, (form, ordinal)  # type: ignore[operator]
            assert ordinal_of(text, form) == ordinal  # type: ignore[operator]
    for text, form in (("0760", "hh-mm figures"), ("07:42", "hh-mm figures"), ("074512.12", "hh-mm-ss figures.3")):
        try:
            ordinal_of(text, form)  # type: ignore[operator]
        except AssertionError:
            continue
        raise AssertionError(f"the oracle read {text!r} in {form}")


def test_a_fraction_clock_counts_its_values_by_their_whole_seconds(tmp_path: pathlib.Path) -> None:
    """2,000 times with fractions inside ten minutes: every spelling different, 600 whole seconds at most -- and the twin is made.

    The fraction is read and not kept, so the column's different values
    are its different whole seconds (`taxonomy._figures_distinct`):
    counted by spelling, the census of a column whose cells are all
    different asked each ten-minute group for as many steps as cells,
    and the description's own rule (CC5) refused it -- at 200,000 rows
    on the zoo's TM shape every group did (1,365 cells over 594 steps),
    and generate and validate stopped. Mutant: `_figures_distinct`
    returning the spellings' count.

    ...AND NO REMARK THAT EVERY VALUE DIFFERS (the lane's skeptic 1, item
    4 (c)): every spelling differs, but the whole seconds repeat, so the
    block carries neither all-different remark. Mutants: the all-different
    remark judged by spelling (`taxonomy._clock_verdict`, V11), and the
    fraction clock's `apart` judged by spelling (V10), which reaches the
    remark the same way. Where `apart` reaches the tails it changes no byte:
    `ordered_tails` hands it to `_tail_pinned` alone, asked only of a tail
    `parsing.tail_may_list` admits, whose every listed distance some two
    cells hold -- so its distances repeat and the flag reads False either
    way.
    """
    draw = random.Random(17)
    rows: "list[list[str]]" = []
    for index in range(2000):
        second = 8 * 3600 + draw.randrange(600)
        cell = f"{second // 3600:02d}{second % 3600 // 60:02d}{second % 60:02d}.{index:06d}"
        rows += [[f"R{100000 + index}", cell, f"{draw.randint(60, 140)}"]]
    seen = run_answered(tmp_path / "frac", ["row_ref", "chart_time", "pulse"], rows, "chart_time",
                        {"chart_time": "clock-figures"})
    assert seen["exits"] == (0, 0, 0, 0), seen["exits"]
    block = seen["block"]
    assert block["clock_form"] == "hh-mm-ss figures.6"
    assert block["n_distinct"] <= 600 and block["n_distinct"] == block["n_distinct_folded"]
    assert len(set(seen["cells"])) <= 600
    remarks = " ".join(f"{remark}" for remark in block["remarks"])
    assert "every value in this column is different" not in remarks, remarks


# -- repair 1: the lane's skeptic 1 and its statistics check ----------------


def test_clock_stand_ins_are_never_written_as_figures() -> None:
    """THE STATISTICS CHECK, ITEM 1: 25,000 stand-ins of a column written to the second, none in a form of figures.

    G7A.5 writes a column's unparsed cells as times at the other precision,
    the forty forms' 22,200 spellings at the minute first and then each
    again below the floor; a form of figures among them (`0742`) is a word
    to every reader, and its 1,440 spellings took the words of 2,500,000
    present cells past route 1's allowance
    (tests/test_stage3b_clock_minutes.py). Every stand-in here is read by
    `parsing.clock_form`, and none is four figures. Mutant: the forms of
    figures back among `generation._clock_times_unread`'s forms.
    """
    from synthtwin import generation

    cells = generation._clock_times_unread("hh-mm-ss", 25_000, {}, (), 11)
    assert len(cells) == 25_000
    assert not [cell for cell in cells if re.fullmatch(r"\d{4}", cell)]
    assert all(parsing.clock_form(cell) is not None for cell in cells)


def test_the_oracle_writes_and_reads_every_zone_word_as_the_product_does() -> None:
    """A-P4-59 (the lane's skeptic 1, item 2): method G7.5's nine zone fields, written out a second time in the oracle, agree with the product.

    The generated cases' 17 words by their 6 stamp forms, 20 rounds: the
    oracle reads each cell under the layout the product reads it under at
    the offset its word names (`layout_zone_offset`, as
    `parsing.layout_reading`), and writes it, at every offset of its
    family, as `parsing.layout_cell` does (`layout_written`); and G7.9b's
    offer spells each whole hour east as the family's word where it names
    one and as nothing where it names none, as `layout_offset_added`
    writes or refuses it. Mutant: the product's writer writing the
    standard word whatever the offset.
    """
    oracle = _oracle()
    written = oracle["layout_written"]
    named = oracle["layout_zone_offset"]
    offer = oracle["offsets_on_offer"]
    draw = random.Random(20261110)
    start = datetime.datetime(2001, 1, 1)
    checked = 0
    for _round in range(20):
        for family, words in FAMILIES.items():
            for word, offset in words:
                for form in STAMP_FORMS:
                    moment = start + datetime.timedelta(seconds=draw.randrange(25 * 365 * 86400))
                    cell = f"{moment.strftime(form)} {word}"
                    name = _stamp_layout(cell, family)
                    assert name is not None, cell
                    items = parsing.layout_items(name)
                    assert items is not None
                    read = parsing.layout_reading(cell, items)
                    assert read is not None and read[1] == offset
                    assert named(name, cell) == offset, (name, cell)  # type: ignore[operator]
                    # The instant as the layout reads it (`{MM}.{DD}.{YYYY}` reads
                    # `04.08.2020` month first), written back from there.
                    canonical = f"{read[0]}"
                    second = int(canonical[11:13]) * 3600 + int(canonical[14:16]) * 60 + int(canonical[17:19])
                    for _other, other_offset in words:
                        product = parsing.layout_cell(items, read[0], other_offset, read[2], 0)
                        made = written(  # type: ignore[operator]
                            name, int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10]), second,
                            other_offset, "padded", 0,
                        )
                        assert made == product, (name, other_offset, made, product)
                        assert named(name, made) == other_offset  # type: ignore[operator]
                    checked += 1
    assert checked == 20 * 17 * len(STAMP_FORMS)
    for family in FAMILIES:
        name = f"layout {{YYYY}}{{MM}}{{DD}}{{HH}}{{MI}}{{SS}} {{{family}?}}"
        spelled = offer(family, {})  # type: ignore[operator]
        assert len(spelled) == 15
        for hours, spelling in enumerate(spelled):
            added = parsing.layout_offset_added("20240101091530", name, f"+{hours:02d}:00")
            assert (added[15:] if added is not None else None) == spelling, (family, hours, added, spelling)


def test_an_added_zone_word_is_the_word_of_its_own_offset() -> None:
    """G7.9b's word (the lane's skeptic 1, item 4 (d)): on a zone column whose cells may omit the word, each word added is its own offset's.

    Every family, under a layout of figures (`{CET/CEST?}` after fourteen
    figures, the shape G7.9b writes owed offsets on) and one with marks, at every
    whole hour G7.9b offers (`+00:00` to `+14:00`) and at the family's own
    offsets: `layout_offset_added` writes the family's word for the
    offset, which reads back at it, and refuses an offset the family names
    no word for. Mutant: its zone arm writing the standard word (V25).
    """
    checked = 0
    for family, words in FAMILIES.items():
        own = dict((offset, word) for word, offset in words)
        offsets = list(dict.fromkeys([f"+{hours:02d}:00" for hours in range(15)] + [offset for _word, offset in words]))
        for name, cell in (
            (f"layout {{YYYY}}{{MM}}{{DD}}{{HH}}{{MI}}{{SS}} {{{family}?}}", "20240101091530"),
            (f"layout {{YYYY}}-{{MM}}-{{DD}} {{HH}}:{{MI}}:{{SS}} {{{family}?}}", "2024-01-01 09:15:30"),
        ):
            assert parsing.is_layout_format(name), name
            items = parsing.layout_items(name)
            assert items is not None
            for offset in offsets:
                added = parsing.layout_offset_added(cell, name, offset)
                if offset not in own:
                    assert added is None, (name, offset, added)
                    continue
                assert added == f"{cell} {own[offset]}", (name, offset, added)
                read = parsing.layout_reading(added, items)
                assert read is not None and read[1] == offset
                checked += 1
    assert checked == 2 * 17


def test_a_zone_layout_shows_its_standard_word() -> None:
    """A zone layout's sample cell wears its family's standard word, and reads back at that word's offset.

    `parsing.layout_example` writes the sample a person is shown, and
    `is_layout_format` writes and reads it back. Mutant: the sample's
    offset `+01:00` for a zone field too (V17): Western Europe's sample
    then wears `WEST`, its summer word.
    """
    for family, words in FAMILIES.items():
        name = f"layout {{YYYY}}-{{MM}}-{{DD}} {{HH}}:{{MI}}:{{SS}} {{{family}}}"
        example = parsing.layout_example(name)
        assert example.endswith(f" {words[0][0]}"), (family, example)
        items = parsing.layout_items(name)
        assert items is not None
        read = parsing.layout_reading(example, items)
        assert read is not None and read[1] == words[0][1], (family, example, read)


def _answered_clock_figures(folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    """1,200 military times answered `clock-figures` in the questions file; the table and the file the answered run wrote."""
    header, rows = _clock_rows(1200, 3)
    seen = run_answered(folder, header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["block"]["role"] == "time_of_day"
    kept = folder / "kept-questions.json"
    kept.write_bytes((folder / "t-questions.json").read_bytes())
    return folder / "t.csv", kept


def _profiled_again(
    folder: pathlib.Path, path: pathlib.Path, kept: pathlib.Path, *typed: str
) -> "tuple[int, dict[str, object], list[tuple[str, str]]]":
    """Profile `path` again with the kept file and what is typed; its exit, chart_time's block and the kept answers it writes."""
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace",
                             "--answers", f"{kept}", *typed])
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "chart_time"][0]
    questions = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    answers = [
        (f"{entry['column']}", f"{entry.get('your_answer') or entry.get('read_as_now')}")
        for entry in questions.get("answered_before") or []
        if isinstance(entry, dict) and entry.get("column") == "chart_time"
    ]
    return code, block, answers


def test_a_kept_clock_figures_answer_gives_way_to_a_later_code_or_identifier(tmp_path: pathlib.Path) -> None:
    """The lane's skeptic 1, item 4 (a): a kept `clock-figures` and a later answer of what the column holds never stand together.

    Answered `clock-figures` and kept, then `--code chart_time` (and,
    apart, `--identifier chart_time`) typed on the next run, which is the
    later statement: the file that run writes keeps only the later answer,
    and the column is read as it says. Mutant: the pair taken off
    `asking._CANNOT_STAND_TOGETHER` (V6): both kept, and the column said
    to be codes held as record numbers.
    """
    path, kept = _answered_clock_figures(tmp_path / "first")
    for option, role, answer in (
        ("--code", "long_tail_labels", "code"),
        ("--identifier", "identifier", "identifier"),
    ):
        folder = tmp_path / option.strip("-")
        folder.mkdir()
        code, block, answers = _profiled_again(folder, path, kept, option, "chart_time")
        assert code == 0
        assert answers == [("chart_time", answer)], (option, answers)
        assert block["role"] == role, (option, block["role"])


def test_a_kept_clock_figures_answer_handed_back_stays_kept(tmp_path: pathlib.Path) -> None:
    """A kept `clock-figures` handed back twice, unchanged: still kept, still reading the column as clock times.

    The answer belongs to a family of its own (`asking._FAMILY_FIGURES`),
    so the file each run writes carries it again under `answered_before`.
    Mutant: `asking.answered_before` without its clock-figures entry (the
    answer read once and not carried, the column held on the third run).
    The family's arm of `asking._family_of` (the skeptic's V5) changes no
    byte on any path measured -- this one, a kept answer changed to `keep`
    and asked again, a kept answer that no longer reads, and a later code
    or identifier typed -- because the kept entry is written under its
    family by name, a code, identifier or measurement replaces it through
    `_CANNOT_STAND_TOGETHER`, and a kept `keep` of it is not carried; the
    lane's repair report names it equivalent with those measurements.
    """
    path, kept = _answered_clock_figures(tmp_path / "first")
    folder = tmp_path / "again"
    folder.mkdir()
    for _round in range(2):
        code, block, answers = _profiled_again(folder, path, kept)
        assert code == 0
        assert answers == [("chart_time", "clock-figures")], answers
        assert block["role"] == "time_of_day"
        kept = folder / f"kept-{_round}.json"
        kept.write_bytes((folder / "t-questions.json").read_bytes())


def test_a_heap_of_military_times_is_published_in_its_figures(tmp_path: pathlib.Path) -> None:
    """The lane's skeptic 1, item 4 (b): 600 military times, a third of them `0800`, answered `clock-figures`: the heap is named in its own figures.

    The description's own guard reads a clock value in any form, the forms
    of figures among them, so the heap at `0800` is published and the
    profile stands. Mutant: the guard's figures arm removed (V8).
    """
    header, rows = _clock_rows(600, 13)
    for index in range(0, 600, 3):
        rows[index][1] = "0800"
    seen = run_answered(tmp_path / "heap", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["exits"][1] == 0, seen["exits"]
    block = seen["block"]
    assert block["clock_form"] == "hh-mm figures"
    assert "0800" in json.dumps(block.get("clock_heaps")), block.get("clock_heaps")


def test_the_repeat_block_hands_back_the_questions_file_for_clock_figures(tmp_path: pathlib.Path) -> None:
    """The lane's skeptic 1, item 3: where a `clock-figures` answer stands, the lines that repeat the run name the questions file.

    No option declares clock times written as figures (`--clock-figures`
    is not on the command line), so the block says `--answers` and the
    file this run writes, which keeps the answer: answered at the keyboard
    (key 19) and answered in the questions file alike, and the file named
    there repeats the reading with nobody at the keyboard. Mutants: the
    block's condition without the clock figures; the questions-file
    answer not counted as answers handed back (V26).
    """
    header, rows = _clock_rows(1200, 3)
    folder = tmp_path / "keys"
    path = _write(folder, header, rows)
    screen: "list[tuple[str, str]]" = []
    cli.run(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"], screen=screen,
            ask=[""] * 40, small_tables_refused=False)
    said = "".join(text for _stream, text in screen)
    order = re.findall(r"Column \d+ of \d+: '([^']+)'", said)
    assert "chart_time" in order, said[-2000:]
    keys: "list[str | None]" = ["19" if name == "chart_time" else "" for name in order] + [""] * 20
    screen = []
    cli.run(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"], screen=screen, ask=keys,
            small_tables_refused=False)
    said = "".join(text for _stream, text in screen)
    at = said.find("TO REPEAT THIS RUN")
    assert at >= 0, said[-2000:]
    # ...the file as it is typed: quoted for the shell where its path holds
    # a space, as the suite's own temporary folders do.
    assert f"--answers {cli._typed_path(folder / 't-questions.json')}" in said[at:at + 800], said[at:at + 800]
    again = tmp_path / "again"
    again.mkdir()
    code, block, _answers = _profiled_again(again, path, folder / "t-questions.json")
    assert code == 0 and block["role"] == "time_of_day"
    seen = run_answered(tmp_path / "file", header, rows, "chart_time", {"chart_time": "clock-figures"})
    second = seen["unanswered"][3]
    at = second.rfind("TO REPEAT THIS RUN")
    assert at >= 0, second[-2000:]
    assert "--answers" in second[at:at + 800], second[at:at + 800]


def test_held_birth_stamps_are_drawn_from_the_made_up_date_room(tmp_path: pathlib.Path) -> None:
    """THE LANE'S SKEPTIC 1, ITEM 1 (HIPAA): a held column of birth stamps draws its made-up stamps from the room.

    One birth stamp a person, 100 people born 1928 to 2005, 12 rows each
    (a test size the command refuses; the 20,000-row leg with 1,000
    patients is K-HZ-26's), the person column answered `identifier`, in an
    Eastern zone word, with no offset, with `-05:00` or `-04:00` and with
    ` UTC`: the block publishes the year 2028 (`made_up_years`), every
    twin cell is a stamp of 2028 in the column's own form, and none falls on
    a real calendar date -- where the G1 floor's fixed span of 2000 to 2029
    wrote, at 20,000 rows, 80 cells on 3 real birth dates in each form.
    Mutants: `taxonomy.with_made_up_years` without its stamp branch; and
    generation's `_room_spans` without its stamp arm (the twin's years
    2000 to 2029 again).
    """
    draw = random.Random(206)
    births = []
    for _person in range(100):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))]
    order = [index % 100 for index in range(1200)]
    draw.shuffle(order)
    for spelling, ending in (("zone", " {word}"), ("plain", ""), ("offset", "{offset}"), ("utc", " UTC")):
        real = []
        for person in order:
            summer = 4 <= births[person].month <= 10
            real += [f"{births[person]:%Y-%m-%d %H:%M:%S}" + ending.format(
                word="EDT" if summer else "EST", offset="-04:00" if summer else "-05:00")]
        rows = [[f"Q{700000 + person}", real[row], f"{row % 7}"] for row, person in enumerate(order)]
        seen = run_answered(tmp_path / spelling, ["person_ref", "birth_ts", "grade"], rows, "birth_ts",
                            {"person_ref": "identifier"})
        assert seen["exits"][1:3] == (0, 0), (spelling, seen["exits"])
        block = seen["block"]
        assert block["role"] == "identifier" and block["time_grain"]["kind"] == "stamp", (spelling, block["role"])
        assert block["made_up_years"] == [[2028, 2028]], (spelling, block.get("made_up_years"))
        days = {cell[:10] for cell in real}
        twin = seen["cells"]
        assert all(cell[:4] == "2028" and cell[4] == "-" for cell in twin), (spelling, sorted(set(cell[:4] for cell in twin))[:5])
        assert not [cell for cell in twin if cell[:10] in days], spelling
        assert {len(cell) for cell in twin} <= {len(cell) for cell in real}, spelling


def test_a_made_up_stamp_stands_only_where_a_reading_names_a_year_of_the_room() -> None:
    """The check each made-up stamp passes before it stands (`generation._stamp_in_the_room`; plan P4-D473).

    One of its readings (`taxonomy.cell_date_years`) names a published year
    of its kind: a stamp of 2028 in an ISO, a zone-word, a compact, a
    month-word or a two-figure form stands beside the block 2028 (or `28`);
    one of 2027 -- the offset or the zone carrying a draw across the
    year's end -- or of a real year does not, and the floor draws again.
    Mutant: the check answering yes whatever the readings.
    """
    from synthtwin import generation

    four: "dict[int, bool]" = {2028: True}
    two: "dict[int, bool]" = {28: True}
    for cell in ("2028-03-14 09:15:00", "2028-03-14 09:15:00 EST", "20280314091500", "14-MAR-2028 09:15:00",
                 "2028-03-14T09:15:00Z"):
        assert generation._stamp_in_the_room(cell, (four, {})), cell
    for cell in ("2027-12-31 23:00:00 EST", "2005-03-14 09:15:00", "1952-10-01T14:28:00Z"):
        assert not generation._stamp_in_the_room(cell, (four, {})), cell
    assert generation._stamp_in_the_room("03/14/28 09:15", ({}, two))
    assert not generation._stamp_in_the_room("03/14/27 09:15", ({}, two))


# Seven more forms of a birth stamp: what each is written as, and how a cell is read back to its day.
HELD_STAMP_FORMS = (
    ("iso_t_z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%SZ"),
    ("us_12h", "%m/%d/%Y %I:%M %p", "%m/%d/%Y %I:%M %p"),
    ("month_word", "%d-%b-%Y %H:%M:%S", "%d-%b-%Y %H:%M:%S"),
    ("compact", "%Y%m%d%H%M%S", "%Y%m%d%H%M%S"),
    ("fraction", "%Y-%m-%d %H:%M:%S.123", "%Y-%m-%d %H:%M:%S.%f"),
    ("two_figure", "%m/%d/%y %H:%M", "%m/%d/%y %H:%M"),
    ("day_first", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M"),
)


def test_held_birth_stamps_in_seven_more_forms_name_no_real_day(tmp_path: pathlib.Path) -> None:
    """THE CLASS, A TABLE-LEVEL SAMPLE (LANE I4r RULINGS 1 (4)): seven more stamp forms, each held, none naming a real day.

    The same 100 people born 1928 to 2005, 12 rows each, the person
    answered `identifier`, written with a `T` and a `Z`, on a 12-hour clock
    with its marker, with a month's word, as fourteen figures, with a
    fraction, with a two-figure year, and day first. Where the block
    publishes the year 2028 every twin cell reads back in the column's own
    form to a day of 2028; where a real cell names a year of the block --
    a month's word or a two-figure year beside births of 1928 to 1999,
    read with either width of year -- it publishes `[]` and the twin
    writes made-up values that are no date (NF137). Either way no twin
    cell reads back to a real cell's day. Mutant: generation's
    `_room_spans` without its stamp arm.
    """
    draw = random.Random(206)
    births = []
    for _person in range(100):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))]
    order = [index % 100 for index in range(1200)]
    draw.shuffle(order)
    real_days = {births[person].date() for person in order}

    def day_of(cell: str, form: str) -> "datetime.date | None":
        try:
            return datetime.datetime.strptime(cell.title() if "%b" in form else cell, form).date()
        except ValueError:
            return None

    rooms = {}
    for name, written, read in HELD_STAMP_FORMS:
        real = [births[person].strftime(written).upper() for person in order]
        rows = [[f"Q{700000 + person}", real[row], f"{row % 7}"] for row, person in enumerate(order)]
        seen = run_answered(tmp_path / name, ["person_ref", "birth_ts", "grade"], rows, "birth_ts",
                            {"person_ref": "identifier"})
        assert seen["exits"][1:3] == (0, 0), (name, seen["exits"])
        block = seen["block"]
        assert block["time_grain"]["kind"] == "stamp", name
        rooms[name] = block["made_up_years"]
        days = [day_of(cell, read) for cell in seen["cells"]]
        assert not [day for day in days if day in real_days], name
        if block["made_up_years"]:
            assert block["made_up_years"] == [[2028, 2028]], (name, block["made_up_years"])
            assert all(day is not None and day.year == 2028 for day in days), (name, seen["cells"][:3])
        else:
            assert all(day is None for day in days), (name, seen["cells"][:3])
    assert [name for name, room in rooms.items() if room] == ["iso_t_z", "us_12h", "compact", "fraction", "day_first"], rooms


# Eleven stamp readings a held column may carry, each with a form it writes (and its zone or offset).
STAMP_READINGS = (
    ("iso-datetime", "%Y-%m-%dT%H:%M:%SZ", ""),
    ("month-first-datetime", "%m/%d/%Y %I:%M %p", ""),
    ("layout {DD}-{MON}-{YYYY} {HH}:{MI}:{SS}", "%d-%b-%Y %H:%M:%S", ""),
    ("layout {YYYY}{MM}{DD}{HH}{MI}{SS}", "%Y%m%d%H%M%S", ""),
    ("iso-datetime", "%Y-%m-%d %H:%M:%S.123", ""),
    ("layout {MM}/{DD}/{YY} {HH}:{MI}", "%m/%d/%y %H:%M", ""),
    ("day-first-datetime", "%d/%m/%Y %H:%M", ""),
    ("layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {EST/EDT}", "%Y-%m-%d %H:%M:%S", " EST"),
    ("iso-datetime", "%Y-%m-%d %H:%M:%S", ""),
    ("iso-datetime", "%Y-%m-%d %H:%M:%S", "-05:00"),
    ("layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {UTC}", "%Y-%m-%d %H:%M:%S", " UTC"),
)


def test_the_g1_floor_draws_every_stamp_reading_inside_the_room() -> None:
    """THE CLASS, A GENERATED UNIT SAMPLE (LANE I4r RULINGS 1 (4)): 2,200 made-up stamps, 200 for each of eleven readings.

    Each cell a stamp of 1900 to 2024 in its reading's form; the G1 floor
    (`grains.filled`, its member's own form allowed, as the room's
    fallback writes it) draws it inside the room's span of 2028, and the
    check each one passes (`generation._stamp_in_the_room`) finds a
    reading naming 2028 -- or `28`, where the reading writes two figures.
    Mutant: the check reading the four-figure years alone (every
    two-figure stamp refused).
    """
    from synthtwin import date_counts, generation, grains

    draw = random.Random(20261110)
    span = (parsing.days_from_civil(2028, 1, 1) * date_counts.DAY, parsing.days_from_civil(2029, 1, 1) * date_counts.DAY)
    drawn = 0
    for member, form, tail in STAMP_READINGS:
        reading = grains.Reading(grains.STAMP, member)
        for _case in range(200):
            moment = datetime.datetime(1900, 1, 1) + datetime.timedelta(seconds=draw.randrange(125 * 365 * 86400))
            cell = (moment.strftime(form).upper() if "%b" in form else moment.strftime(form)) + tail
            made = grains.filled(cell, reading, draw.getrandbits(64), span, True, {}, False, True)
            assert made is not None, (member, cell)
            assert generation._stamp_in_the_room(made, ({2028: True}, {28: True})), (member, cell, made)
            drawn += 1
    assert drawn == 2200


# -- repair 2: Codex's review of lane TR (LANE TR RULINGS 5 and 6) -----------


def _keyboard_order(path: pathlib.Path, folder: pathlib.Path) -> "list[str]":
    """The columns the keyboard puts a question to, in order, from one run left unanswered."""
    screen: "list[tuple[str, str]]" = []
    cli.run(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"], screen=screen,
            ask=[""] * 40, small_tables_refused=False)
    said = "".join(text for _stream, text in screen)
    return re.findall(r"Column \d+ of \d+: '([^']+)'", said)


def test_a_clock_figures_answer_typed_at_the_keyboard_reads_on_its_own_run(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 1: key 19, or its letter `f`, typed at the keyboard reads the column on THAT run.

    1,200 six-figure clock times, seconds drawn over the whole day (Codex's
    table, at a test size): the run answered at the keyboard alone
    describes chart_time as `time_of_day` in `hh-mm-ss figures`, and the
    twin generated from that run's own description at seed 0 writes every
    cell as six figures on the clock's grid. Mutant: the answer left out of
    the rebuild condition (the run's description kept the column as it read
    before the answer while its questions file recorded the answer -- 9,902
    of 20,000 twin cells no clock time, by the verify's count).
    """
    header, rows = _clock_rows(1200, 31, fraction=0)
    # ...the clock beside a reading alone: a record key whose question is left
    # open holds that key, and the description is then built again with every
    # answer, which hid the defect.
    header, rows = header[1:], [row[1:] for row in rows]
    grid = re.compile(r"([01]\d|2[0-3])[0-5]\d[0-5]\d")
    for key in ("19", "f"):
        folder = tmp_path / f"key-{key}"
        path = _write(folder, header, rows)
        order = _keyboard_order(path, folder)
        assert "chart_time" in order, order
        keys: "list[str | None]" = [key if name == "chart_time" else "" for name in order] + [""] * 20
        cli.run(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"], screen=[], ask=keys,
                small_tables_refused=False)
        questions = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
        kept = [entry.get("your_answer") or entry.get("read_as_now") for entry in questions.get("answered_before") or []
                if isinstance(entry, dict) and entry.get("column") == "chart_time"]
        assert kept == ["clock-figures"], (key, kept)
        document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
        block = [one for one in document["columns"] if one["name"] == "chart_time"][0]
        assert block["role"] == "time_of_day" and block["clock_form"] == "hh-mm-ss figures", (key, block["role"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
        assert generated == 0, key
        with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
            cells = [row[0] for row in list(csv.reader(handle))[1:]]
        assert all(grid.fullmatch(cell) for cell in cells), (key, [c for c in cells if not grid.fullmatch(c)][:5])


def _fraction_rows(n: int, missing: int, base: str = "080000") -> "tuple[list[str], list[list[str]]]":
    """Codex's table of item 2 at `n` rows: `missing` rows of `<base>.000000`, the rest `<base>.000001` upward."""
    rows: "list[list[str]]" = []
    for index in range(n):
        cell = f"{base}.000000" if index < missing else f"{base}.{index - missing + 1:06d}"
        rows += [[f"R{300000 + index}", cell, f"{60 + index % 80}"]]
    return ["row_ref", "chart_time", "pulse"], rows


def test_a_clock_figures_answer_that_would_write_a_missing_spelling_is_not_taken(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 2 (FAIL CLOSED): `080000.000000` declared missing beside fractions of that second.

    Answered `clock-figures`, every present cell is the second 08:00:00,
    which the form writes `080000.000000` -- the declared spelling -- so the
    twin wrote it on every cell and every observed value came back missing
    (at 20,000 rows: 19,989 present described, 0 recounted, validate exit 3).
    A form of figures has no other spelling of that second, so the answer
    is not taken: the column is described as it was before the answer --
    byte for byte the description of a run with nothing answered -- never
    held, the run says why in a message that names no value, and the twin's
    present cells read back present. Mutant: the check of the spellings
    removed from `taxonomy._figure_clock_reading`.
    """
    header, rows = _fraction_rows(1200, 11)
    folder = tmp_path / "collide"
    path = _write(folder, header, rows)
    declared = ["--missing-value", "080000.000000"]
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            first = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace", *declared])
    before = (folder / "t-profile.json").read_text(encoding="utf-8")
    questions = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    offered = False
    for entry in list(questions["asked"]) + list((questions.get("checklist") or {}).get("columns") or []):
        choices = [choice["answer"] for choice in entry.get("answers_you_can_give") or []]
        if entry["column"] == "chart_time" and "clock-figures" in choices:
            entry["your_answer"] = "clock-figures"
            offered = True
    assert offered
    (folder / "t-questions.json").write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            second = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace", *declared,
                               "--answers", f"{folder / 't-questions.json'}"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                                  "--seed", "0", "--replace"])
            validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                                  "--out-dir", f"{folder}", "--replace"])
    assert (first, second, generated, validated) == (0, 0, 0, 0)
    said = screen.getvalue()
    assert "was answered as clock times written as figures" in said and "The answer was" in said, said[-3000:]
    assert "080000" not in said[said.find("was answered as clock times written"):][:900]
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "chart_time"][0]
    assert block["role"] != "time_of_day" and block["role"] != "identifier", block["role"]
    assert "chart_time" not in document["settings"]["forced_identifiers"]
    assert [one for one in json.loads(before)["columns"] if one["name"] == "chart_time"][0] == block
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        cells = [row[1] for row in list(csv.reader(handle))[1:]]
    assert sum(1 for cell in cells if cell == "080000.000000") <= 11


def test_the_spellings_of_every_figure_form_against_missing_spellings_of_every_width() -> None:
    """THE COLLISION CLASS, A GENERATED UNIT SWEEP (LANE TR RULINGS 5 (6)): each figure form against declared spellings of every width.

    For each of the eight forms of figures and 300 drawn seconds, the
    form's own spelling of the second is set against the same second
    written in every width of figures (four, six, six with one to six
    figures after the point) and as a number with no leading nought, each
    declared missing in turn: it collides exactly where the declared value
    names it -- by its spelling or by its exact number (`80000` and
    `080000.000000` are one number) -- and nowhere else. And the whole
    reading: present cells of a fraction on the declared spelling's second
    are never read by rule 5c, cells on another second are. Mutant: the
    number half of `taxonomy.figure_spellings_absent` dropped
    (`--missing-value 80000` beside `080000.000001` read, the twin
    writing the missing number).
    """
    from synthtwin import taxonomy

    def spelled(second: int, form: str) -> str:
        whole = form == "hh-mm figures"
        return parsing.written_clock(second - second % 60 if whole else second, not whole,
                                     "hh" + form[form.find(" "):])

    draw = random.Random(20261110)
    widths = ["hh-mm figures", "hh-mm-ss figures"] + [f"hh-mm-ss figures.{n}" for n in range(1, 7)]
    checked = 0
    for form in widths:
        for _case in range(300):
            second = draw.randrange(86400)
            spelling = spelled(second, form)
            assert parsing.clock_ordinal(spelling, form) is not None, (form, spelling)
            for other in widths:
                written = spelled(second, other)
                for declared in (written, written.lstrip("0") or "0"):
                    settings = taxonomy.Settings(declared_missing_values=(declared,))
                    expected = float(declared) == float(spelling)
                    assert taxonomy.figure_spellings_absent([spelling], settings) == expected, (form, spelling, declared)
                    checked += 1
            missing = taxonomy.Settings(declared_missing_values=(spelling,))
            elsewhere = spelled((second + 3600) % 86400, form)
            if "." in spelling:
                same = spelling[:7] + "1" * (len(spelling) - 7)
                assert taxonomy.clock_figures_reading([same, same, spelling], missing) == taxonomy.FIGURES_ABSENT
                elsewhere = elsewhere[:7] + "1" * (len(elsewhere) - 7)
            assert taxonomy.clock_figures_reading([elsewhere, elsewhere, spelling], missing) == taxonomy.FIGURES_READ
    assert checked == 8 * 300 * 8 * 2


def test_valid_one_and_two_value_clock_figures_keep_the_earlier_rules(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 3: a kept `clock-figures` on `0800` and `1600` alternating, and on `0800` alone.

    Every cell satisfies rule 5c, but rules 3 and 4 (one value, two values)
    come first and keep their precedence: the column is the binary (or
    constant) column it always was, its two values published, never held
    as record numbers. Mutant: `profile._counted_dates_declined` without its
    earlier-rule arm (the column `identifier`, as Codex measured).
    """
    _path, kept = _answered_clock_figures(tmp_path / "first")
    for name, cells, role in (
        ("two", ["0800" if index % 2 else "1600" for index in range(1200)], "binary"),
        ("one", ["0800"] * 1200, "constant"),
    ):
        folder = tmp_path / name
        rows = [[f"R{300000 + index}", cell, f"{60 + index % 80}"] for index, cell in enumerate(cells)]
        path = _write(folder, ["row_ref", "chart_time", "pulse"], rows)
        code, block, answers = _profiled_again(folder, path, kept)
        assert code == 0
        assert answers == [("chart_time", "clock-figures")], (name, answers)
        assert block["role"] == role, (name, block["role"])


def test_a_fraction_clock_whose_twin_holds_one_value_says_so(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 3, the round trip: 1,200 fractions of one second answered `clock-figures`.

    The column is `time_of_day` at its one whole second, and its twin writes
    `080000.000000` on every cell, which the earlier rule reads back as one
    value: the twin's report names that deviation of the role where it
    named none. Mutant: generation's `_figures_collapsed` returning nothing.
    """
    header, rows = _fraction_rows(1200, 0)
    seen = run_answered(tmp_path / "one", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["exits"][:3] == (0, 0, 0), seen["exits"]
    assert seen["block"]["role"] == "time_of_day" and seen["block"]["clock_form"] == "hh-mm-ss figures.6"
    assert set(seen["cells"]) == {"080000.000000"}
    report = (tmp_path / "one" / "t-twin-report.txt").read_text(encoding="utf-8")
    assert "reads back as constant" in report, report[-3000:]


def test_a_newer_date_count_replaces_a_kept_clock_figures_answer_and_the_other_way(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 4: a kept `clock-figures` and a newer counted-date reading never stand together.

    (a) Kept, then `--date-count chart_time seconds-since-1970` typed over
    six-figure afternoon times: the file keeps the date count alone and the
    column is read as those dates, where both were kept and the column held
    as record numbers. (b) The other way, in one questions file: a kept date
    count and the column's question answered `clock-figures` -- the newer
    answer is read and the date count is not. (c) And `typed_over_kept`
    leaves a kept `clock-figures` out under a typed date count. Mutant:
    `date_counts.MEMBERS` taken off the clock-figures row of
    `asking._CANNOT_STAND_TOGETHER`.
    """
    from synthtwin import asking

    path, kept = _answered_clock_figures(tmp_path / "first")
    afternoon = random.Random(41)
    rows = []
    for index in range(1200):
        second = 43200 + afternoon.randrange(43200)
        rows += [[f"R{300000 + index}", f"{second // 3600:02d}{second % 3600 // 60:02d}{second % 60:02d}",
                  f"{60 + index % 80}"]]
    folder = tmp_path / "counted"
    path = _write(folder, ["row_ref", "chart_time", "pulse"], rows)
    code, block, answers = _profiled_again(folder, path, kept, "--date-count", "chart_time", "seconds-since-1970")
    assert code == 0
    assert answers == [("chart_time", "seconds-since-1970")], answers
    assert block["role"] == "datetime", block["role"]
    # (b) the other way: the file the military times' first run wrote asks chart_time's question.
    asked = json.loads((tmp_path / "first" / "t-questions.json").read_text(encoding="utf-8"))
    folder = tmp_path / "open"
    path = _write(folder, *_clock_rows(1200, 3))
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"]) == 0
    document = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == "chart_time":
            entry["your_answer"] = "clock-figures"
    document["answered_before"] = asking.answered_before(
        asking.Given(date_counts=(("chart_time", "seconds-since-1970"),)))
    read = asking.answers_in(document, "q.json")
    assert read.clock_figures == ("chart_time",), read.clock_figures
    assert not [pair for pair in read.date_counts if pair[0] == "chart_time"], read.date_counts
    # (c) a typed date count over the kept answer, at the unit.
    left = asking.typed_over_kept(asked, (("chart_time", "seconds-since-1970"),))
    assert isinstance(left, dict)
    assert not [entry for entry in left.get("answered_before") or []
                if isinstance(entry, dict) and entry.get("column") == "chart_time"], left.get("answered_before")


def test_a_minority_of_another_zone_family_is_a_mixing(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane TR, item 5: 995 Eastern stamps beside 5 Central European ones (99.5 per cent) stay unread.

    The parse rate's allowance is for cells that read as no stamp, never
    for cells of another family, so the column mixes families and no zone
    layout reads it -- as an even mixture is not read -- where the Eastern
    layout read it with the 5 left unread (19,900 and 100 at 20,000 rows:
    100 twin cells of filler, no deviation). Cells of no family, `IST`
    among them, still fall to the allowance: 995 Eastern stamps beside 5
    `IST` ones read under the Eastern layout. Mutant:
    `taxonomy._another_zone_family` answering no.
    """
    header, rows = _eastern_rows(1000, 23)
    for index in range(0, 1000, 200):
        rows[index][1] = rows[index][1][:19] + (" CET" if rows[index][1].endswith("EST") else " CEST")
    seen = run(tmp_path / "mixed", header, rows, "seen_at")
    assert seen["exits"][0] == 0
    assert seen["block"]["role"] != "datetime", seen["block"].get("format")
    header, rows = _eastern_rows(1000, 23)
    for index in range(0, 1000, 200):
        rows[index][1] = rows[index][1][:19] + " IST"
    seen = run(tmp_path / "unparsed", header, rows, "seen_at")
    assert seen["block"]["role"] == "datetime" and seen["block"]["format"].endswith("{EST/EDT}"), seen["block"]["role"]


def _driver() -> "object":
    """K-HZ-26's driver, imported from tools/measurements as lane BT2's tests import theirs."""
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
    import kpi_zoo_time_readers

    return kpi_zoo_time_readers


def test_the_figures_leg_counts_every_real_value_outside_the_constant_and_count_locations() -> None:
    """Codex's review of lane TR, item 6 (THE HIPAA MEASURING TOOL): no real value is set apart, only locations.

    Codex's probe: real `0742` and `1000` published as string levels and
    written on three twin cells read 2 values and 3 cells -- where the leg,
    setting apart the fixed example `0742` and the setting `1000`, read 0
    and 0. A mutant that writes a real `0742` on one twin cell and
    publishes nothing reads 1 cell. The constant and count locations alone
    are set apart: the clock-figures choice's offered text naming `0742`,
    the settings block's ceiling of 1,000 and a count of 1,440 cells read 0
    beside a hold that publishes nothing. Mutant: the old set-apart of real
    values equal to a fixed example or a whole number of the description.
    """
    kpi = _driver()
    real = ["0742", "1000", "1440", "0742", "2359"]
    settings = {"settings": {"categorical_ceiling": 1000}}
    questions = {"asked": [{"column": "chart_time", "answers_you_can_give": [
        {"answer": "clock-figures", "means": "clock times written as figures alone -- `0742` is 07:42"}]}]}
    probe = dict(settings, columns=[{"name": "chart_time", "role": "categorical", "levels": {"0742": 12, "1000": 12}}])
    found = kpi.figures_counted(real, probe, questions, "", ["0742", "1000", "0742"])
    assert (found["values"], found["twin_cells"]) == (2, 3), found
    held = dict(settings, columns=[{"name": "chart_time", "role": "identifier", "layout_forms": {"%%%%": 1440}}])
    assert kpi.figures_counted(real, held, questions, "", ["10457", "88123"]) == {
        "values": 0, "fragments": 0, "twin_cells": 0}
    mutant = kpi.figures_counted(real, held, questions, "", ["10457", "0742"])
    assert mutant["twin_cells"] == 1, mutant
    # ...and a real value published as a measurement's statistic, a number with a point, is counted.
    measured = dict(settings, columns=[{"name": "chart_time", "role": "count", "percentiles": {"max": 2359.0}}])
    assert kpi.figures_counted(real, measured, questions, "", [])["values"] == 1
    # ...and the summary: its words for a count of the description are set apart (`1440 different values`, as
    # measured at 20,000 rows), any other figures it writes are searched.
    counted = dict(settings, columns=[{"name": "chart_time", "role": "identifier", "n_distinct": 1440}])
    assert kpi.figures_counted(real, counted, questions, "1440 different values", [])["values"] == 0
    assert kpi.figures_counted(real, counted, questions, "1440 different values; 2359 most often", [])["values"] == 1


def test_a_made_up_cell_of_every_zone_word_is_written_as_a_stamp_of_its_family() -> None:
    """LANE TR RULINGS 6 (3), carry C-B, A GENERATED UNIT CASE: a held column's made-up cell of each word's length, every family.

    For each of the 17 words, each of the six stamp forms before it and 30
    made-up cells in that cell's very shape (figures where it writes
    figures, letters where it writes letters, the identifier walk's way),
    the G1 floor finds a form some date wears (`grains.wears_a_date`) and
    writes it as a stamp of 2028 followed by a word of the family as long as
    the made-up one, reading back under the column's layout. Before, a
    made-up cell as long as `WEST`, `CEST` or `EEST` -- a letter longer than
    the family's standard word -- wore no date, and the twin kept the walk's
    value (11,760 of 20,000 cells of held birth stamps, invalid dates).
    Mutant: `grains._layout_written` trying no word but the standard one.
    """
    from synthtwin import date_counts, grains

    draw = random.Random(20261111)
    span = (parsing.days_from_civil(2028, 1, 1) * date_counts.DAY, parsing.days_from_civil(2029, 1, 1) * date_counts.DAY)
    written = 0
    for family, words in FAMILIES.items():
        for word, _offset in words:
            for form in STAMP_FORMS:
                real = (datetime.datetime(2020, 3, 14, 9, 26, 53).strftime(form).upper() if "%b" in form
                        else datetime.datetime(2020, 3, 14, 9, 26, 53).strftime(form)) + " " + word
                name = _stamp_layout(real, family)
                assert name is not None, (family, real)
                items = parsing.layout_items(name)
                assert items is not None
                reading = grains.Reading(grains.STAMP, name)
                for _case in range(30):
                    made_up = "".join(
                        draw.choice("0123456789") if character.isdigit()
                        else draw.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if character.isalpha() else character
                        for character in real
                    )
                    assert grains.wears_a_date(made_up, reading, True), (name, made_up)
                    made = grains.filled(made_up, reading, draw.getrandbits(64), span, True, {}, False, False)
                    assert made is not None, (name, made_up)
                    worn = made[made.rfind(" ") + 1:]
                    assert worn in dict(words) and len(worn) == len(word), (name, made_up, made)
                    read = parsing.layout_reading(made, items)
                    assert read is not None and read[0][:4] == "2028", (name, made)
                    written += 1
    assert written == 17 * len(STAMP_FORMS) * 30


def test_held_birth_stamps_with_a_european_zone_word_write_no_invalid_cell(tmp_path: pathlib.Path) -> None:
    """LANE TR RULINGS 6 (3), carry C-B, A TABLE-LEVEL SAMPLE: held `CET`/`CEST` birth stamps, the person answered `identifier`.

    The same 100 people born 1928 to 2005, 12 rows each: every twin cell is
    a stamp of 2028 followed by `CET` or `CEST`, none on a real calendar day,
    where the summer word's cells were the walk's invalid values (744 of
    1,200 here at the repair-1 head; 11,760 of 20,000 at 20,000 rows,
    validate exiting 0). Mutant: `grains._layout_written` trying no word but
    the standard one.
    """
    draw = random.Random(206)
    births = []
    for _person in range(100):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))]
    order = [index % 100 for index in range(1200)]
    draw.shuffle(order)
    real = [f"{births[person]:%Y-%m-%d %H:%M:%S} " + ("CEST" if 4 <= births[person].month <= 10 else "CET")
            for person in order]
    rows = [[f"Q{700000 + person}", real[row], f"{row % 7}"] for row, person in enumerate(order)]
    seen = run_answered(tmp_path / "cet", ["person_ref", "birth_ts", "grade"], rows, "birth_ts",
                        {"person_ref": "identifier"})
    assert seen["exits"][1:3] == (0, 0), seen["exits"]
    assert seen["block"]["made_up_years"] == [[2028, 2028]], seen["block"].get("made_up_years")
    days = {cell[:10] for cell in real}
    stamp = re.compile(r"2028-\d\d-\d\d \d\d:\d\d:\d\d (CET|CEST)")
    bad = [cell for cell in seen["cells"] if not stamp.fullmatch(cell)]
    assert not bad, (len(bad), bad[:3])
    assert not [cell for cell in seen["cells"] if cell[:10] in days]
    assert {cell[20:] for cell in seen["cells"]} == {"CET", "CEST"}


# -- the follow-up (LANE TR RULINGS 7) --------------------------------------

# The forms before a zone word that write a fraction of a second: three or six
# figures, ISO, day-first with dots, month-first with slashes.
FRACTION_FORMS = (
    "%Y-%m-%d %H:%M:%S.{ms}",
    "%Y-%m-%d %H:%M:%S.{us}",
    "%d.%m.%Y %H:%M:%S.{ms}",
    "%m/%d/%Y %H:%M:%S.{ms}",
)
# The forms of the class: to the second, to the minute, with three and six
# figures of fraction, day-first with dots, a month's word, a two-figure year,
# the 12-hour clock.
HELD_ZONE_FORMS = {
    "second": "%Y-%m-%d %H:%M:%S",
    "minute": "%Y-%m-%d %H:%M",
    "milliseconds": "%Y-%m-%d %H:%M:%S.{ms}",
    "microseconds": "%Y-%m-%d %H:%M:%S.{us}",
    "dots": "%d.%m.%Y %H:%M",
    "month word": "%d-%b-%Y %H:%M:%S",
    "two-figure year": "%m/%d/%y %H:%M",
    "12-hour": "%m/%d/%Y %I:%M %p",
}
_A_MOMENT = datetime.datetime(2020, 3, 14, 9, 26, 53, 123456)


def _zone_stamp(moment: datetime.datetime, form: str, word: str) -> str:
    """An instant in one of this file's forms, `{ms}` and `{us}` filled, a month's word in capitals, then the zone word."""
    text = moment.strftime(form.replace("{ms}", f"{moment.microsecond // 1000:03d}").replace(
        "{us}", f"{moment.microsecond:06d}"))
    return f"{text.upper() if '%b' in form else text} {word}"


def _made_up(real: str, draw: random.Random) -> str:
    """A held column's made-up cell in a real cell's very shape: figures for figures, capitals for letters (the walk's way)."""
    return "".join(
        draw.choice("0123456789") if character.isdigit()
        else draw.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if character.isalpha() else character
        for character in real
    )


def test_a_made_up_stamp_with_a_fraction_before_its_zone_word_is_drawn_with_its_fraction() -> None:
    """LANE TR RULINGS 7 (2), A GENERATED UNIT CASE: the G1 floor draws a held zone stamp whose fraction precedes the word.

    For each of the 17 words, four forms with a fraction of a second and 30
    made-up cells in that cell's very shape, `grains.wears_a_date` finds a
    form some date wears and `grains.filled` writes a stamp of 2028 whose
    fraction has the made-up one's figures, written as noughts, followed by
    a word of the family as long as the made-up one, reading back under the
    column's layout: 2,040 cells. At 7d968bb8 the fraction was read from the
    cell's last run, the word, so none was found: the made-up cell wore no
    date and the twin kept the identifier walk's value (20,000 of 20,000
    cells of held birth stamps, `9239-30-79 96:66:35.510 UIW`). Mutant: the
    fraction read from the last run alone in `grains._layout_written`.
    """
    from synthtwin import date_counts, grains

    draw = random.Random(20261111 + 2)
    span = (parsing.days_from_civil(2028, 1, 1) * date_counts.DAY, parsing.days_from_civil(2029, 1, 1) * date_counts.DAY)
    written = 0
    for family, words in FAMILIES.items():
        for word, _offset in words:
            for form in FRACTION_FORMS:
                real = _zone_stamp(_A_MOMENT, form, word)
                name = _stamp_layout(real, family)
                assert name is not None, (family, real)
                items = parsing.layout_items(name)
                assert items is not None
                reading = grains.Reading(grains.STAMP, name)
                figures = len(real[: real.rfind(" ")].rsplit(".", 1)[1])
                for _case in range(30):
                    made_up = _made_up(real, draw)
                    assert grains.wears_a_date(made_up, reading, True), (name, made_up)
                    made = grains.filled(made_up, reading, draw.getrandbits(64), span, True, {}, False, False)
                    assert made is not None and len(made) == len(made_up), (name, made_up, made)
                    body, worn = made[: made.rfind(" ")], made[made.rfind(" ") + 1:]
                    assert worn in dict(words) and len(worn) == len(word), (name, made)
                    assert body.rsplit(".", 1)[1] == "0" * figures, (name, made)
                    read = parsing.layout_reading(made, items)
                    assert read is not None and read[0][:4] == "2028", (name, made)
                    written += 1
    assert written == 17 * len(FRACTION_FORMS) * 30


def _held_zone_block(tmp_path: pathlib.Path) -> "object":
    """A held birth-stamp column's block (the G1 floor's), its stamps followed by EST or EDT, profiled with nobody at the
    keyboard from 600 rows (a test size the command refuses), 30 people born 1928 to 2005, 20 rows each."""
    from synthtwin import contract, grains

    draw = random.Random(206)
    births = []
    for _person in range(30):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))]
    order = [index % 30 for index in range(600)]
    draw.shuffle(order)
    rows = [[f"Q{700000 + person}", f"{births[person]:%Y-%m-%d %H:%M:%S} " + ("EDT" if 4 <= births[person].month <= 10
                                                                            else "EST"), f"{row % 7}"]
            for row, person in enumerate(order)]
    path = _write(tmp_path / "block", ["person_ref", "birth_ts", "grade"], rows)
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert cli.main(["profile", f"{path}", "--out-dir", f"{tmp_path / 'block'}", "--replace"],
                            small_tables_refused=False) == 0
    column = [one for one in contract.load_profile(f"{tmp_path / 'block' / 't-profile.json'}").columns
              if one.name == "birth_ts"][0]
    assert column.time_grain is not None and column.time_grain.rung == grains.HELD
    assert column.time_grain.reading.kind == grains.STAMP
    assert isinstance(column.facts, contract.IdentifierFacts)
    return column


def test_a_held_zone_word_column_writes_a_drawn_stamp_or_a_blank_never_the_walk_s_value(tmp_path: pathlib.Path) -> None:
    """LANE TR RULINGS 7 (2), A GENERATED UNIT CASE OF THE CLASS: what `generation._inside_the_grain` writes in a held zone column.

    For each of the nine families, the eight forms of `HELD_ZONE_FORMS` and
    two rooms -- none (the `[]` of NF137) and the year 2028 -- 30 made-up
    cells in a real cell's very shape, one made-up stamp of a form the
    census publishes that no date of the layout wears (no seconds where the
    layout writes them), and one made-up word holding no figure: every cell
    holding a figure leaves as a stamp of 2028 that reads back under the
    column's layout, or blank -- never the identifier walk's value, which is
    no date (LANE TR RULINGS 6 (3): never a twin cell that is an invalid
    date string where the base wrote a blank); the word stays the walk's, a
    stand-in of a real word. With no room every cell holding a figure is
    blank; with the room the fraction forms' cells are all drawn. At
    7d968bb8 the walk's values stood: 20,000 of 20,000 cells for a fraction,
    a month's word or a two-figure year before EST/EDT. Mutants:
    `generation._zone_word_layout` answering no; the published-layout arm
    keeping the walk's value; the fraction read from the last run alone.
    """
    import dataclasses

    from synthtwin import contract, generation, grains

    base = _held_zone_block(tmp_path)
    grain = base.time_grain  # type: ignore[attr-defined]
    facts = base.facts  # type: ignore[attr-defined]
    convention = generation._layout_convention(facts)
    draw = random.Random(20261111 + 3)
    looked = 0
    for family, words in FAMILIES.items():
        for key, form in HELD_ZONE_FORMS.items():
            name = _stamp_layout(_zone_stamp(_A_MOMENT, form, words[0][0]), family)
            assert name is not None, (family, key)
            items = parsing.layout_items(name)
            assert items is not None
            cells = [_made_up(_zone_stamp(_A_MOMENT, form, word), draw) for word, _offset in words for _case in range(30)]
            cells = cells[:30] + [_made_up(_zone_stamp(_A_MOMENT, "%Y-%m-%d %H", words[0][0]), draw), "QWERTYU"]
            forms: "dict[str, int]" = {}
            for cell in cells:
                forms[parsing.layout_form(cell, convention)] = forms.get(parsing.layout_form(cell, convention), 0) + 1
            for years in ((), ((2028, 2028),)):
                column = dataclasses.replace(
                    base,
                    time_grain=dataclasses.replace(grain, reading=grains.Reading(grains.STAMP, name)),
                    facts=dataclasses.replace(facts, layout_forms=forms, made_up_years=years),
                )
                assert isinstance(column.facts, contract.IdentifierFacts)
                found, _unwritten = generation._inside_the_grain(column, cells, [draw.getrandbits(64) for _cell in cells])
                for cell, made in zip(cells, found):
                    looked += 1
                    if cell == "QWERTYU":
                        assert made == cell, (name, years, made)
                        continue
                    assert made != cell, (name, years, cell)
                    if made:
                        read = parsing.layout_reading(made, items)
                        assert read is not None and read[0][:4] == "2028", (name, years, cell, made)
                    if not years:
                        assert made == "", (name, cell, made)
                    if years and key in ("milliseconds", "microseconds") and cell != cells[30]:
                        assert made, (name, cell)
    assert looked == 9 * len(HELD_ZONE_FORMS) * 2 * 32


def test_a_held_zone_word_value_the_floor_does_not_draw_is_written_blank(tmp_path: pathlib.Path, monkeypatch) -> None:
    """LANE TR RULINGS 7 (2): the arm where `grains.filled` gives None in every span of the room.

    With the G1 floor drawing nothing (its two writers stubbed to give None,
    every made-up value taken as one some date wears), a held zone-word
    column with the room 2028 writes each made-up value holding a figure
    blank, never the walk's value, and keeps a made-up word holding none as
    the walk wrote it, counted among the values left as made up. Mutant: the
    arm writing the walk's value for every value the floor gives None for.
    """
    import dataclasses

    from synthtwin import generation, grains

    base = _held_zone_block(tmp_path)
    facts = base.facts  # type: ignore[attr-defined]
    draw = random.Random(20261111 + 4)
    cells = [_made_up(_zone_stamp(_A_MOMENT, "%Y-%m-%d %H:%M:%S", "EST"), draw) for _case in range(20)] + ["QWERTYU"]
    column = dataclasses.replace(base, facts=dataclasses.replace(facts, made_up_years=((2028, 2028),)))
    monkeypatch.setattr(grains, "filled", lambda *arguments, **named: None)
    monkeypatch.setattr(grains, "filled_at_its_length", lambda *arguments, **named: None)
    monkeypatch.setattr(grains, "wears_a_date", lambda *arguments, **named: True)
    found, unwritten = generation._inside_the_grain(column, cells, [draw.getrandbits(64) for _cell in cells])
    assert found[:20] == [""] * 20, found[:3]
    assert found[20] == "QWERTYU" and unwritten == 1, (found[20], unwritten)


# The class's three forms at a table: (the form before the word, the shape each twin cell has, or None for a blank).
_ZONE_TABLE_FORMS = {
    "fraction": ("%Y-%m-%d %H:%M:%S.{ms}", r"2028-\d\d-\d\d \d\d:\d\d:\d\d\.000 (EST|EDT)"),
    "month word": ("%d-%b-%Y %H:%M:%S", None),
    "two-figure year": ("%m/%d/%y %H:%M", None),
}


def test_held_zone_word_birth_stamps_write_a_stamp_or_a_blank_never_an_invalid_cell(tmp_path: pathlib.Path) -> None:
    """LANE TR RULINGS 7 (2), A TABLE-LEVEL SAMPLE: held birth stamps followed by EST or EDT, the person answered `identifier`.

    The same 100 people born 1928 to 2005 as carry C-B's case, 12 rows each.
    With a fraction of a second the room holds 2028 and every twin cell is
    a stamp of 2028 whose fraction is three noughts, none on a real day; with
    a month's word or a two-figure year the producer publishes no room
    (`[]`, NF137) and every twin cell is blank, as the base wrote, the twin's
    report naming them -- where 7d968bb8's twins wrote the walk's values, no
    date, on every cell (20,000 of 20,000 at 20,000 rows, validate exiting
    0). Mutants: `generation._zone_word_layout` answering no; the fraction
    read from the last run alone.
    """
    draw = random.Random(206)
    births = []
    for _person in range(100):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))]
    fractions = random.Random(207)
    births = [moment.replace(microsecond=1000 * fractions.randrange(1000)) for moment in births]
    order = [index % 100 for index in range(1200)]
    draw.shuffle(order)
    days = {f"{moment:%Y-%m-%d}" for moment in births}
    for key, (form, shape) in _ZONE_TABLE_FORMS.items():
        real = [_zone_stamp(births[person], form, "EDT" if 4 <= births[person].month <= 10 else "EST")
                for person in order]
        rows = [[f"Q{700000 + person}", real[row], f"{row % 7}"] for row, person in enumerate(order)]
        folder = tmp_path / key.replace(" ", "-")
        seen = run_answered(folder, ["person_ref", "birth_ts", "grade"], rows, "birth_ts", {"person_ref": "identifier"})
        assert seen["exits"][1:3] == (0, 0), (key, seen["exits"])
        cells = seen["cells"]
        if shape is None:
            assert seen["block"]["made_up_years"] == [], (key, seen["block"].get("made_up_years"))
            assert set(cells) == {""}, (key, sorted(set(cells))[:3])
            report = (folder / "t-twin-report.txt").read_text(encoding="utf-8")
            assert "1200 cells written blank" in report, (key, report[-2000:])
            continue
        assert seen["block"]["made_up_years"] == [[2028, 2028]], (key, seen["block"].get("made_up_years"))
        assert seen["exits"][3] == 0, (key, seen["exits"])
        bad = [cell for cell in cells if not re.fullmatch(shape, cell)]
        assert not bad, (key, len(bad), bad[:3])
        assert not [cell for cell in cells if cell[:10] in days], key


def test_a_minority_of_another_family_beside_cells_without_a_word_is_a_mixing() -> None:
    """LANE TR RULINGS 7 (3), mutant X1: the walk over grown layouts (the optional word's) refuses a mixing too.

    At 20,000 rows Eastern stamps with one cell in twenty written without a
    word and one in two hundred Central European are no column of the
    Eastern layout -- it misses 1,100 cells, past the parse rate's 200 --
    so only the grown layout with an optional word could read them, missing
    the 100 Central European cells; and the mirror, Central European stamps
    beside Eastern ones. The walk names no layout for either, as for the
    first walk's mixing. Measured by the verify at 20,000 rows through the
    command: under the mutant both read `datetime` under `{EST/EDT?}` and
    `{CET/CEST?}`, 100 cells of the other family unparsed. Mutant X1: the
    mixing check off in the walk over grown layouts (`taxonomy._layout_walk`).
    """
    from synthtwin import taxonomy

    settings = taxonomy.Settings()
    for own, other in ((("EDT", "EST"), ("CEST", "CET")), (("CEST", "CET"), ("EDT", "EST"))):
        draw = random.Random(31)
        counted: "dict[str, int]" = {}
        for index in range(20000):
            day = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(730))
            moment = datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))
            summer = 4 <= moment.month <= 10
            text = f"{moment:%Y-%m-%d %H:%M:%S}"
            if index % 200 == 7:
                text = f"{text} {other[0] if summer else other[1]}"
            elif index % 20 != 3:
                text = f"{text} {own[0] if summer else own[1]}"
            counted[text] = counted.get(text, 0) + 1
        needed = taxonomy._needed(settings.minimum_parse_rate, 20000)
        found = taxonomy._chosen_layout(counted, 20000, needed, False, False, taxonomy.century_window_of(settings))
        assert found is None, (own, found[0] if found else None)


def test_a_fraction_clock_whose_twin_holds_two_values_says_so(tmp_path: pathlib.Path) -> None:
    """LANE TR RULINGS 7 (3), mutant X3: Codex's round trip at two seconds, the twin reading back as two values.

    1,200 fractions of 08:00:00 and of 16:00:00 answered `clock-figures`: the
    column is `time_of_day` at its whole seconds, its twin writes
    `080000.000000` and `160000.000000` alone, which the earlier rule reads
    back as two values, and the twin's report names that deviation of the
    role (the verify's item 3: "reads back as binary"). Mutant X3: a twin of
    two values naming no deviation (`generation._figures_collapsed`).
    """
    header, rows = _fraction_rows(1200, 0)
    for index in range(1, 1200, 2):
        rows[index][1] = "16" + rows[index][1][2:]
    seen = run_answered(tmp_path / "two", header, rows, "chart_time", {"chart_time": "clock-figures"})
    assert seen["exits"][:3] == (0, 0, 0), seen["exits"]
    assert seen["block"]["role"] == "time_of_day" and seen["block"]["clock_form"] == "hh-mm-ss figures.6"
    assert set(seen["cells"]) == {"080000.000000", "160000.000000"}
    report = (tmp_path / "two" / "t-twin-report.txt").read_text(encoding="utf-8")
    assert "reads back as binary" in report, report[-3000:]


def test_the_driver_counts_a_held_european_cell_that_is_no_stamp() -> None:
    """LANE TR RULINGS 7 (3), mutant X4: K-HZ-26's counter of twin cells that are no stamp, at the unit.

    Under the Central European spelling the identifier walk's value
    `9528-75-82 71:81:15 MNYY` -- the 11,760 cells a run of carry C-B -- is
    one cell that is no stamp, and `2028-07-12 23:52:12 CEST` none; a blank
    is no cell, an Eastern word under that spelling is one, and the
    fraction spelling counts its own form only. Mutant X4: the driver
    counting no cell as no stamp.
    """
    kpi = _driver()
    assert kpi.no_stamp_cells(["9528-75-82 71:81:15 MNYY"], "zone-eu") == 1
    assert kpi.no_stamp_cells(["2028-07-12 23:52:12 CEST"], "zone-eu") == 0
    assert kpi.no_stamp_cells(["", "2028-01-20 12:13:54 CET", "2028-01-20 12:13:54 EST"], "zone-eu") == 1
    assert kpi.no_stamp_cells(["9239-30-79 96:66:35.510 UIW", "2028-07-26 00:08:59.000 EST"], "zone-fraction") == 1


def test_the_keyboard_offers_clock_figures_only_where_no_time_is_written_as_a_missing_spelling() -> None:
    """LANE TR RULINGS 7 (3), mutant X2 SHOWN EQUIVALENT: the keyboard's message of an answer not taken is never said.

    The keyboard puts the questions asked, never the checklist's entries
    (they are shown), and the asked question offers `clock-figures` only
    where a width question is put (`asking.why_worth_asking`, padded or
    fixed width, on the cells or on their figures where every cell writes
    the same noughts after a point) and rule 5c's conditions hold. (1) A
    column of clock figures with a fraction other than noughts raises no
    width question, at every width of fraction. (2) Every figure form writes
    each time of its grid back exactly as it reads it (`parsing.clock_spelling`
    of `parsing.clock_ordinal`), a fraction of noughts included. (3) So a
    column the keyboard may answer `clock-figures` -- figures alone, or the
    same noughts after a point -- never reads `FIGURES_ABSENT`, whatever the
    missing values declared in whatever width: 2,400 generated columns. The
    keyboard's arm of the message (mutant X2) changes no run; it stays as a
    guard. Mutant: the figures before a point read as a width question
    whatever figures follow it (`asking._without_nought_places`).
    """
    from synthtwin import asking, taxonomy

    draw = random.Random(20261111 + 5)
    for figures in range(1, 7):
        cells = [f"{draw.randrange(24):02d}{draw.randrange(60):02d}{draw.randrange(60):02d}."
                 f"{draw.randrange(1, 10 ** figures):0{figures}d}" for _cell in range(40)]
        assert asking.why_worth_asking(cells) not in (asking.BECAUSE_PADDED, asking.BECAUSE_FIXED_WIDTH), figures
        assert asking._without_nought_places(cells) == [], figures
    for form in parsing.CLOCK_FIGURE_FORMS:
        for _case in range(400):
            text = parsing.clock_spelling(draw.randrange(parsing.CLOCK_CAPACITY[form]), form)
            again = parsing.clock_ordinal(text, form)
            assert again is not None and parsing.clock_spelling(again, form) == text, (form, text)
    checked = 0
    for form in parsing.CLOCK_FIGURE_FORMS:
        for _case in range(300):
            cells = [parsing.clock_spelling(draw.randrange(parsing.CLOCK_CAPACITY[form]), form) for _cell in range(40)]
            chosen = draw.choice(cells)
            widths = (chosen, chosen.lstrip("0") or "0", f"{float(chosen):.1f}", f"{chosen}0" if "." in chosen else chosen)
            settings = taxonomy.Settings(declared_missing_values=(draw.choice(widths),))
            assert taxonomy.clock_figures_reading(cells, settings) != taxonomy.FIGURES_ABSENT, (form, chosen, settings)
            checked += 1
    assert checked == 300 * len(parsing.CLOCK_FIGURE_FORMS)
