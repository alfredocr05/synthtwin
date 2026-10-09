"""THE CODEX REVIEW OF LANDING R4 (plan P4-D384): its nine items, each pinned.

Each clause reproduces the reviewer's own input and turned red on the
landing's head, `dbb347a`:

* item 1 -- a declared column mixing counts with dates written as text is
  declined in NF115 with a way out, and the producer never writes a
  description its loader refuses (a battery over mixed columns);
* item 2 -- a column is settled only to a unit its writer keeps: Excel
  serials written `%.14f` are read at the millisecond, and every moment
  the twin is drawn at reads back as itself;
* item 3 -- the producer publishes a form only where its own checker holds
  every count, and the writer writes nothing the checker refuses;
* item 4 -- a rare absent count, the producer's own decision or the
  person's `--missing-value`, is not held to the form;
* item 5 -- Q3's midnight rule reads whole counts written `.0`;
* item 6 -- a rule whose text check fails lets the next rule run;
* item 7 -- a count's exact value is bounded before it is built, and
  redundant figures are dropped;
* item 8 -- the exponent form of contract 6.6.2: whole figures of any
  length, `17e+8`, `1704067200e+0`;
* item 9 -- every one of the twelve systems has a reading and a writing
  anchor worked out from the calendar, and moving its epoch by one day
  turns its anchor red.

Every table is built here, seeded and made up (plan D13).
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import pathlib
import random
import tracemalloc

import pytest

from synthtwin import contract, date_counts, parsing, reading, taxonomy, validation
from synthtwin import asking

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-26.json"


def _exit_of(argv: "list[str]") -> "tuple[int, str]":
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return code, said.getvalue()


def _table(folder: pathlib.Path, cells: "list[str]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "table.csv"
    path.write_text("seen\n" + "\n".join(cells) + "\n", encoding="utf-8", newline="\n")
    return path


def _described(folder: pathlib.Path, cells: "list[str]", member: str, *extra: str) -> "dict[str, object]":
    """One column `seen`, profiled through the command line, its description loaded strictly."""
    path = _table(folder, cells)
    argv = ["profile", str(path), "--out-dir", str(folder), "--replace", *extra]
    if member:
        argv += ["--date-count", "seen", member]
    code, said = _exit_of(argv)
    assert code == 0, said[-800:]
    described = folder / "table-profile.json"
    loaded = contract.load_profile(str(described))
    return {
        "path": path,
        "described": described,
        "loaded": loaded,
        "block": json.loads(described.read_text(encoding="utf-8"))["columns"][0],
        "said": said,
    }


def _twin(trip: "dict[str, object]", folder: pathlib.Path) -> "list[str]":
    folder.mkdir(parents=True, exist_ok=True)
    code, said = _exit_of(["generate", str(trip["described"]), "--seed", "0", "--out-dir", str(folder), "--replace"])
    assert code == 0, said[-800:]
    return (folder / "table-twin.csv").read_text(encoding="utf-8").splitlines()[1:]


def _missed(trip: "dict[str, object]", checked: pathlib.Path) -> "list[str]":
    """Every subcheck a file MISSES against the description."""
    loaded = trip["loaded"]
    assert isinstance(loaded, contract.Profile)
    outcome = validation.measure(loaded, str(checked))
    return sorted({check.subcheck for check in outcome.checks if check.verdict == validation.MISSED})


def _block_of(tmp: pathlib.Path, cells: "list[str]") -> "dict[str, object]":
    path = _table(tmp, cells)
    table = reading.read_table(str(path))
    from synthtwin import profile

    return profile.build_document(table, taxonomy.Settings(), [])["columns"][0]


def _declined(block: "dict[str, object]") -> bool:
    remarks = block["remarks"]
    assert isinstance(remarks, list)
    return block.get("count_form") is None and any(contract.COUNTED_NOT_READ_MARK in remark for remark in remarks)


# -- item 1: counts beside dates written as text --------------------------------


def test_item1_counts_beside_iso_dates_are_declined_with_a_way_out(tmp_path: pathlib.Path) -> None:
    """900 Excel serials and 100 cells `2023-06-01`: no twin of numbers alone, and NF115 says why and what to do.

    On `dbb347a` the column was described as counted dates with no
    unparsed cell, its twin held numbers only, and the source met its own
    form check.
    """
    cells = [f"{45000 + row}" for row in range(900)] + ["2023-06-01"] * 100
    random.Random(1).shuffle(cells)
    trip = _described(tmp_path, cells, "excel-1900")
    block = trip["block"]
    assert isinstance(block, dict)
    assert _declined(block), block["count_form"]
    said = taxonomy.rendered(taxonomy.REMARK_COUNTED_DATES_NOT_READ, ("excel-1900",))
    assert "written as dates in text" in said and "the same way" in said
    twin = _twin(trip, tmp_path / "twin")
    assert any(not parsing.is_digit_text(cell) for cell in twin if cell)


def test_item1_epic_contacts_beside_iso_dates_never_write_what_the_loader_refuses(tmp_path: pathlib.Path) -> None:
    """900 Epic days carrying `.01` and 100 ISO cells: on `dbb347a` the loader refused the description (CD4)."""
    cells = [f"{64000 + row}.01" for row in range(900)] + ["2023-06-01"] * 100
    random.Random(2).shuffle(cells)
    trip = _described(tmp_path, cells, "days-since-1840")
    block = trip["block"]
    assert isinstance(block, dict)
    assert _declined(block)
    _twin(trip, tmp_path / "twin")
    assert _missed(trip, tmp_path / "twin" / "table-twin.csv") == []
    assert _missed(trip, trip["path"]) == []


_MIXED_COUNTS = {
    "excel-1900": lambda row: f"{44000 + row % 900}",
    "excel-1900-times": lambda row: f"{44000 + row % 900 + (row % 96) / 96:.6f}",
    "seconds-since-1970": lambda row: f"{1600000000 + 86400 * (row % 900) + 3600 * (row % 7)}",
    "milliseconds-since-1970": lambda row: f"{1600000000000 + 86400000 * (row % 900)}",
    "days-since-1960": lambda row: f"{21000 + row % 900}",
    "days-since-1840": lambda row: f"{64000 + row % 900}" + (".01" if row % 3 == 0 else ""),
}
_MIXED_TEXTS = {
    "iso-date": lambda row: f"2021-{1 + row % 12:02d}-{1 + row % 28:02d}",
    "iso-datetime": lambda row: f"2021-{1 + row % 12:02d}-{1 + row % 28:02d} 10:30:00",
    "slashed": lambda row: f"{1 + row % 12:02d}/{1 + row % 28:02d}/2021",
    "word": lambda row: "unknown",
}


@pytest.mark.parametrize("counts", sorted(_MIXED_COUNTS))
@pytest.mark.parametrize("texts", sorted(_MIXED_TEXTS))
@pytest.mark.parametrize("share", (1, 20, 120))
def test_item1_the_producer_always_loads_over_mixed_count_and_text_columns(
    tmp_path: pathlib.Path, counts: str, texts: str, share: int
) -> None:
    """Battery: every declared column of counts beside text cells is described in a form the loader takes.

    And where any text cell is an ISO date -- one the column's counts,
    read as dates, would be written as -- the declaration is declined.
    """
    member = counts if counts != "excel-1900-times" else "excel-1900"
    rows = 600
    cells = [_MIXED_COUNTS[counts](row) for row in range(rows - share)]
    cells += [_MIXED_TEXTS[texts](row) for row in range(share)]
    random.Random(f"{counts}:{texts}:{share}").shuffle(cells)
    trip = _described(tmp_path, cells, member)
    block = trip["block"]
    assert isinstance(block, dict)
    if texts.startswith("iso"):
        assert _declined(block), (counts, texts, share)
    _twin(trip, tmp_path / "twin")
    missed = _missed(trip, tmp_path / "twin" / "table-twin.csv")
    assert _missed(trip, trip["path"]) == []
    if block.get("count_form") is not None:
        assert missed == []
        return
    # DECLINED, THE COLUMN IS THE COLUMN UNDECLARED: its twin meets its
    # description as the undeclared one's does (a free-text twin of
    # numbers beside dates misses its published forms either way, a limit
    # of the free-text role that no declaration touches).
    plain = _described(tmp_path / "plain", cells, "")
    _twin(plain, tmp_path / "plain" / "twin")
    assert missed == _missed(plain, tmp_path / "plain" / "twin" / "table-twin.csv"), (counts, texts, share)


# -- item 2: a unit the writer keeps -------------------------------------------


def test_item2_excel_serials_written_to_fourteen_places_are_read_at_a_unit_the_writer_keeps(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's input: `%.14f` of whole-second Excel moments published nanoseconds on `dbb347a`.

    999 of 1,000 moments the writer was handed read back as another one
    at that precision. The reading now settles at the millisecond, the
    moments stand on whole seconds, and every moment written at the
    published unit reads back as itself.
    """
    cells = [f"{45293 + row + (31359 + row) / 86400:.14f}" for row in range(1000)]
    trip = _described(tmp_path, cells, "excel-1900")
    loaded = trip["loaded"]
    assert isinstance(loaded, contract.Profile)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    assert unit == date_counts.SECOND
    moved = 0
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        moment = date_counts.moment_of("excel-1900", *date_counts.exact_value(written), unit)
        assert moment is not None
        again = date_counts.written_for("excel-1900", moment, unit, facts.count_form)
        assert again is not None
        back = date_counts.written_count(again)
        assert back is not None
        if date_counts.moment_of("excel-1900", *date_counts.exact_value(back), unit) != moment:
            moved = moved + 1
    assert moved == 0
    _twin(trip, tmp_path / "twin")
    assert _missed(trip, tmp_path / "twin" / "table-twin.csv") == []
    assert _missed(trip, trip["path"]) == []


@pytest.mark.parametrize("member", date_counts.MEMBERS)
def test_item2_every_unit_a_reading_settles_at_is_one_its_writer_keeps(member: str) -> None:
    """Every member, figures after the point from 1 to 17 written through binary64: the moments the reading settles read back as themselves."""
    if date_counts.TABLE[member].contacts:
        return
    draw = random.Random(member)
    found = date_counts.TABLE[member]
    first = parsing.days_from_civil(2000, 1, 1)
    for places in (1, 3, 6, 10, 12, 14, 17):
        exact: "list[tuple[int, int]]" = []
        tallies: "dict[int, date_counts.Tally]" = {}
        for _row in range(200):
            nanos = (first + draw.randrange(9000)) * date_counts.DAY + draw.randrange(date_counts.DAY)
            count = date_counts.count_of(member, nanos, 1)
            assert count is not None
            text = f"{count[0] / count[1]:.{places}f}"
            written = date_counts.written_count(text)
            assert written is not None
            exact += [date_counts.exact_value(written)]
            date_counts.tallied_by_places(tallies, written)
        tally = date_counts.every_count(tallies)
        form = date_counts.form_from(tally, ".", None)
        read = date_counts.settled_reading(member, form, tally, exact)
        if read is None:
            continue
        settled, unit, _moments = read
        assert unit >= settled
        # THE TWIN DRAWS ITS OWN MOMENTS at the published unit: each must
        # read back as itself once written.
        for _row in range(200):
            nanos = (first + draw.randrange(9000)) * date_counts.DAY + draw.randrange(date_counts.DAY)
            moment = nanos // unit
            text = date_counts.written_for(member, moment, unit, form)
            assert text is not None
            back = date_counts.written_count(text)
            assert back is not None
            assert date_counts.moment_of(member, *date_counts.exact_value(back), unit) == moment, (
                member, places, found.unit, text,
            )


# -- item 3: one spelling rule ---------------------------------------------------


@pytest.mark.parametrize(
    "spelled",
    (
        lambda row: str(1704067200 + row * 86400) + (".0" if row % 2 else ""),
        lambda row: f"{1704067200 + row * 86400:.14e}",
        lambda row: f"{1704067200 + row * 86400 + (row % 10) / 10:.14e}",
    ),
    ids=("alternating-point-zero", "percent-e-whole", "percent-e-tenths"),
)
def test_item3_the_source_meets_the_form_its_producer_published(
    tmp_path: pathlib.Path, spelled: "object"
) -> None:
    """Codex's inputs: on `dbb347a` the source missed `form.count_form` of its own description."""
    assert callable(spelled)
    cells = [spelled(row) for row in range(100)]
    trip = _described(tmp_path, cells, "seconds-since-1970")
    assert "form.count_form" not in _missed(trip, trip["path"])
    # WHETHER THE FORM IS PUBLISHED OR THE DECLARATION DECLINED, the twin
    # meets the description: a declined column's twin is read without the
    # declaration, as its source was.
    _twin(trip, tmp_path / "twin")
    assert _missed(trip, tmp_path / "twin" / "table-twin.csv") == []


def test_item3_an_exponent_forms_own_writing_is_one_its_checker_holds() -> None:
    """`1.70406720000001e+18` nanoseconds: the writer wrote `1704067200000010000`, which the checker refused as nineteen figures."""
    member = date_counts.NANOSECONDS_SINCE_1970
    written = date_counts.written_count("1.70406720000001e+18")
    assert written is not None
    form = date_counts.form_of([written], ".", None)
    assert form.exponent
    moment = date_counts.moment_of(member, *date_counts.exact_value(written), date_counts.NANOSECOND)
    assert moment is not None
    text = date_counts.written_for(member, moment, date_counts.NANOSECOND, form)
    assert text is not None
    again = date_counts.written_count(text)
    assert again is not None and date_counts.form_holds(member, form, again), text


_FORMS = (
    date_counts.CountForm(0, False, None, False, ".", None),
    date_counts.CountForm(3, False, None, False, ".", None),
    date_counts.CountForm(6, False, None, False, ".", None),
    date_counts.CountForm(6, True, None, False, ".", None),
    date_counts.CountForm(10, True, 15, False, ".", None),
    date_counts.CountForm(12, True, 17, False, ".", None),
    date_counts.CountForm(0, True, 15, True, ".", None),
    date_counts.CountForm(6, True, None, False, ",", None),
)


@pytest.mark.parametrize("member", date_counts.MEMBERS)
def test_item3_the_writer_writes_nothing_its_checker_refuses(member: str) -> None:
    """Battery: every member, eight forms, whole and broken moments: each cell written is one `form_holds` holds."""
    draw = random.Random(f"writer:{member}")
    first = parsing.days_from_civil(1990, 1, 1)
    for form in _FORMS:
        for unit in (date_counts.DAY, date_counts.SECOND, date_counts.MILLISECOND, date_counts.NANOSECOND):
            for _row in range(60):
                nanos = (first + draw.randrange(20000)) * date_counts.DAY
                if unit < date_counts.DAY:
                    nanos = nanos + draw.randrange(date_counts.DAY)
                moment = nanos // unit
                text = date_counts.written_for(member, moment, unit, form)
                if text is None:
                    continue
                written = date_counts.counted(member, text, form.mark)
                assert written is not None, (member, form, text)
                assert date_counts.form_holds(member, form, written), (member, form, text)


# -- item 4: absent counts are not held to the form --------------------------------


@pytest.mark.parametrize("absent,extra", (("1", ()), ("9999", ("--missing-value", "9999"))))
def test_item4_a_rare_absent_count_is_not_held_to_the_form(
    tmp_path: pathlib.Path, absent: str, extra: "tuple[str, ...]"
) -> None:
    """999 serials written `%.6f` and one `1` (or one declared `9999`, a word the settings record): on `dbb347a` the source missed its form."""
    cells = [f"{45000 + row}.500000" for row in range(999)] + [absent]
    trip = _described(tmp_path, cells, "excel-1900", *extra)
    block = trip["block"]
    assert isinstance(block, dict) and block["count_form"] is not None
    assert _missed(trip, trip["path"]) == []


_NO_DATE_BESIDE = (("0",), ("60",), ("-1",), ("2958466",), ("1", "2958466"), ("0",) * 11, ("1.5",))


@pytest.mark.parametrize("absent", _NO_DATE_BESIDE)
def test_item4_a_count_naming_no_date_tells_nothing_of_the_form(tmp_path: pathlib.Path, absent: "tuple[str, ...]") -> None:
    """The verification of item 4: 999 serials written `%.6f` beside counts read as no value -- Excel's 0 and 60, minus one, a count past 9999-12-31, a moment of 1 January 1900 -- are read as counted dates in their six-place form, and the source and its twin meet it; on `9197903` the lone count made a trimmed form and the column was declined."""
    cells = [f"{45000 + row}.500000" for row in range(999)] + list(absent)
    trip = _described(tmp_path / "declared", cells, "excel-1900")
    block = trip["block"]
    assert isinstance(block, dict) and block["role"] == "datetime", block["remarks"]
    form = block["count_form"]
    assert isinstance(form, dict) and form["places"] == 6 and not form["trimmed"], form
    assert _missed(trip, trip["path"]) == []
    twin = _twin(trip, tmp_path / "twin")
    checked = tmp_path / "twin" / "table-twin.csv"
    assert twin and _missed(trip, checked) == []


@pytest.mark.parametrize("absent", _NO_DATE_BESIDE)
def test_item4_question_q3_asks_beside_a_count_naming_no_date(tmp_path: pathlib.Path, absent: "tuple[str, ...]") -> None:
    """The same columns undeclared: Q3 offers Excel's 1900 system, as it did on `dbb347a`; on `9197903` it asked nothing."""
    cells = [f"{45000 + row}.500000" for row in range(999)] + list(absent)
    said = asking._date_counts_said(_block_of(tmp_path, cells))
    assert said is not None
    offered = [member for member, _first, _last in said.readings]
    assert date_counts.EXCEL_1900 in offered, offered


# -- items 5 and 6: question Q3 -------------------------------------------------------


def test_item5_midnight_counts_written_with_a_decimal_zero_are_asked(tmp_path: pathlib.Path) -> None:
    """`str(315532800 + i * 86400) + ".0"`: days at midnight from 1 January 1980; on `dbb347a` Q3 asked nothing."""
    cells = [str(315532800 + row * 86400) + ".0" for row in range(100)]
    said = asking._date_counts_said(_block_of(tmp_path, cells))
    assert said is not None and said.rule == date_counts.RULE_MIDNIGHT
    offered = [member for member, _first, _last in said.readings]
    assert date_counts.SECONDS_SINCE_1970 in offered and date_counts.SECONDS_SINCE_1960 in offered


@pytest.mark.parametrize("spelled", (lambda count: f"{count}.0", lambda count: f"{count * 100}e-2", lambda count: f"{count}.000"))
def test_item5_the_midnight_rule_reads_a_whole_count_however_its_zeros_are_written(spelled: "object") -> None:
    """Rule B's text half over whole counts written with zeros after the point or an exponent below nought."""
    assert callable(spelled)
    cells = [spelled(315532800 + row * 86400) for row in range(100)]
    assert date_counts._text_holds(cells, date_counts.SECONDS_SINCE_1970, date_counts.RULE_MIDNIGHT, 99)
    for text in cells:
        written = date_counts.written_count(text)
        assert written is not None and date_counts.exact_value(written)[1] == 1, text


def test_item6_a_band_rule_whose_text_fails_lets_the_midnight_rule_run(tmp_path: pathlib.Path) -> None:
    """Unix counts at midnight crossing from nine to ten figures: on `dbb347a` the band held, its widths failed, and Q3 asked nothing."""
    cells = [str((11000 + row) * 86400) for row in range(1000)]
    said = asking._date_counts_said(_block_of(tmp_path, cells))
    assert said is not None and said.rule == date_counts.RULE_MIDNIGHT
    offered = [member for member, _first, _last in said.readings]
    assert date_counts.SECONDS_SINCE_1970 in offered


# -- item 7: bounded before it is built ----------------------------------------------------


def test_item7_an_exponent_past_every_date_builds_no_huge_number() -> None:
    """`1e+9999`: on `dbb347a` a 4,456-byte integer per cell, kept; now a few words, and still no date."""
    for text in ("1e+9999", "-1e+9999", "1e-9999", "9.99e+99999", "1E+0009999"):
        written = date_counts.written_count(text)
        assert written is not None, text
        numerator, denominator = date_counts.exact_value(written)
        assert numerator.bit_length() <= 256 and denominator.bit_length() <= 256, text
    for member in date_counts.MEMBERS:
        written = date_counts.written_count("1e+9999")
        assert written is not None
        assert date_counts.moment_of(member, *date_counts.exact_value(written), date_counts.SECOND) is None


def test_item7_redundant_zeros_after_the_point_are_dropped_before_the_figures_are_read(tmp_path: pathlib.Path) -> None:
    """`45042.` and 4,301 zeros: on `dbb347a` Python's limit on integer text raised ValueError."""
    long = "45042." + "0" * 4301
    written = date_counts.written_count(long)
    assert written is not None
    assert date_counts.exact_value(written) == (45042, 1)
    cells = [f"{45000 + row}" for row in range(200)] + [long]
    trip = _described(tmp_path, cells, "excel-1900")
    block = trip["block"]
    assert isinstance(block, dict) and block["role"] == "datetime"


def test_item7_a_column_of_huge_exponents_keeps_a_small_reading() -> None:
    """Machine-free: 2,000 `1e+9999` cells read under a declaration allocate well under a megabyte."""
    cells = [taxonomy._classify(f"{45000 + row}") for row in range(100)]
    cells += [taxonomy._classify("1e+9999") for _row in range(2000)]
    settings = taxonomy.Settings(forced_date_counts=((taxonomy.COUNTED_HERE, "excel-1900"),))
    tracemalloc.start()
    try:
        taxonomy._counts_read_as_dates(cells, "excel-1900", settings, False)
        _now, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 2_000_000, peak


# -- item 8: the exponent grammar of contract 6.6.2 ---------------------------------


@pytest.mark.parametrize(
    "text,value",
    (
        ("17e+8", (1700000000, 1)),
        ("1704067200e+0", (1704067200, 1)),
        ("17E8", (1700000000, 1)),
        ("0.5e+3", (500, 1)),
        ("45386.5e-1", (453865, 100)),
        ("1.6e+12", (1600000000000, 1)),
    ),
)
def test_item8_the_exponent_reader_takes_the_grammar_of_section_6_6_2(text: str, value: "tuple[int, int]") -> None:
    written = date_counts.written_count(text)
    assert written is not None, text
    numerator, denominator = date_counts.exact_value(written)
    assert numerator * value[1] == value[0] * denominator, text


@pytest.mark.parametrize("text", ("017e+8", "+17e+8", "17e", "17e+", "1.e+8", "17e+8.0", "1 7e+8"))
def test_item8_the_grammar_is_no_wider(text: str) -> None:
    assert date_counts.written_count(text) is None, text


def test_item8_a_column_of_whole_figures_with_an_exponent_honours_its_declaration(tmp_path: pathlib.Path) -> None:
    """Unix seconds written `1704067200e+0`: on `dbb347a` no cell was a count, and the declaration decided nothing."""
    cells = [f"{1704067200 + row * 3607}e+0" for row in range(300)]
    trip = _described(tmp_path, cells, "seconds-since-1970")
    block = trip["block"]
    assert isinstance(block, dict) and block["role"] == "datetime" and block["count_form"] is not None
    _twin(trip, tmp_path / "twin")
    assert _missed(trip, tmp_path / "twin" / "table-twin.csv") == []
    assert _missed(trip, trip["path"]) == []


# -- item 9: an anchor per system, worked out from the calendar ------------------------

# EACH COUNT WORKED OUT BY HAND FROM THE CALENDAR, NOT FROM ANY SYSTEMS TABLE:
# 1 January 2000 is Julian day number 2451545, Excel's well-known serial
# 36526, SAS's 14610 and MUMPS' $H 58074; Unix time 946684800. From those:
# Excel 1904 counts 1,462 days fewer (1900-01-01 to 1904-01-01, with Excel's
# own 29 February 1900); 1960 seconds are 14610 * 86400 = 1262304000; 1970
# days are 946684800 / 86400 = 10957; SPSS's 14 October 1582 is Julian day
# 2299160 (the Gregorian calendar's first day, the 15th, is 2299161), so
# 2000-01-01 is 152385 days on, 13166064000 seconds. Each anchor adds a
# time of day where the system writes one: 12:34:56.789 is 45296.789 s.
ANCHORS = (
    ("excel-1900", "36526.5", "2000-01-01 12:00", date_counts.MINUTE, date_counts.CountForm(1, True, None, False, ".", None)),
    ("excel-1904", "35064.25", "2000-01-01 06:00", date_counts.MINUTE, date_counts.CountForm(2, True, None, False, ".", None)),
    ("days-since-1960", "14610", "2000-01-01", date_counts.DAY, date_counts.CountForm(0, False, None, False, ".", None)),
    ("seconds-since-1960", "1262349296", "2000-01-01 12:34:56", date_counts.SECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("milliseconds-since-1960", "1262349296789", "2000-01-01 12:34:56.789", date_counts.MILLISECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("days-since-1970", "10957", "2000-01-01", date_counts.DAY, date_counts.CountForm(0, False, None, False, ".", None)),
    ("seconds-since-1970", "946730096", "2000-01-01 12:34:56", date_counts.SECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("milliseconds-since-1970", "946730096789", "2000-01-01 12:34:56.789", date_counts.MILLISECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("microseconds-since-1970", "946730096789012", "2000-01-01 12:34:56.789012", date_counts.MICROSECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("nanoseconds-since-1970", "946730096789012345", "2000-01-01 12:34:56.789012345", date_counts.NANOSECOND, date_counts.CountForm(0, False, None, False, ".", None)),
    ("days-since-1840", "58074", "2000-01-01", date_counts.DAY, date_counts.CountForm(0, False, None, False, ".", None)),
    ("seconds-since-1582", "13166109296", "2000-01-01 12:34:56", date_counts.SECOND, date_counts.CountForm(0, False, None, False, ".", None)),
)


def _anchor_holds(member: str, text: str, iso: str, unit: int, form: "date_counts.CountForm") -> bool:
    """Whether the count reads as the moment, and the moment is written as the count."""
    written = date_counts.written_count(text)
    if written is None:
        return False
    moment = date_counts.moment_of(member, *date_counts.exact_value(written), unit)
    if moment is None or date_counts.iso_text(moment, unit, unit) != iso:
        return False
    at = date_counts.moment_of_iso(iso, unit)
    return at is not None and date_counts.written_for(member, at, unit, form) == text


def test_item9_every_system_has_a_reading_and_a_writing_anchor() -> None:
    assert sorted(anchor[0] for anchor in ANCHORS) == sorted(date_counts.MEMBERS)
    for anchor in ANCHORS:
        assert _anchor_holds(*anchor), anchor[0]


@pytest.mark.parametrize("member", date_counts.MEMBERS)
@pytest.mark.parametrize("shift", (-1, 1))
def test_item9_an_epoch_moved_by_one_day_turns_its_anchor_red(
    monkeypatch: pytest.MonkeyPatch, member: str, shift: int
) -> None:
    moved = dict(date_counts.TABLE)
    moved[member] = dataclasses.replace(date_counts.TABLE[member], epoch=date_counts.TABLE[member].epoch + shift)
    monkeypatch.setattr(date_counts, "TABLE", moved)
    for anchor in ANCHORS:
        if anchor[0] == member:
            assert not _anchor_holds(*anchor), member
        else:
            assert _anchor_holds(*anchor), anchor[0]


def test_item9_the_twenty_sixth_file_anchors_spss_seconds_unix_microseconds_and_unix_days() -> None:
    """The oracle's own reading and writing, from its `datetime` epochs, for the three systems that had none."""
    document = json.loads(VECTORS.read_text(encoding="utf-8"))
    readings = {(case["member"], case["text"]): case["answer"] for case in document["readings"].values()}
    spellings = {(case["member"], case["iso"]): case["answer"] for case in document["spellings"].values()}
    assert readings[("seconds-since-1582", "13166109296")] == "2000-01-01 12:34:56"
    assert readings[("microseconds-since-1970", "946730096789012")] == "2000-01-01 12:34:56.789012"
    assert readings[("days-since-1970", "10957")] == "2000-01-01"
    assert spellings[("seconds-since-1582", "2000-01-01 12:34:56")] == "13166109296"
    assert spellings[("microseconds-since-1970", "2000-01-01 12:34:56.789012")] == "946730096789012"
    assert spellings[("days-since-1970", "2000-01-01")] == "10957"
