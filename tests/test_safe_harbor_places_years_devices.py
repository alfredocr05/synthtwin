"""P4-D434 (lane SH2): years of birth, places, device numbers and ZIP codes read as dates.

FOUR LIVE SAFE HARBOR EXPOSURES, measured on lane SH's head 3b1aa03c (lane
E0c's skeptic 1, wave6/E0c-sk1.md items L1 and L2 and its birth_city note;
lane SH's verify 3, wave6/SH-verify3.md 'New shapes'; this lane's
wave6/SH2/base-600.log), each with no question asked:

1. YEARS SHOWING AN AGE OF 90 OR MORE (45 CFR 164.514(b)(2)(i)(C): "all
   elements of dates (including year) indicative of such age"). Birth
   years beside one stray cell, read as a count, printed 1928, 1930 and
   1934 and the twin wrote 26 cells of them at 600 rows; birth dates
   printed years of 1927 to 1933 in their percentiles and tails, their
   twins about 80 cells.
2. PLACES SMALLER THAN A STATE ((B)). A city of birth published its
   cities as levels, the twin writing them on every cell; ZIP codes cut to
   three figures (`021**`) published 7 of 7.
3. DEVICE NUMBERS ((M); the orchestrator's LANE E0c RULINGS 1 (2)). GS1
   device identifiers, lot-level, published 20 of 20 as levels and on
   every twin cell.
4. ZIP CODES ANSWERED AS COUNTED DATES (the orchestrator's LANE SH
   ADDENDUM 7). Five-figure ZIPs beside one `UNKNOWN` answered
   `excel-1900` published 33 of 40 dates naming them one to one; the
   twin wrote 599 of 600 real ZIP numbers.

THE RULE (`taxonomy.safe_harbor_years`, `taxonomy.safe_harbor_hold`). This
release's year, `taxonomy.SAFE_HARBOR_REFERENCE_YEAR`, is the reference
(synthtwin reads no clock): a year of birth at most 90 years before it
shows an age of 90 or more. A column of four-figure years
from 1850 to the reference, judged on its bulk as lane SH's ages are, one
of them that early, is read while its Safe Harbor question is open with
every such year written as the latest of them -- the group "that year or
earlier", as lane SH's top-code writes 90 -- and the key `top_coded_year`;
a column of such years that is also ZIP-shaped stays lane SH's ZIP hold
(a ZIP code that lost its nought reads as a year as well). A column of
dates holding one so early, of ZIP-shaped numbers read as counted dates
by an answer, of GS1 device identifiers, of ZIP codes cut to three
figures, or whose name says it holds a place, is held whole meanwhile
(P4-D401's held block). Each is put lane SH's one question, never a
second; `no` frees it, `yes` holds it for good.

THE GATE: `shapes.SH2_SHAPES` at 600 and 20,000 rows: 0 such values in any
file -- the description, its summary, the questions file, the screen, the
twin's report and both quality reports -- and in the twin, the one
question put; the mutants of wave6/SH2/sh2_mutants.py turn it red. The
600-row cases run here; the 20,000-row ones run in K-S3-64's slow leg
(`kpi_run --slow`), one of them here too (the orchestrator's ruling of
2026-10-26 on the suite's time).

REPAIR 1 (skeptic 1, wave6/SH2-sk1.md, and Codex's review): the shapes
grew by the escapes each measured on 34d847b6 -- place names the word
list missed and county codes top-coded as ages, UDIs spaced, bare, of
HIBCC and beside other codes, years in two figures or beside a word,
early dates hidden among others or written without four figures of a
year, a typed count of days on ZIP codes -- and the reference year is
2027 (the orchestrator's LANE SH2 RULINGS 1 (1)).
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re

import pytest

from synthtwin import asking, cli, profile, reading, taxonomy

import unanswered_identifier_shapes as shapes

_HARBOR = [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]
# A held block's real table misses the census of repetition its held
# block publishes absorbed, as every held block's real table does (plan
# P4-D401; lane SH's `_HELD_REAL_MISSES`).
_HELD_REAL_MISSES = {"distinct.n_distinct_by_occurrences"}
_MISSED = re.compile(r"^\s+(\S+) \[[^\]]+\]: MISSED", re.M)
_YEARS_LINE = "years of birth showing an age over 89: every year up to"


def _check(seen: "dict[str, object]", kind: str, rows: int = 600) -> None:
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    if kind not in shapes.SH2_HELD_LIMITS and not (rows < 20000 and kind in shapes.SH2_HELD_LIMITS_AT_600):
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    # ...and at 600 rows no held twin writes an early year by chance either
    # (a held twin's made-up places equal to real ones by chance are lane
    # ID-ROOM's, counted apart as lane SH's ZIP codes' are).
    assert seen.get("twin_cells_made_up", 0) == 0 or rows >= 20000, seen
    if kind in shapes.SH2_FIRST_ASKED:
        # ...a column of counted birth dates, unanswered, is put the
        # date-count question alone, which offers `identifier` and so holds
        # it (lane SH's ADDENDUM 6); its text names no year before the
        # group (repair 2, the verify's finding 3).
        assert seen["asked"] == [shapes.SH2_FIRST_ASKED[kind]], seen
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        return
    # ONE QUESTION, lane SH's, never a second -- a column of ages whose
    # cells and name state no unit asked its unit inside it (lane SH3's
    # repair, the orchestrator's LANE SH3 RULINGS 2 (1)).
    assert seen["asked"] in ([_HARBOR], [_HARBOR + list(asking.AGE_UNIT_ANSWERS)]), seen
    assert seen["asked"] == [_HARBOR] or kind in shapes.SH2_AGE_TOP_CODED, seen
    assert "THE SAFE HARBOR QUESTION" in f"{seen['screen']}", seen
    if kind in shapes.SH2_AGE_TOP_CODED:
        # ...ages read under lane SH's top-code (the close round: DICOM's
        # `091Y`, placeholders on few rows, a value past 125), published,
        # never held, and the real table meets its own description. THE FIVE
        # AGE TAILS COME HERE, their role a count's (the orchestrator's LANE
        # I4m RULINGS 22 (2)): their one question offers the units beside
        # `yes` and `no` (lane SH3, plan P4-D454) and no `identifier`, so an
        # open age question publishes the column top-coded and never holds
        # it; their offer is `shapes.SH2_AGE_TAILS_ASKED`, not the table of
        # the date-count question that holds its column whole, which the
        # tests-only fix 3355025d had put them in (six cases red on the
        # sealed head's suite, 0 values past 90 and 0 placeholders published
        # or written at 20,000 rows, measured).
        assert seen["role"] != taxonomy.ROLE_IDENTIFIER, seen
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        assert seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED], seen
        assert seen["validate_real_exit"] == 0, seen
    elif kind in shapes.SH2_TOP_CODED:
        assert seen["role"] == shapes.SH2_TOP_CODED[kind], seen
        assert seen["top_coded_year"] == seen["cutoff"], seen
        assert seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED], seen
        assert _YEARS_LINE in f"{seen['summary']}", seen
        # THE REAL TABLE MEETS ITS OWN DESCRIPTION, read under the top-code.
        assert seen["validate_real_exit"] == 0, seen
    else:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        assert seen["top_coded_year"] is None, seen
        assert seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES], seen
        assert set(_MISSED.findall(f"{seen['real_quality']}")) <= _HELD_REAL_MISSES, seen


@pytest.mark.parametrize("kind", shapes.SH2_SHAPES)
def test_no_year_place_or_device_is_published_at_600_rows(tmp_path: pathlib.Path, kind: str) -> None:
    """0 years of an age of 90 or more, places, device numbers or ZIP codes in every file and the twin."""
    _check(shapes.run_sh2(tmp_path, kind, 600), kind)


def test_no_placeholder_of_an_age_is_published_at_20000_rows(tmp_path: pathlib.Path) -> None:
    """The owner's table floor: `998` on 5 cells and `997` on 10 beside ages 18 to 104, at 20,000 rows.

    The orchestrator's LANE SH2 RULINGS 2 (1), from the second verify's
    finding 1 (31359664: both published as tail values, kurtosis 399 and a
    tail distance of 248): every placeholder is set aside whatever its
    rows. Mutant: placeholders set aside only where the floor's rows hold
    them. ONE CASE AT THE FLOOR'S SIZE (the orchestrator's ruling of
    2026-10-26 11:06 on the suite's time: checks at 20,000 rows go into a
    KPI driver or one case, never a parametrized grid); every shape of
    `SH2_SHAPES`, the years beside a stray among them, is run at 600 and
    20,000 rows by K-S3-64's slow leg
    (`tools/measurements/kpi_unanswered_identifiers.py`, `kpi_run --slow`),
    which stops on any shape put other than the one question. ITS ROLE A
    COUNT'S, top-coded at 90, its one question the Safe Harbor one with the
    units beside `yes` and `no` (lane SH3, plan P4-D454): an open age question
    offers no `identifier` and holds nothing (the orchestrator's LANE I4m
    RULINGS 22 (2); measured at 20,000 rows on 2af926ce and on batch 4o's
    sealed head, unanswered: no age past 90 and no placeholder in any file or
    twin cell, no real key).
    """
    _check(shapes.run_sh2(tmp_path, "ages_ph998", 20000), "ages_ph998", 20000)


def test_zip_areas_in_a_column_named_otherwise_are_held(tmp_path: pathlib.Path) -> None:
    """ZIP codes cut to three figures are held by their cells, whatever the column's name (`area3`)."""
    _check(shapes.run_sh2(tmp_path, "area3", 600), "area3")


def test_the_twin_of_a_top_coded_year_column_is_clamped_at_its_year(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Method G7.15: the generator writes the twin of a `top_coded_year` block through the clamp, at the block's year."""
    from synthtwin import contract, generation

    table, _real = shapes.write_sh2_table(tmp_path, "birth_years_stray", 600, shapes.reference_year())
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    loaded = contract.load_profile(f"{tmp_path / 'birth_years_stray_long-profile.json'}")
    real = taxonomy.at_least_the_year_cutoff
    seen: "list[int]" = []

    def clamp(cells: "list[str]", absent: "frozenset[str]", cutoff: int) -> "list[str]":
        seen.extend([cutoff])
        return real(cells, absent, cutoff)

    monkeypatch.setattr(taxonomy, "at_least_the_year_cutoff", clamp)
    generation.generate(loaded, 0)
    assert seen == [taxonomy.year_cutoff(shapes.reference_year())]


@pytest.mark.parametrize("kind", ["birth_years_stray", "dob_iso", "birth_city", "udi_lot", "lat_2dec", "origin"])
def test_no_frees_the_column(tmp_path: pathlib.Path, kind: str) -> None:
    """`no` -- the values name no person, place, date or record -- describes the column as before."""
    seen = shapes.run_sh2(tmp_path, kind, 600, asking.ANSWER_SAFE_HARBOR_NO)
    assert seen["profile_exit"] == 0, seen
    assert seen["asked"] == [], seen
    assert seen["top_coded_year"] is None, seen
    assert seen["role"] != taxonomy.ROLE_IDENTIFIER, seen
    assert int(seen["description_values"]) > 0, seen  # type: ignore[call-overload]


@pytest.mark.parametrize("kind", ["birth_years_stray", "zip_dates"])
def test_yes_holds_the_column_for_good(tmp_path: pathlib.Path, kind: str) -> None:
    """`yes` holds the column whole and closes the question."""
    seen = shapes.run_sh2(tmp_path, kind, 600, asking.ANSWER_SAFE_HARBOR_YES)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    assert seen["asked"] == [], seen
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
    assert seen["description_values"] == 0 and seen["twin_cells"] == 0, seen


@pytest.mark.parametrize("typed", [["--date-count", "zip_dates", "excel-1900"], ["--code", "zip_dates"]])
def test_a_typed_reading_is_no_release(tmp_path: pathlib.Path, typed: "list[str]") -> None:
    """The orchestrator's LANE SH2 RULINGS 1 (5): a reading typed on the command line releases no ZIP hold.

    A typed `--date-count` (the dates the ZIP codes name, one to one) or
    `--code` leaves the column held, the Safe Harbor question put in that
    run, as the same answer in the questions file does (lane SH's
    ADDENDUM 7); only `--identifier` or `no` releases it.
    """
    table, _real = shapes.write_sh2_table(tmp_path, "zip_dates", 600, shapes.reference_year())
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"] + typed) == 0
    document = json.loads((tmp_path / "zip_dates_long-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "zip_dates"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    written = json.loads((tmp_path / "zip_dates_long-questions.json").read_text(encoding="utf-8"))
    asked = [[c["answer"] for c in entry["answers_you_can_give"]]
             for entry in written["asked"] if entry["column"] == "zip_dates"]
    assert asked == [_HARBOR]


# -- the zoo answers truthfully ---------------------------------------------


@pytest.mark.parametrize(("table", "columns"), [
    ("patients", ("dob_iso", "dob_us", "dob_text", "birth_city")),
    ("immunizations", ("udi",)),
])
def test_the_zoos_columns_are_answered_yes_and_stay_held(
    tmp_path: pathlib.Path, table: str, columns: "tuple[str, ...]"
) -> None:
    """The orchestrator's THE ZOO ANSWERS TRUTHFULLY: a birth date, a city of birth and a UDI are answered `yes`.

    Each is put the Safe Harbor question, answered `yes` by the zoo's
    general answers, and held: no city or device number of the real
    table in the description, and the column described as record numbers.
    """
    import health_zoo as zoo

    with shapes.nobody_at_the_keyboard():
        result = zoo.run_table(zoo.table_named(table), tmp_path, 600, 0)
    assert result["steps"]["profile"]["exit"] == 0 and result["steps"]["generate"]["exit"] == 0, result
    for column in columns:
        given = [one["given"] for one in result["asked"] if one["column"] == column]
        assert given == [asking.ANSWER_SAFE_HARBOR_YES], (column, result["asked"])
        assert result["roles"][column] == taxonomy.ROLE_IDENTIFIER, (column, result["roles"])
    described = (tmp_path / f"{table}-profile.json").read_text(encoding="utf-8")
    if table == "patients":
        for city, _weight in zoo.CITIES:
            assert json.dumps(city)[1:-1] not in described and city not in described, city
    else:
        assert "(01)" not in described


# -- the reach, cell by cell ----------------------------------------------


_YEAR = 2026


def _years(*extra: str) -> "list[str]":
    return [f"{year}" for year in range(1925, 2008)] * 3 + list(extra)


@pytest.mark.parametrize(("cells", "reached"), [
    (_years(), True),
    # ...beside a stray, words and placeholders of any share.
    (_years("19"), True),
    (_years(*(["UNKNOWN"] * 400)), True),
    (_years(*(["9999"] * 300), *(["0"] * 300)), True),
    # ...never where no year is 90 years before the reference: admission
    # or fiscal years.
    ([f"{year}" for year in range(2010, 2026)] * 20, False),
    # ...nor where the numbers are amounts that pass through the years.
    ([f"{value}" for value in range(1000, 3000, 7)], False),
    # ...nor a year grouped between thousands.
    ([f"1,{year - 1000:03d}" for year in range(1925, 2008)], False),
    # REPAIR 1 (skeptic 1 item 4): a year beside a word or a mark is a
    # year (`born 1930`, `1930?`, `1925 AD`), as lane SH's `95 years` is an
    # age; and the reach is judged on two in three, so a tenth written in
    # two figures keeps it -- but no more than a third.
    ([f"{year} AD" for year in range(1925, 2008)], True),
    ([f"born {year}" for year in range(1925, 2008)], True),
    (_years(*[f"{year}?" for year in range(1925, 1940)]), True),
    (_years(*[f"{year % 100:02d}" for year in range(1925, 1950)]), True),
    (_years(*[f"{value % 100:02d}" for value in range(0, 130)]), False),
])
def test_the_year_reach_is_judged_on_the_bulk(cells: "list[str]", reached: bool) -> None:
    assert taxonomy.safe_harbor_years(cells, False, frozenset(), 11, _YEAR) is reached


@pytest.mark.parametrize(("cells", "pooled"), [
    (_years("19"), True),
    # ...two-figure years as many as the floor's rows would still show the
    # years pooling hid: the column is held whole instead.
    (_years(*[f"{year % 100:02d}" for year in range(1925, 1936)]), False),
    (_years(*[f"{year % 100:02d}" for year in range(1925, 1935)]), True),
])
def test_the_years_are_pooled_only_beside_fewer_strays_than_the_floor(cells: "list[str]", pooled: bool) -> None:
    assert taxonomy.years_with_few_strays(cells, False, frozenset(), 11, _YEAR) is pooled


def test_the_years_are_written_as_the_latest_year_of_the_group() -> None:
    cutoff = taxonomy.year_cutoff(_YEAR)
    assert cutoff == 1936
    written = taxonomy.year_top_coded_cells(
        ["1925", "1936", "1937", "1925.0", " 1930 ", "19", "1849", "", "born 1930", "1931?", "1925 AD"],
        False, frozenset([""]), cutoff,
    )
    assert written == [
        "1936", "1936", "1937", "1936.0", " 1936 ", "19", "1849", "", "born 1936", "1936?", "1936 AD",
    ]


def test_the_twin_writes_no_year_before_the_group_and_keeps_its_counts() -> None:
    written = taxonomy.at_least_the_year_cutoff(
        ["1925", "1925", "1930", "1936", "1940", "NA"], frozenset(["NA"]), 1936
    )
    assert written[-1] == "NA"
    assert all(int(cell) >= 1936 for cell in written[:-1])
    # ...each different value one value, so each keeps its number of cells.
    assert written[0] == written[1] and written[2] != written[0]
    # ...and a year beside a word is clamped in its own form (repair 1).
    affixed = taxonomy.at_least_the_year_cutoff(["born 1925", "born 1940", "1930?"], frozenset(), 1936)
    assert affixed[1] == "born 1940"
    assert affixed[0][:5] == "born " and int(affixed[0][5:]) >= 1936
    assert affixed[2][-1:] == "?" and int(affixed[2][:4]) >= 1936


@pytest.mark.parametrize(("name", "place"), [
    ("birth_city", True), ("BirthCity", True), ("RES_CITY", True), ("county", True),
    ("street_address", True), ("zip3", True), ("zip", True), ("precinct_code", True),
    ("ethnicity", False), ("capacity", False), ("velocity", False), ("department", False),
    # REPAIR 1: skeptic 1 item 2 (the words, plurals, an address line in capitals,
    # compounds after a known opening) and Codex item 3 (runs of capitals).
    ("birthplace", True), ("place_of_birth", True), ("BIRTHCITY", True), ("hometown", True),
    ("residence", True), ("pob", True), ("cities", True), ("counties", True), ("streets", True),
    ("addresses", True), ("towns", True), ("home_add_line", True), ("mail_addr_line", True),
    ("homeaddress", True), ("USCity", True), ("FIPSCounty", True), ("COUNTYText", True),
    ("CITYText", True), ("census_tract", True),
    ("place_of_service", False), ("urinary_tract_infection", False), ("simplicity", False),
    ("toxicity", False), ("additive_line", False),
    # REPAIR 2 (the verify's finding 1): one word opening with a place word
    # and closing in another, a closing of `PLACE_CLOSINGS` or `of` and a
    # word; `residence` and `postal` openings; the place of service in
    # every spelling stays none, and `placebo` names no place.
    ("placeofbirth", True), ("PLACEOFBIRTH", True), ("cityname", True), ("countyname", True),
    ("townname", True), ("citycode", True), ("countycode", True), ("streetaddress", True),
    ("cityofbirth", True), ("cityofresidence", True), ("countyofresidence", True),
    ("residencecity", True), ("POSTALCD", True), ("cityzip", True), ("birthcityname", True),
    ("PLACE_OF_SVC", False), ("placeofservice", False), ("PLACEOFSVC", False), ("placebo", False),
    ("placement", False), ("townsend", False),
    # THE CLOSE ROUND: the verify 2's finding 2 (the `residence` and
    # `postal` openings, read only through them), and a city beside its
    # state in one word (the orchestrator's LANE SH2 RULINGS 2 (3)).
    ("residencecityname", True), ("postalcitycode", True),
    ("citystate", True), ("cityst", True), ("CityState", True), ("city_state", True),
    ("countystate", True), ("state", False), ("statement", False), ("estate", False),
])
def test_a_place_is_read_from_the_words_of_the_columns_name(name: str, place: bool) -> None:
    assert taxonomy.named_as_a_place(name) is place


@pytest.mark.parametrize(("cell", "device"), [
    ("(01)14620042400034(17)270101(10)LOT516", True),
    ("(01) 14620042400034 (17) 257982 (10) LOT516", True),
    ("01146200424000341725798210LOT516", True),
    ("]C101146200424000342112345", True),
    ("+H724PRD5160/$$3257982LOT516X", True),
    ("+$$3257982LOT516X", True),
    ("=/A99971234567", True),
    # REPAIR 2 (the verify's finding 2): the bare form with spaces.
    ("01 12318051111639 17 260101 10 LOT280", True),
    ("0112318051111639 21 A12", True),
    ("01 12318051111639", False),
    ("01 1231805111163 17 260101", False),
    ("(01)1462004240003", False),
    ("0114620042400034", False),
    ("+POSITIVE", False),
    ("+1 555 1234", False),
    ("1234-5678-90", False),
    ("Boston", False),
])
def test_device_identifiers_of_each_agency_are_read(cell: str, device: bool) -> None:
    """Repair 1, skeptic 1 item 3: GS1 spaced or bare, HIBCC and ICCBBA, read as device identifiers."""
    assert taxonomy._a_device_identifier(cell) is device


def test_device_identifiers_and_zip_areas_are_read_from_their_cells(tmp_path: pathlib.Path) -> None:
    """One cell of the shape holds the column, words set aside whatever their share (repair 1: not two in three)."""
    lines = ["pid,device,area,word"]
    for row in range(300):
        device = "UNKNOWN" if row % 3 == 0 else f"(01){10**13 + row % 20}(17)270101(10)LOT{row % 20}"
        lines += [f"P{row},{device},{('021**', '191**', '000**')[row % 3]},{('Boston', 'Lima')[row % 2]}"]
    path = tmp_path / "t.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    reasons: "dict[str, str]" = {}
    held: "list[str]" = []
    profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True,
                           five_figures=held, ages_held=[], harbor_year=_YEAR, harbor_reasons=reasons)
    assert reasons == {"device": taxonomy.HELD_DEVICES, "area": taxonomy.HELD_ZIP3}, reasons
    assert held == ["device", "area"], held


@pytest.mark.parametrize("share", [1, 30, 70])
def test_a_column_holding_a_device_identifier_beside_other_codes_is_held(share: int) -> None:
    """Whatever their share (LANE E0c RULINGS 1 (2)): 1, 30 and 70 in 100 UDIs beside NDC codes."""
    cells = [
        f"(01){10**13 + row % 7}(17)270101(10)LOT{row % 7}" if row % 100 < share else f"1234-{5600 + row % 9}-10"
        for row in range(600)
    ]
    assert taxonomy._mostly(cells, frozenset(), True)
    assert not taxonomy._mostly([cell for cell in cells if cell[:4] != "(01)"], frozenset(), True)


def _dates_column(details: "dict[str, object]") -> taxonomy.ColumnProfile:
    """A column read as dates, as the reach reads it: its details alone."""
    import types

    return types.SimpleNamespace(details=details)  # type: ignore[return-value]


def test_every_cell_is_read_as_its_column_reads_it() -> None:
    """Codex item 1: one early date among two-figure years read in a declared century, and a compact date."""
    cutoff = taxonomy.year_cutoff(_YEAR)
    cells = ["01/02/30"] + [f"01/{2 + row % 20:02d}/{50 + row % 30:02d}" for row in range(599)]
    layout = "layout {MM}/{DD}/{YY1900}"
    assert taxonomy.dates_showing_an_age_over_89(_dates_column({"format": layout}), cells, frozenset(), cutoff, 11)
    assert not taxonomy.dates_showing_an_age_over_89(
        _dates_column({"format": layout}), cells[1:], frozenset(), cutoff, 11
    )
    compact = ["19300102"] + [f"{1950 + row % 50}0102" for row in range(599)]
    assert taxonomy.dates_showing_an_age_over_89(
        _dates_column({"format": "compact-date"}), compact, frozenset(), cutoff, 11
    )


def test_the_dates_the_block_publishes_are_read_too() -> None:
    """The backstop: an early date the block publishes, though no cell reads under the members it names."""
    cutoff = taxonomy.year_cutoff(_YEAR)
    column = _dates_column({"format": "iso-date", "percentiles": {"min": "1925-03-01"}})
    assert taxonomy.dates_showing_an_age_over_89(column, ["unread"], frozenset(), cutoff, 11)
    assert not taxonomy.dates_showing_an_age_over_89(
        _dates_column({"format": "iso-date"}), ["unread"], frozenset(), cutoff, 11
    )


@pytest.mark.parametrize(("early", "held"), [
    # Skeptic 1 item 7: a day typed for "no date", repeated by the floor's
    # rows and showing an age over 125, is no birth date ...
    (["1899-12-31"] * 40, False),
    (["1901-01-01"] * 40, False),
    # ...but a day held by fewer rows, or one a living person could have
    # been born on, is.
    (["1899-12-31"] * 5, True),
    (["1930-05-05"] * 40, True),
    (["1899-12-31"] * 40 + ["1931-02-02"], True),
])
def test_a_placeholder_day_repeated_by_the_floors_rows_is_set_aside(early: "list[str]", held: bool) -> None:
    cutoff = taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR)
    cells = [f"20{15 + row % 10}-0{1 + row % 9}-1{row % 10}" for row in range(600)] + early
    assert taxonomy.dates_showing_an_age_over_89(
        _dates_column({"format": "iso-date"}), cells, frozenset(), cutoff, 11
    ) is held


def test_the_exposure_count_reads_both_quality_reports() -> None:
    """Codex item 5: a real city in the real table's own quality report alone is counted."""
    texts = {"t-profile.json": "{}", "real-quality": "Boston"}
    assert shapes.sh2_exposure("birth_city", ["Boston"], texts, ["Lima"])["description_values"] == 1


def test_the_library_keeps_its_bytes_without_the_commands_year(tmp_path: pathlib.Path) -> None:
    """The year top-code is the command's rule, as lane SH's top-code is: the library's default describes as before."""
    path, _real = shapes.write_sh2_table(tmp_path, "birth_years_stray", 600, _YEAR)
    table = reading.read_table(f"{path}")
    plain = profile.build_document(table, taxonomy.Settings(), [])
    assert all("top_coded_year" not in block for block in plain["columns"])  # type: ignore[union-attr]
    coded = profile.build_document(table, taxonomy.Settings(), [], top_code=True, harbor_year=_YEAR)
    blocks = [block for block in coded["columns"] if block["name"] == "birth_years_stray"]  # type: ignore[union-attr, index]
    assert blocks[0]["top_coded_year"] == 1936


def test_the_reference_year_is_not_behind_the_calendar() -> None:
    """THE TRIPWIRE: the release's reference year is this year or later, or a year of an age of 90 is published.

    synthtwin reads no clock, so the year the Safe Harbor years are
    judged against is written in `taxonomy.SAFE_HARBOR_REFERENCE_YEAR`;
    on the first day of a later year this goes red until it is raised.
    It is 2027 or later (the orchestrator's LANE SH2 RULINGS 1 (1): the
    release ships in December 2026 and is used through 2027, and a
    person born in 1937 turns 90 in 2027), so this goes red on 1 January
    2028 first.
    """
    import datetime

    assert taxonomy.SAFE_HARBOR_REFERENCE_YEAR >= datetime.date.today().year
    assert taxonomy.SAFE_HARBOR_REFERENCE_YEAR >= 2027
    assert taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR) == taxonomy.SAFE_HARBOR_REFERENCE_YEAR - 90


def test_the_question_is_lane_shs_sentence() -> None:
    """One question, the owner's Z1 sentence, naming no value of the column."""
    for reason in (asking.BECAUSE_SAFE_HARBOR_YEARS, asking.BECAUSE_SAFE_HARBOR_DATES,
                   asking.BECAUSE_SAFE_HARBOR_PLACES, asking.BECAUSE_SAFE_HARBOR_ZIP3,
                   asking.BECAUSE_SAFE_HARBOR_DEVICES, asking.BECAUSE_SAFE_HARBOR_ZIP_DATES,
                   asking.BECAUSE_SAFE_HARBOR_YEARS_HELD, asking.BECAUSE_SAFE_HARBOR_YEARS_BESIDE):
        question = asking._safe_harbor_question("v", taxonomy.ROLE_COUNT, reason, 1936)
        assert asking.safe_harbor_sentence("v") in question.shape
        assert [choice.answer for choice in question.choices] == _HARBOR
    # ...and a shape a share of the cells takes is said of some of them
    # (Codex item 6), never of the whole column.
    for reason in (asking.BECAUSE_SAFE_HARBOR_ZIP3, asking.BECAUSE_SAFE_HARBOR_DEVICES):
        assert "some of its values are" in asking._safe_harbor_question("v", taxonomy.ROLE_COUNT, reason, 1936).shape


# -- repair 2: the years a question names, the ages' placeholders, the oracle --


@pytest.mark.parametrize(("year", "said"), [
    (1930, "1937 or earlier"), (1937, "1937 or earlier"), (1938, "1938"), (2005, "2005"),
])
def test_an_edge_year_showing_an_age_over_89_is_said_as_the_group(year: int, said: str) -> None:
    """The verify's finding 3: Q3's text and NF114 wrote the year of a counted column's published edge.

    Excel serials of births of 1930 to 2005, held as record numbers,
    printed "they run from 1930 to 2005" in the questions file and on the
    screen while their questions were open. The question, its choices
    and the sentence write such a year as the group.
    """
    assert taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR) == 1937
    assert taxonomy.edge_year_said(year) == said
    shown = asking._date_count_shape("", asking.DateCountsSaid("fixed-width-days", (), (("excel-1900", year, 2005),)))
    assert f"they run from {said} to 2005" in shown
    choices = asking._date_count_choices(taxonomy.ROLE_COUNT, 11, asking.DateCountsSaid(
        "fixed-width-days", (), (("excel-1900", year, 2005),)))
    assert any(f"runs from {said} to 2005" in choice.means for choice in choices)
    sentence = taxonomy.rendered(taxonomy.REMARK_READ_AS_COUNTED_DATES, ("excel-1900", year, 2005))
    assert f"runs from {said} to 2005" in sentence


# ...a share of rows (`tails.high.percent`) is no age, but a percentile is one (close round 2: the walk had read
# `percentiles.p95` as a share and passed it over).
_AGE_FACT = re.compile(r"count|styles|\.n_|rows|missing|occurrences|people|_cells|distinct|width|length|places|figures|percent(?!ile)")


def _age_facts_over_90(node: object, path: str, found: "list[tuple[str, object]]") -> None:
    """Every number of a block above 90 whose key is no count, width or share (the verify's walk)."""
    if isinstance(node, dict):
        for key in node:
            _age_facts_over_90(node[key], f"{path}.{key}", found)
    elif isinstance(node, list):
        for place, one in enumerate(node):
            _age_facts_over_90(one, f"{path}[{place}]", found)
    elif isinstance(node, (int, float)) and not isinstance(node, bool) and node > 90 and not _AGE_FACT.search(path):
        found += [(path, node)]
    elif isinstance(node, str) and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", node) and float(node) > 90 \
            and not _AGE_FACT.search(path):
        found += [(path, node)]


@pytest.mark.parametrize("placeholder", ["999", "998", "-1"])
def test_an_age_placeholder_is_set_aside_before_any_rung(tmp_path: pathlib.Path, placeholder: str) -> None:
    """The orchestrator's LANE SH2 ADDENDUM 1: no fact of a top-coded age column above 90.

    Ages 18 to 104 beside a tenth of `999` (or `998`, or `-1`) published
    p99 and the mean between 90 and 999 (measured at 20,000 rows on
    e38f7d4e: 200 cells, p99 99.09; 1,000, the mean 106.8 and p95
    135.45, the twin 180 cells between them). The placeholder is set
    aside, written blank, before any rung is read; the twin writes it
    blank; both the twin and the table validate.
    """
    import random

    draw = random.Random(434)
    cells = [placeholder if row % 10 == 0 else f"{draw.randint(18, 104)}" for row in range(600)]
    path = tmp_path / "ages.csv"
    path.write_text("\n".join(["pid,age"] + [f"P{row:04d},{cell}" for row, cell in enumerate(cells)]) + "\n",
                    encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{path}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        assert cli.main(["generate", f"{tmp_path / 'ages-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{tmp_path / 'ages-profile.json'}", "--twin",
                         f"{tmp_path / 'ages-twin.csv'}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        real = tmp_path / "real"
        real.mkdir()
        assert cli.main(["validate", f"{tmp_path / 'ages-profile.json'}", "--twin", f"{path}",
                         "--out-dir", f"{real}", "--replace"]) == 0
    document = json.loads((tmp_path / "ages-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "age"][0]
    assert block["top_coded"] == 90
    assert block["n_missing"] == 60, block["n_missing"]
    found: "list[tuple[str, object]]" = []
    _age_facts_over_90(block, "age", found)
    assert found == [], found
    twin = shapes._csv_column(tmp_path / "ages-twin.csv", 1)
    assert [cell for cell in twin if cell and 90 < float(cell)] == []
    assert len([cell for cell in twin if cell == ""]) == 60


def test_the_age_placeholders_are_the_reachs_own() -> None:
    """Which cells are set aside: the reach's placeholders, never an age, a word or a rare stray."""
    cells = ["45", "95", "999", "-1", "-99", "998", "998", "130", "UNK", "", "0"]
    aside = taxonomy.age_placeholders_set_aside(cells, False, frozenset({""}), 2)
    assert aside == ["45", "95", "", "", "", "", "", "130", "UNK", "", "0"]


def test_a_value_outside_the_ages_written_as_no_placeholder_is_kept() -> None:
    """A value past 125 that many rows hold is set aside only when it is written as a placeholder is.

    The whole suite on 5cf9f3b9: a workbook's site codes `12`, `45`,
    `101`, `230` and `7` (the reach's false alarm, `230` on a fifth of
    the rows) and the measurements `+100.25`, `200.25` and `300.25` had
    `230`, `200.25` and `300.25` written blank, so their twins lost those
    cells. Mutant: every value outside 0 to 125 held by the floor's rows
    set aside, as repair 2 first built it.
    """
    cells = ["101", "230", "230", "45", "888", "888", "-88", "-88", "200.25", "200.25", "9998", "9998"]
    aside = taxonomy.age_placeholders_set_aside(cells, False, frozenset({""}), 2)
    assert aside == ["101", "230", "230", "45", "", "", "", "", "200.25", "200.25", "", ""]


def _oracle() -> object:
    import importlib.util

    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_safe_harbor", where)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_AGE_TWINS = [
    ["95", "91", "90", "89", "95", "130", "", "NA"],
    ["95 years", "103 years", "90 years", "88 years"],
    ["097", "064", "093", "103"],
    ["+95", "92.5", "92.50", "90.0", "89.9", "91.25"],
    [" 95 ", "95", "96", "97", "98", "99", "100", "90", "89"],
    ["95", "-1", "999", "91", "12"],
    ["91.1234567", "92.123", "125", "125.5"],
]
_YEAR_TWINS = [
    ["1930", "1925", "1950", "born 1930", "1930?", "1937", "1936.0", "+1920", "19", "NA"],
    ["1920", "1920", "1921", "1938", "1939", "1940"],
    ["c. 1931", "1931 AD", "1849", "2001", "1937.00", " 1936 "],
]


def test_the_oracle_writes_the_top_codes_twins_as_the_product_does() -> None:
    """A-P4-59 for methods G7.14 and G7.15 (batch 4l's debt OWES 7 (b)): the oracle's own reading of each step.

    `tools/reference/make_generation_reference_vectors.py` writes both
    steps from the method's words alone (`safe_harbor_ages_twin`,
    `safe_harbor_years_twin`); the product's `at_most_the_top_code` and
    `at_least_the_year_cutoff` write the same cells, on the cases above
    and on two hundred columns drawn in each of the forms the generator
    writes.
    """
    import random

    oracle = _oracle()
    draw = random.Random(4347)
    ages = list(_AGE_TWINS)
    years = list(_YEAR_TWINS)
    for _column in range(200):
        cells: "list[str]" = []
        for _cell in range(draw.randint(1, 30)):
            value = draw.choice([f"{draw.randint(0, 130)}", f"{round(draw.uniform(85, 126), draw.randint(1, 3))}",
                                 # ...the close round: past 125, below nought, and
                                 # a unit letter against it (`1100M`, `126O`).
                                 f"{draw.randint(-20, 999)}"])
            cells += [draw.choice(["", "0", "+"]) + value + draw.choice(["", "", " yrs", "Y", "M", "W", "D", "O"])
                      if draw.random() < 0.3 else value]
        ages += [cells]
        born = [f"{draw.randint(1880, 2026)}" for _cell in range(draw.randint(1, 30))]
        years += [[draw.choice(["", "born ", "", ""]) + one + draw.choice(["", "?", "", ".0"]) for one in born]]
    for cells in ages:
        assert taxonomy.at_most_the_top_code(cells, frozenset({"NA"})) == \
            oracle.safe_harbor_ages_twin(cells, frozenset({"NA"})), cells  # type: ignore[attr-defined]
    for cells in years:
        assert taxonomy.at_least_the_year_cutoff(cells, frozenset({"NA"}), 1937) == \
            oracle.safe_harbor_years_twin(cells, frozenset({"NA"}), 1937), cells  # type: ignore[attr-defined]


# -- the close round: coordinates, places beside their states, DICOM ages, ages' tails --


@pytest.mark.parametrize(("name", "coordinate"), [
    ("home_lat", True), ("home_lon", True), ("lat", True), ("LAT", True), ("Latitude", True),
    ("longitude", True), ("lng", True), ("geo", True), ("gps_lat", True), ("x_coord", True),
    ("latlong", True), ("homelat", True), ("latLong", True), ("geolocation", True), ("lat_2dec", True),
    # ...the orchestrator's LANE SH2 ADDENDUM 3: never `long` alone, `plateau`
    # or `flat`, nor a word that only opens with one.
    ("long", False), ("plateau", False), ("flat", False), ("latency", False), ("lateral", False),
    ("longitudinal", False), ("coordinator", False), ("geography", False), ("length_long", False),
    ("va_pair", False),
])
def test_a_coordinate_is_read_from_the_words_of_the_columns_name(name: str, coordinate: bool) -> None:
    assert taxonomy.named_as_a_coordinate(name) is coordinate


def test_a_pair_of_coordinates_is_read_from_their_cells() -> None:
    """ADDENDUM 3: decimals of three places or more, one of two inside [-90, 90]; never two shares inside [-1, 1]."""
    latitude = taxonomy.coordinate_reading([f"-33.{k:04d}" for k in range(300)], False, frozenset())
    longitude = taxonomy.coordinate_reading([f"151.{k:04d}" for k in range(300)], False, frozenset())
    shares = taxonomy.coordinate_reading([f"0.{k:03d}" for k in range(300)], False, frozenset())
    assert (latitude, longitude, shares) == (
        taxonomy.COORDINATE_LATITUDE, taxonomy.COORDINATE_LONGITUDE, taxonomy.COORDINATE_NEAR_NOUGHT,
    )
    # ...two decimals, words of any share aside, and numbers past 180 are none.
    assert taxonomy.coordinate_reading([f"-33.{k % 100:02d}" for k in range(300)], False, frozenset()) == ""
    assert taxonomy.coordinate_reading(["UNKNOWN"] * 400 + [f"-33.{k:04d}" for k in range(300)],
                                       False, frozenset()) == taxonomy.COORDINATE_LATITUDE
    assert taxonomy.coordinate_reading([f"{181 + k}.123" for k in range(300)], False, frozenset()) == ""
    held = taxonomy.coordinates_held
    assert held([("a", latitude), ("b", longitude), ("c", "")]) == ["a", "b"]
    assert held([("a", latitude), ("b", latitude)]) == ["a", "b"]
    assert held([("a", latitude), ("b", shares)]) == ["a", "b"]
    # ...never a lone column, two longitudes, or two shares.
    assert held([("a", latitude)]) == []
    assert held([("a", longitude), ("b", longitude)]) == []
    assert held([("a", shares), ("b", shares)]) == []


@pytest.mark.parametrize(("cell", "beside"), [
    ("Lake City, MN", True), ("Union City, NJ 07087", True), ("St. Louis, MO 63101-1234", True),
    ("O'Fallon, MO", True), ("Lake City,MN", True),
    ("Lake City, Mn", False), ("Boston", False), ("Lake City, MN 5504", False), ("12 Main St, ZZ", False),
    ("Smith, John", False),
])
def test_a_place_beside_its_state_is_read_from_a_cell(cell: str, beside: bool) -> None:
    """The orchestrator's LANE SH2 RULINGS 2 (3): a place, a comma and a state's two-letter code."""
    assert taxonomy._a_place_beside_its_state(cell) is beside


def test_an_age_with_its_unit_letter_is_read_in_years() -> None:
    """ADDENDUM 4: DICOM's `090Y` is no code padded with zeros, and `120M` is ten years."""
    assert taxonomy._safe_harbor_kind("095Y", False)[0] == taxonomy._AGE_ABOVE
    assert taxonomy._safe_harbor_kind("045Y", False)[0] == taxonomy._AGE_IN
    assert taxonomy._safe_harbor_kind("120M", False) == (taxonomy._AGE_IN, taxonomy._ZIP_OTHER, 10.0)
    cells = [f"{age:03d}Y" for age in range(18, 105)] * 3 + ["006M", "003W", "010D"]
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), 11, True) == taxonomy.SAFE_HARBOR_AGES
    # ...a code padded with zeros, no letter against it, is still none.
    assert taxonomy.safe_harbor_reach([f"{age:03d}" for age in range(18, 105)] * 3, False, frozenset(), 11,
                                      True) == ""
    assert taxonomy.top_coded_cells(["104Y", "095Y", "045Y", "120M", "1100M", "006M"]) == [
        "090Y", "090Y", "045Y", "120M", "1080M", "006M",
    ]


def test_a_value_past_125_of_an_age_column_is_written_at_the_top_code() -> None:
    """RULINGS 2 (2): `130` may be a real age mistyped; a placeholder is set aside, a made-up label kept."""
    assert taxonomy.top_coded_cells(["130", "95", "130.5", "+140", "998", "999", "-1", "126O", "45"]) == [
        "90", "90", "90.0", "+90", "998", "999", "-1", "126O", "45",
    ]
    aside = taxonomy.age_placeholders_set_aside(["998", "997", "997", "45", "126O", "777Q"], False, frozenset(), 11)
    assert aside == ["", "", "", "45", "126O", "777Q"]


@pytest.mark.parametrize("cells", [
    # ...site codes `230` on a fifth of the rows beside `101`, and the
    # measurements `200.25` and `300.25` beside `100.25`: reached as they
    # were before the close round, false alarms the answer `no` frees (the
    # orchestrator's LANE SH2 RULINGS 4 (1), correcting RULINGS 2 (2)'s
    # parenthesis); in the column the top-code reads every value 90.
    ["12", "45", "101", "230", "7"] * 100,
    ["+100.25", "200.25", "300.25"] * 50,
])
def test_columns_of_other_values_past_125_are_reached_as_false_alarms(cells: "list[str]") -> None:
    """Mutant: f9bdf41a's stray rule (no value but a placeholder set aside): neither is reached."""
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES
    coded = taxonomy.top_coded_cells(cells)
    assert [cell for cell in coded if float(cell) > taxonomy.TOP_CODE] == []


@pytest.mark.parametrize(("value", "cells"), [("130", 1200), ("150", 1500), ("200", 1200)])
def test_ages_beside_a_value_past_125_on_many_rows_are_reached(value: str, cells: int) -> None:
    """RULINGS 4 (1): up to three values past 125 that the floor's rows repeat are set aside whatever their share.

    The close check's finding 1 on f9bdf41a, at 20,000 rows: ages 18 to
    104 beside `130` on 1,200 cells (or `150` on 1,500, `200` on 1,200)
    read as no age column -- more than one stray in twenty -- were put no
    question and published every age above 89 (4,150 and 4,300 twin cells
    above 90). Reached, the value is read 90 like every age above 89; the
    whole command's outputs are counted at 600 rows above (`ages_130_many`
    and the others of `SH2_SHAPES`) and at 20,000 rows in K-S3-64's slow
    leg. Mutant: f9bdf41a's stray rule, red on all three.
    """
    import random

    draw = random.Random(4344)
    column = [f"{draw.randint(18, 104)}" for _row in range(20000)]
    for spot in draw.sample(range(20000), cells):
        column[spot] = value
    assert taxonomy.safe_harbor_reach(column, False, frozenset({""}), 11) == taxonomy.SAFE_HARBOR_AGES
    read = taxonomy.top_coded_cells(taxonomy.age_placeholders_set_aside(column, False, frozenset({""}), 11))
    assert [cell for cell in read if cell and float(cell) > taxonomy.TOP_CODE] == []
    assert read.count("90") == sum(1 for cell in column if int(cell) >= taxonomy.TOP_CODE)


def test_ages_beside_placeholders_of_any_rows_are_reached() -> None:
    """RULINGS 2 (1): `998` on 5 cells and `997` on 10, and `-88` on a third, are set aside whatever their rows.

    The orchestrator's LANE SH2 RULINGS 4 (2): ten placeholders on 5
    cells each, 50 of 650 together -- more than one stray in twenty -- are
    set aside too; red on the floor-rows mutant (a placeholder set aside
    only where the floor's rows hold it, the close check's r1r), as the
    first case alone is not.
    """
    ages = [f"{18 + k % 87}" for k in range(600)]
    assert taxonomy.safe_harbor_reach(ages + ["998"] * 5 + ["997"] * 10, False, frozenset(), 11) == \
        taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(ages + ["-88"] * 300, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES
    marks = ["998", "997", "996", "995", "994", "993", "888", "777", "-88", "-77"]
    assert taxonomy.safe_harbor_reach(ages + marks * 5, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.age_placeholders_set_aside(ages + marks * 5, False, frozenset(), 11)[600:] == [""] * 50


def _rounds_put(folder: pathlib.Path, table: pathlib.Path, column: str) -> "list[list[list[str]]]":
    """Profile in rounds, `keep` to a question offering it and `yes` to the Safe Harbor question; what each round put."""
    stem = table.name[: -len(".csv")]
    put: "list[list[list[str]]]" = []
    arguments: "list[str]" = []
    with shapes.nobody_at_the_keyboard():
        for number in range(5):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"] + arguments) == 0
            written = json.loads((folder / f"{stem}-questions.json").read_text(encoding="utf-8"))
            mine = [entry for entry in written["asked"] if entry["column"] == column]
            put += [[[choice["answer"] for choice in entry["answers_you_can_give"]] for entry in mine]]
            given = 0
            for entry in mine:
                offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
                if sorted(offered) == _HARBOR:
                    entry["your_answer"] = asking.ANSWER_SAFE_HARBOR_YES
                    given += 1
                elif asking.ANSWER_KEEP in offered:
                    entry["your_answer"] = asking.ANSWER_KEEP
                    given += 1
            if not given:
                break
            answers = folder / f"answers{number}.json"
            answers.write_text(json.dumps(written), encoding="utf-8", newline="\n")
            arguments = ["--answers", f"{answers}"]
    return put


@pytest.mark.parametrize("kind", ["dicom_age", "zipplus4_30", "zip52_unknown40"])
def test_a_column_answered_keep_and_then_yes_is_asked_nothing_again(tmp_path: pathlib.Path, kind: str) -> None:
    """RULINGS 4 (3), G3: the person question answered `keep` is not put again once the Safe Harbor question is answered.

    The close check's finding 3 on f9bdf41a: DICOM ages (and ZIP codes,
    measured here) answered `keep` and then `yes` were put the person
    question once more in every later round, under `read_as_now: keep`,
    though the file's `answered_before` section kept the answer. Round 0
    puts the person question, round 1 the Safe Harbor question alone, and
    round 2 nothing: both answers stand. Mutant: the question not dropped
    once the Safe Harbor question is answered (rounds 2 to 4 put it).
    """
    if kind in shapes.SH2_SHAPES:
        table, _real = shapes.write_sh2_table(tmp_path, kind, 600, shapes.reference_year())
    else:
        table, _real = shapes.write_safe_harbor_table(tmp_path, kind, 600)
    put = _rounds_put(tmp_path, table, kind)
    assert len(put) == 3, put
    assert asking.ANSWER_IDENTIFIER in put[0][0] and asking.ANSWER_KEEP in put[0][0], put
    assert put[1] == [_HARBOR] and put[2] == [], put
    written = json.loads((tmp_path / f"{kind}_long-questions.json").read_text(encoding="utf-8"))
    kept = sorted(f"{entry['your_answer']}" for entry in written[asking.ANSWERED_BEFORE] if entry["column"] == kind)
    assert kept == [asking.ANSWER_KEEP, asking.ANSWER_SAFE_HARBOR_YES], kept
