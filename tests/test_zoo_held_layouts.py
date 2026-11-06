"""P4-D442 (lane HB): held and unanswered columns written in their own valid layouts.

WHAT WAS MEASURED ON THE BASE (lane ID-ROOM's READY head daed36fb, `tests/held_layouts_shapes.py`
at 20,000 rows, wave6/HB/base20k.log and base600.log). Record numbers beside `-1` or `-99` took
226.8 s and 216.7 s to generate against 4.2 s for the same column with those cells blank (the
layout search read 4,096 fillings of a layout of figures alone for every slot of another band);
a telephone number opening `+` was written `!             !AAAAAAAAAAAAAAAG` and its twin missed
its own census (validate exit 3); 14,002, 13,959 and 14,090 twin UIDs of three columns with no
root were off the UID grammar; the walk wrote 20,000 real persons as 13,684 (`pad_split`), a
number beside its `.0` as 19,220 numbers, a dotted pad as 19,669 merged keys and 19,284 numbers,
`P` beside `P-` as 12,707 of 17,222; birth dates read as free text or as labels beside
`UNKNOWN` wrote 20,000 and 15,948 cells no date reader takes (`00/00/0000`, `0000-00-00`), a column
of two dates five; and a two-figure `PatientStudyKey` beside `-1`, read by value as an age is,
wrote 20,000 of 20,000 twin cells as real keys.

THE RULES (method G9.6, G9.6b and G8.3; plan P4-D442). The identifier walk offers a group its next
spelling where one names a walk person written before it -- its merged key or its value read as a
number -- and jumps that layout's walk by the golden section of its room; a slot of another band
passes over a layout of figures alone in one step, its walk moved as the search would have moved
it; a published `+` before a telephone number's figures is the source's and is filled; a rootless
UID column's twin is written in the UID grammar; a published form of a date is filled with valid
dates; a member of one merged identity spelled on its own shares only its own identity's key and
number; and a column whose NAME says it is a key is asked the person question whatever its width.

Each case is red on the mutant its docstring names (wave6/HB/mutants.log). Every check at 20,000
rows is one case a writer; the rest of the hunt is K-HZ-13's (tools/measurements/kpi_held_layouts.py,
kpi_run --slow).
"""

from __future__ import annotations

import collections
import contextlib
import csv
import dataclasses
import io
import json
import pathlib
import random
import re
import types

import pytest

from synthtwin import asking, cli, contract, errors, generation, parsing, profile, taxonomy, validation

import held_layouts_shapes as hunt
import identifier_room_shapes as room
import unanswered_identifier_shapes as held_shapes


def _run(tmp_path: pathlib.Path, name: str, n: int) -> "dict[str, object]":
    return hunt.run(tmp_path / f"{name}-{n}", name, n)


# -- (C) speed: the layout search beside a negative placeholder ------------------------------


def test_a_figures_layout_is_passed_over_by_a_slot_of_another_band() -> None:
    """Every filling of a plain layout of `%` and `!` alone is figures, so only the figures band
    wears it. Mutant: the predicate answering False (every slot reads the whole ceiling)."""
    plain = parsing.LAYOUT_PLAIN
    assert generation._figures_alone_outside_their_band("code", "%%%%%%%", plain)
    assert generation._figures_alone_outside_their_band("wide", "!!%%%%%", plain)
    assert not generation._figures_alone_outside_their_band("digits", "%%%%%%%", plain)
    assert not generation._figures_alone_outside_their_band("code", "%%%-%%%", plain)
    assert not generation._figures_alone_outside_their_band("code", "%%%%", parsing.LAYOUT_HEX_LOWER)


def test_the_search_beside_minus_one_reads_no_ceiling_and_moves_no_byte(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Record numbers beside `-1`, 600 rows: the walk asks a few fillings a slot, not 4,096 (1,153,063
    on the base), and writes the twin byte for byte as the full search does. Mutants: the pass-over
    withdrawn (the calls), and the pass-over not moving the layout's walk (the bytes)."""
    folder = tmp_path / "t"
    folder.mkdir()
    header, rows, _column, _typed = hunt.table_of("keys_beside_minus_one", 600)
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    asked = [0]
    fits = generation._fits_its_slot

    def counted(*arguments: object) -> bool:
        asked[0] += 1
        return fits(*arguments)  # type: ignore[arg-type]

    twins: "list[bytes]" = []
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"]) == 0
        for skip in (True, False):
            if not skip:
                monkeypatch.setattr(generation, "_figures_alone_outside_their_band", lambda *_a: False)
            else:
                monkeypatch.setattr(generation, "_fits_its_slot", counted)
            assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                             "--seed", "0", "--replace"]) == 0
            twins += [(folder / "t-twin.csv").read_bytes()]
            if skip:
                monkeypatch.setattr(generation, "_fits_its_slot", fits)
    assert asked[0] < 20 * 600, asked[0]
    assert twins[0] == twins[1]


def test_the_date_reader_answers_figures_alone_as_every_member_would() -> None:
    """Figures alone are a date only at eight figures (`compact-date`): the shortcut answers as the
    twenty members do, asked one by one, on every length from one to fourteen. Mutant: the shortcut
    reading eight figures too (`20240317` is a date)."""
    import random

    draw = random.Random(442)
    for length in range(1, 15):
        for _ in range(300):
            text = "".join(draw.choice("0123456789") for _place in range(length))
            slow = any(parsing.parse_datetime(text, name) is not None for name in parsing.DATE_FORMATS)
            assert generation._reads_as_a_date(text) == slow, text
    assert generation._reads_as_a_date("20240317")


# -- (B) persons: two real persons are never written as one ----------------------------------


def _readings(cell: str) -> "tuple[str, str | None]":
    return parsing.merged_key(cell), hunt.as_a_number(cell)


def test_the_walk_writes_as_many_persons_as_the_real_column_holds(tmp_path: pathlib.Path) -> None:
    """A number written `1000000.0`, `001000001` and `1000002` by turns, 20,000 different (ID-ROOM's
    verify 2's `x_dotted_pad`): the twin holds 20,000 merged keys and 20,000 numbers (19,669 and
    19,284 on the base), 0 cells equal to or merging with a real one, and validates. Mutants: the
    walk's refusal of a spelling naming another person withdrawn; the refused layout's walk not
    jumping (a run of refusals as long as the other layout's walk, some taken at the last try)."""
    seen = _run(tmp_path, "x_dotted_pad", 20_000)
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    before, after = seen["persons"]  # type: ignore[misc]
    assert after == before == {"merged_keys": 20_000, "numbers": 20_000}, (before, after)
    assert seen["equal"] == 0 and seen["merged"] == 0


def test_the_pass_writes_no_two_walk_persons_as_one_beside_a_merging_walk(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ID-ROOM's verify 2, item 1, at 20,000 rows, read per walk person: given the base's walk (its
    refusal withdrawn, so it writes a number beside its `.0` as one person 780 times), every twin
    merged key and every twin number holds cells of ONE walk merged key and ONE walk number (79
    numbers held two on daed36fb, each member spelled on its own and claimed only afterwards), and no
    twin cell equals or merges with a real one. Mutant: `_respelled_one_by_one` claiming its members
    only after all are spelled, sharing nothing."""
    monkeypatch.setattr(generation, "_names_another_person", lambda _spelling, _persons, _read: False)
    seen = room.walk_and_pass(tmp_path, "number_beside_its_decimal", 20_000)
    real, twin, walk = seen["real"], seen["twin"], seen["walk"]
    by_key: "dict[str, set[str]]" = collections.defaultdict(set)
    by_number: "dict[str, set[str | None]]" = collections.defaultdict(set)
    for place in range(len(twin)):
        if not twin[place].strip():
            continue
        key, number = _readings(twin[place])
        by_key[key].add(parsing.merged_key(walk[place]))
        if number is not None:
            by_number[number].add(hunt.as_a_number(walk[place]))
    assert sum(1 for held in by_key.values() if len(held) > 1) == 0
    assert sum(1 for held in by_number.values() if len(held) > 1) == 0
    assert room.equal_cells(real, twin) == 0 and room.merged_equal_cells(real, twin) == 0


def test_one_merged_identity_moves_together_on_its_own_spellings() -> None:
    """`0123` and `123`, one merged person: the together search writes the new merged key in each
    one's own spelling, place for place (`_on_its_spelling`, ID-ROOM's verify 2, item 2), so it finds
    a filling both wear. Mutant: that line withdrawn (each written as the leading value's filling,
    the two take one spelling and nothing fits together)."""
    facts = contract.IdentifierFacts(
        min_length=3, max_length=4, all_whole_numbers=True, n_all_digits=3, n_code_alphabet=3,
        n_distinct_by_occurrences={"1": 3}, layout_forms={"!%%%": 1, "%%%": 2}, layout_prefixes={},
        layout_exclusions={"!%%%": ("!%%9",), "%%%": ("%%9",), parsing.EXCLUSION_SPILL: ("%%%%%",)},
    )
    together = generation._respelled_together(generation._off_the_real_room(facts, ()), ["0123", "123"])
    assert together is not None
    assert parsing.merged_key(together["0123"]) == parsing.merged_key(together["123"]), together
    assert parsing.layout_form(together["0123"], parsing.LAYOUT_PLAIN) == "!%%%", together


def test_a_member_spelled_on_its_own_shares_only_what_is_its_own() -> None:
    """The per-member fallback (ID-ROOM's verify 2, item 1): `0447240` and `447240`, one merged key
    and one number, may share the new key and number they take; a third value naming the same
    merged key as another number (`447240.0` read as 447,240 beside `44724.0`... here `4472400`)
    may not take a number another member holds. Mutant: the sharing withdrawn (the walk's one person
    splits) or every claim deferred (two numbers become one)."""
    facts = contract.IdentifierFacts(
        min_length=6, max_length=7, all_whole_numbers=True, n_all_digits=3, n_code_alphabet=3,
        n_distinct_by_occurrences={"1": 3}, layout_forms={"!%%%%%%": 1, "%%%%%%": 1, "%%%%%%%": 1},
        layout_prefixes={},
        layout_exclusions={"!%%%%%%": ("!%%%%%9",), "%%%%%%": ("%%%%%9",), "%%%%%%%": ("%%%%%%9",),
                           parsing.EXCLUSION_SPILL: ("%%%%%%%%",)},
    )
    column = types.SimpleNamespace(name="key", time_grain=None)
    room_ = generation._off_the_real_room(facts, ())
    for cell in ("0447240", "447240", "4472400"):
        generation._claimed(room_, cell)
    one = generation._respelled_one_by_one(room_, column, ["0447240", "447240"])  # type: ignore[arg-type]
    assert parsing.merged_key(one["0447240"]) == parsing.merged_key(one["447240"]), one
    assert hunt.as_a_number(one["0447240"]) == hunt.as_a_number(one["447240"]), one
    other = generation._respelled_one_by_one(room_, column, ["4472400"])  # type: ignore[arg-type]
    numbers = {hunt.as_a_number(cell) for cell in list(one.values()) + list(other.values())}
    assert len(numbers) == 2, (one, other)


def test_a_fold_partner_spelled_on_its_own_keeps_its_partners_fold() -> None:
    """The per-member fallback with a fold collision (G9.3): `Abcde` and `ABCDE`, one person in two
    cases, both moved, keep one folded identity (spelled apart, caps-2000's names wrote 119 folded
    identities against a published 118 on the lane's first head). Mutant: the partner spelled on its
    own (its partner's fold is claimed, so it takes another)."""
    facts = contract.IdentifierFacts(
        min_length=5, max_length=5, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=2,
        n_distinct_by_occurrences={"1": 2}, layout_forms={"@&&&&": 1, "@@@@@": 1}, layout_prefixes={},
        layout_exclusions={"@&&&&": ("@&&&z",), "@@@@@": ("@@@@Z",), parsing.EXCLUSION_SPILL: ("@@@@@@",)},
    )
    column = types.SimpleNamespace(name="key", time_grain=None)
    room_ = generation._off_the_real_room(facts, ())
    for cell in ("Abcde", "ABCDE"):
        generation._claimed(room_, cell)
    one = generation._respelled_one_by_one(room_, column, ["Abcde", "ABCDE"])  # type: ignore[arg-type]
    assert parsing.folded(one["Abcde"]) == parsing.folded(one["ABCDE"]), one
    assert one["Abcde"] != one["ABCDE"] and one["ABCDE"] == one["ABCDE"].upper(), one


# -- (A) published forms on held twins: the `+` of a telephone number, the UID grammar ---------


def test_a_telephone_number_opening_plus_keeps_its_plus(tmp_path: pathlib.Path) -> None:
    """K-S3-64's `phone_plus` (44 patients, `+1-201-555-0123`), held, 20,000 rows: every twin cell
    opens `+` and the twin meets its own census (exit 3 on the base). Mutant: `_dials_a_number`
    answering False (the opening refused as a formula's)."""
    seen = _run(tmp_path, "phone_plus", 20_000)
    assert seen["role"] == "identifier"
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert all(cell[:1] == "+" for cell in seen["twin"] if cell.strip())  # type: ignore[union-attr]
    assert seen["equal"] == 0 and seen["merged"] == 0
    assert generation._dials_a_number("+%-%%%-%%%-%%%%") and generation._dials_a_number("+%% %% %%%%%%%%")
    assert not generation._dials_a_number("+%%%") and not generation._dials_a_number("=%-%%%-%%%-%%%%")
    assert not generation._dials_a_number("+@%-%%%-%%%%")


@pytest.mark.parametrize(("name", "n"), [("uid_ge_and_siemens", 600), ("uid_study_held", 600),
                                         ("uid_hl7_and_dicom", 20_000)])
def test_a_rootless_uid_is_written_in_the_uid_grammar(tmp_path: pathlib.Path, name: str, n: int) -> None:
    """Two roots side by side (declared) and a held study UID: no twin cell off `[012](\\.(0|[1-9]\\d*))+`
    or past 64 characters (13,959 of 20,000 on the base for HL7 beside DICOM; the pool's 9 cells at
    600 rows written as no UID at all), validate exit 0, no cell equal to or merging with a real one.
    Mutants: the grammar step withdrawn (`_rootless_uids` False); the pool's values left as the walk
    wrote them (`_a_uid_in_place_of` answering "")."""
    seen = _run(tmp_path, name, n)
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["off_the_grammar"] == 0
    assert seen["equal"] == 0 and seen["merged"] == 0


# -- (D) dates held or read as words -------------------------------------------------------------


def test_a_published_form_of_a_date_is_filled_with_valid_dates() -> None:
    """`_date_filled_form`: the first steps of `%%%%-%%-%%` and `%%/%%/%%%%` are valid dates, the
    second valid month first and day first; a stamp's form and a form of three fields of other widths
    are not dates. Mutant: the form's dates not written (None)."""
    for form, layouts in (("%%%%-%%-%%", ("%Y-%m-%d",)), ("%%/%%/%%%%", ("%m/%d/%Y", "%d/%m/%Y")),
                          ("%/%/%%%%", ("%m/%d/%Y", "%d/%m/%Y")), ("%%%%.%%.%%", ("%Y.%m.%d",))):
        for step in range(400):
            written = generation._date_filled_form(form, step)
            assert written is not None, (form, step)
            for layout in layouts:
                assert hunt._is_a_date(written, (layout,)), (form, written, layout)
    assert generation._date_filled_form("%%%%-%%-%% %%:%%", 0) is None
    assert generation._date_filled_form("%%%-%%-%%", 0) is None
    assert generation._date_filled_form("%%%%%%%%", 0) is None


def test_two_figure_years_month_words_and_dated_figures_are_filled_with_valid_dates() -> None:
    """Skeptic 1, item 4: a year of two figures last (`%%/%%/%%`: both other fields 1 to 12, the year one
    every pivot from 20 to 69 reads inside 1940 to 2019), a month word (`%%-@&&-%%%%`, `%%@@@%%%%`, in
    the form's case) and, where the column's other forms are dates', eight figures alone, a month beside
    a year and a year alone. Mutants: each form left unread (None)."""
    for form, dated, layouts in (
        ("%%/%%/%%", False, ("%m/%d/%y", "%d/%m/%y")), ("%/%/%%", False, ("%m/%d/%y",)),
        ("%%-@@@-%%%%", False, ("%d-%b-%Y",)), ("%%-@&&-%%", False, ("%d-%b-%y",)),
        ("%%@@@%%%%", False, ("%d%b%Y",)), ("%%%%%%%%", True, ("%Y%m%d",)),
        ("%%/%%%%", True, ("%m/%Y",)), ("%%%%-%%", True, ("%Y-%m",)), ("%%%%", True, ("%Y",)),
    ):
        for step in range(min(500, generation._date_form_dates(form, dated))):
            written = generation._date_filled_form(form, step, dated)
            assert written is not None, (form, step)
            for layout in layouts:
                assert hunt._is_a_date(written, (layout,)), (form, written, layout)
        assert generation._date_form_dates(form, dated) > 0, form
    for short in ("%%/%%/%%", "%%-@&&-%%"):
        for step in range(generation._date_form_dates(short)):
            year = int(f"{generation._date_filled_form(short, step)}"[-2:])
            for pivot in (20, 30, 50, 69):
                full = 2000 + year if year < pivot else 1900 + year
                assert 1940 <= full <= 2019, (short, year, pivot)
    assert generation._date_filled_form("%%-&&&-%%%%", 3) == generation._date_filled_form("%%-@@@-%%%%", 3).lower()
    assert generation._date_filled_form("%%%%%%%%", 0) is None and generation._date_filled_form("%%%%", 0) is None


def test_a_month_beside_a_year_in_free_text_beside_dates_is_a_date(tmp_path: pathlib.Path) -> None:
    """Dates of a diagnosis in ISO beside `MM/YYYY` (the zoo's `dx_date` at 600 rows: 166 cells `27/3614`
    on the lane's first head), 600 rows through the internal switch, read as free text: every cell of a
    date's shape a valid date of the source's layouts. Mutant: the free-text walk's context dropped for
    its forms (`%%/%%%%` filled with free figures)."""
    seen = _run(tmp_path, "dates_beside_month_years", 600)
    assert seen["role"] == "free_text", seen["role"]
    assert seen["invalid_dates"] == 0


def test_a_label_beside_dates_in_a_month_and_year_form_is_a_date() -> None:
    """`_made_up_label` told the column's forms hold a date's (`dated`): its stand-ins of `%%/%%%%` are month
    and year (dates of a diagnosis beside `MM/YYYY` read as labels at 20,000 rows wrote 3,583 cells such as
    `27/5480` on the repair's first head; `K-HZ-13`'s `dates_beside_month_years`). Mutant: the label walk's
    context dropped."""
    used: "dict[str, int]" = {}
    owners: "dict[str, str]" = {}
    walked: "dict[str, int]" = {}
    written = [generation._made_up_label(0, used, owners, "%%/%%%%", (), walked, dated=True)[1] for _ in range(1_500)]
    assert len(set(written)) == 1_500
    assert all(hunt._is_a_date(cell, ("%m/%Y",)) for cell in written), [c for c in written if not hunt._is_a_date(c, ("%m/%Y",))][:3]


def test_a_dated_record_number_column_past_its_forms_dates_comes_round(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_dates_in_their_layouts`, a column of dates read as record numbers whose walk wrote more values in a
    layout than its form holds different dates: `%%%%-%-%%` steps 44,640 times round 43,720 dates of 1940 to
    2099 (a day past its month's last is that last day), and 44,000 values each take a date not written
    before while one is left, then come round, and the pass ends -- the 200,000-row birth dates, whose walk put more values in
    the ISO layout than its 29,220 different dates, did not on the repair's first head. Mutant: the search
    for a date not written before unbounded (it asks the supply for ever: stopped here at 200,000 asks)."""
    facts = contract.IdentifierFacts(
        min_length=8, max_length=9, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=44_000,
        n_distinct_by_occurrences={"1": 44_000}, layout_forms={"%%%%-%-%%": 44_000},
        layout_prefixes={}, layout_exclusions={},
    )
    column = types.SimpleNamespace(name="dx_date", time_grain=None)
    walked = [f"{1000 + k // 9}-{1 + k % 9}-{10 + k % 20}" for k in range(44_000)]
    asked = [0]
    filled = generation._date_filled_form

    def counted(form: str, step: int, dated: bool = False) -> "str | None":
        asked[0] += 1
        assert asked[0] < 200_000, "the date pass does not end"
        return filled(form, step, dated)

    monkeypatch.setattr(generation, "_date_filled_form", counted)
    # ...two runs of eighty years (1940 to 2099), so the column holds more values than the form's dates.
    monkeypatch.setattr(generation, "_DATE_FORM_PHASES", 2)
    written = generation._dates_in_their_layouts(column, facts, walked, list(walked), ())  # type: ignore[arg-type]
    assert all(hunt._is_a_date(cell, ("%Y-%m-%d",)) for cell in written)
    assert len(set(written)) == generation._date_form_dates("%%%%-%-%%") - 920, len(set(written))


def _dated_table(n: int) -> "tuple[list[str], list[list[str]]]":
    """Five date columns side by side: ISO beside `MM/DD/YY`, `YYYYMMDD` and `DD-Mon-YYYY` (read as free
    text), dates beside words read as labels, and birth dates in two layouts declared record numbers."""
    columns = {
        "birth_short": hunt._days_beside(n, "%m/%d/%y"),
        "birth_compact": hunt._days_beside(n, "%Y%m%d"),
        "birth_words": hunt._days_beside(n, "%d-%b-%Y"),
        "visit_date": hunt._dates_beside_words(n),
        "birth_held": hunt._days(n, 1, 0.0, True),
    }
    header = list(columns) + ["value"]
    rows = [[columns[name][row] for name in columns] + [f"{row % 97}.5"] for row in range(n)]
    return header, rows


def test_dates_in_every_writer_are_valid_dates_at_the_floor(tmp_path: pathlib.Path) -> None:
    """One table of 20,000 rows (skeptic 1, item 4; LANE HB RULINGS 1, item (17); the statistics skeptic's
    item 2): free text beside two-figure years, eight figures and month words, labels beside words, and
    birth dates declared record numbers -- the identifier walk's date layouts -- write no date-shaped cell
    that is no valid date of the source's layouts (10,089, 10,060, 10,116, 1,882 and every cell before),
    and the twin validates. Mutants: the free-text walk's context dropped (`dated` False: `10000000`), the
    month word unread, `_dates_in_their_layouts` handing the pass's cells back (`9571-94-98`)."""
    folder = tmp_path / "dated"
    folder.mkdir()
    header, rows = _dated_table(20_000)
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace",
                         "--identifier", "birth_held"]) == 0
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"]) == 0
        validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"])
    # ...every obligation met but one form's census on the free text of two lengths, where G9.5's packing
    # writes the published longest length's carrier in no form (P4-D442's stated limit (l), as on the
    # lane's first head: `@-------`).
    report = (folder / "t-twin-quality.txt").read_text("utf-8").splitlines()
    missed = set()
    for at in range(len(report)):
        if report[at].endswith(": MISSED"):
            named = [line.strip() for line in report[:at] if line.startswith("'")][-1]
            missed.add((named, report[at].split(" [")[0].strip()))
    assert validated in (0, 3) and missed <= {("'birth_short'", "forms.published.%%/%%/%%")}, missed
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    layouts = {"birth_short": ("%Y-%m-%d", "%m/%d/%y"), "birth_compact": ("%Y-%m-%d", "%Y%m%d"),
               "birth_words": ("%Y-%m-%d", "%d-%b-%Y"), "visit_date": ("%Y-%m-%d",),
               "birth_held": ("%Y-%m-%d", "%m/%d/%Y")}
    roles = {block["name"]: block["role"] for block in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]}
    assert roles["birth_held"] == "identifier"
    for name, shapes in layouts.items():
        place = header.index(name)
        cells = [row[place] for row in twin[1:] if row[place].strip()]
        invalid = [cell for cell in cells if hunt._a_date_shape(cell) and not hunt._is_a_date(cell, shapes)]
        # ...the carrier of the published longest length of a free text of numbers beside dates is written
        # as a number of that length, no date (stated limit (l)).
        assert len(invalid) <= (1 if name == "birth_compact" else 0), (name, roles[name], len(invalid), invalid[:3])


@pytest.mark.parametrize("name", ["dob_unknown", "two_dates"])
def test_a_date_held_back_as_a_label_is_written_as_a_valid_date(tmp_path: pathlib.Path, name: str) -> None:
    """Birth dates beside 20 % `UNKNOWN`, read as labels, and a column of two dates read binary whose
    rare date is held back, 600 rows (the internal smoke): no cell `0000-00-00` or `group-N` where a
    date stood. Mutant: the label walk's stand-in test ignoring `dated` (`group-317`, `group-1`)."""
    seen = _run(tmp_path, name, 600)
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    layouts = hunt.DATE_LAYOUTS[name]
    assert all(hunt._is_a_date(cell, layouts) for cell in seen["twin"]  # type: ignore[union-attr]
               if cell.strip() and cell != "UNKNOWN")


# -- (E) a key by its name -------------------------------------------------------------------------


def test_a_column_named_as_a_key_is_read_whole_word_by_word() -> None:
    """`named_as_a_key`: words of the name, cut as lane SH2 cuts a place's, from a closed list; a number
    word after an opening, apart or joined (`patient_num`, `med_rec_no`, `PERSON_NBR`, `recno`; skeptic
    1, item 3), and `fin` only as the last word or before a number word (`fin_class` is a financial
    class's codes). Mutants: an ending read instead of a word (`paid` and `turkey` would name a key);
    the number words withdrawn; `fin` read anywhere."""
    for name in ("PatientStudyKey", "PAT_KEY", "patid", "EncounterKey", "person_key", "CSN", "Id",
                 "patient_num", "med_rec_no", "PERSON_NBR", "recno", "acct_num", "record_no",
                 "AccountNumber", "visit_nr", "FIN", "encounter_fin", "FIN_NBR"):
        assert asking.named_as_a_key(name), name
    for name in ("paid", "valid_flag", "turkey", "monkey", "age", "identity_score", "kidney",
                 "fin_class", "number_of_visits", "case_count", "nominal", "renumbered", "no_show"):
        assert not asking.named_as_a_key(name), name
    assert asking.key_name_words("COUNTYText_ID") == ["county", "text", "id"]


def test_a_two_value_flag_named_as_a_key_is_no_register() -> None:
    """P4-D341's own premise (skeptic 1, item 1 (c)): `subject_id` holding `0` and `1` on 1,196 rows is a
    flag, not a register of persons, so the name asks nothing; three values or more are asked. Mutant:
    `NAMED_KEY_LEAST_VALUES` at two."""
    assert not asking._named_key_puts("subject_id", ["0", "1"] * 598, "binary")
    assert asking._named_key_puts("subject_id", ["10", "11", "12"] * 400, "count")


def test_a_two_figure_key_named_as_a_key_is_held(tmp_path: pathlib.Path) -> None:
    """GG's skeptic 1, item 2: sixty `PatientStudyKey` values 10 to 69 beside `-1` on 2 % of rows,
    20,000 rows: asked the person question, held, no twin cell a real key (20,000 of 20,000 on the
    base, read as a measurement). Mutant: `_named_key_puts` answering False."""
    seen = _run(tmp_path, "durable_two_figures", 20_000)
    assert seen["role"] == "identifier", seen["role"]
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    real = {cell for cell in seen["real"] if cell != "-1"}  # type: ignore[union-attr]
    assert sum(1 for cell in seen["twin"] if cell in real) == 0  # type: ignore[union-attr]
    questions = json.loads((tmp_path / "durable_two_figures-20000" / "t-questions.json").read_text("utf-8"))
    assert [entry["column"] for entry in questions["asked"]] == ["PatientStudyKey"]


def test_keys_named_by_number_words_are_held(tmp_path: pathlib.Path) -> None:
    """Skeptic 1, item 3: two-figure keys 10 to 69 beside `-1` named `patient_num`, `med_rec_no` and
    `PERSON_NBR`, one table of 20,000 rows: each asked the person question, held, no twin cell a real key
    (20,000 of 20,000 real on the base, read as a measurement). Mutant: the number words withdrawn."""
    import random

    names = ("patient_num", "med_rec_no", "PERSON_NBR")
    draw = random.Random(442)
    header = list(names) + ["value"]
    rows = [["-1" if draw.random() < 0.02 else f"{10 + draw.randrange(60)}" for _name in names]
            + [f"{draw.uniform(3, 150):.1f}"] for _row in range(20_000)]
    folder = tmp_path / "named"
    folder.mkdir()
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"]) == 0
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                         "--out-dir", f"{folder}", "--replace"]) == 0
    blocks = {block["name"]: block for block in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]}
    asked = [entry["column"] for entry in json.loads((folder / "t-questions.json").read_text("utf-8"))["asked"]]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for place in range(len(names)):
        assert blocks[names[place]]["role"] == "identifier", names[place]
        assert names[place] in asked, names[place]
        real = {row[place] for row in rows if row[place] != "-1"}
        assert sum(1 for row in twin[1:] if row[place] in real) == 0, names[place]


# -- (12): keys between commas, each kept off the real ----------------------------------------------


def test_a_list_layout_is_kept_off_the_real_key_by_key() -> None:
    """`taxonomy._list_exclusion_of`: a layout of keys between commas writes each key's opening as the
    shortest no real key of its width opens with (`9%%%%%%,9%%%%%%`; `99%%%%%` where every figure opens
    a real key, LANE HB RULINGS 3), an opening 1 to 10 keys hold ending its size; none where the fillings
    left in a field are fewer than the layout's values; a group of a number's thousands is no list; the keys of
    cells marked `;` and `|` are counted. Mutants: `a_list_layout` False; the floor's stop withdrawn; one
    figure alone (`_list_opening_of` reads size 1 only)."""
    firsts = taxonomy._list_key_firsts(["1000001,1000002", "1003999", "R100001;R100002"])
    assert firsts[7]["1"] == 3 and firsts[7]["1003"] == 1 and firsts[6]["1"] == 2
    assert firsts[6]["100002"] == 1 and "2" not in firsts[6]
    assert taxonomy.a_list_layout("%%%%%%%,%%%%%%%") and taxonomy.a_list_layout("@%%%%%%,@%%%%%%")
    assert not taxonomy.a_list_layout("%,%%%,%%%") and not taxonomy.a_list_layout("%%%%%%%")
    # ...a key of seven beside real keys of six opens with `9` once more, so no run of six inside it is
    # a real one (Codex's review of lane HB, item 8); keys of seven alone open with `9` once.
    assert taxonomy._list_exclusion_of("%%%%%%%,%%%%%%%", firsts, 11) == "99%%%%%,99%%%%%"
    alone = taxonomy._list_key_firsts(["1000001,1000002", "1003999"])
    assert taxonomy._list_exclusion_of("%%%%%%%,%%%%%%%", alone, 11) == "9%%%%%%,9%%%%%%"
    assert taxonomy._list_exclusion_of("@%%%%%%, @%%%%%%", {6: {"1": 40}}, 11) == "@9%%%%%, @9%%%%%"
    assert taxonomy._list_exclusion_of("%%%%%%%,%%%%%%%", {7: {"9": 40, "8": 3}}, 11) == "99%%%%%,99%%%%%"
    assert taxonomy._list_exclusion_of("%%%%%%%,%%%%%%%", {7: {"9": 40, "8": 30}}, 11) == "7%%%%%%,7%%%%%%"
    assert taxonomy.one_list_key("@%%%%%%") and taxonomy.one_list_key("%%%%%%%")
    assert not taxonomy.one_list_key("%%%%") and not taxonomy.one_list_key("@%%%%%%,@%%%%%%")
    every = {opening: 40 for opening in "123456789"}
    every.update({"99": 40, "98": 12, "97": 3})
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%%", {6: every}, 11) == "@999%%%,@999%%%"
    # ...and where no opening leaves room, the noughts (rule 22), or nothing where those leave none either.
    assert taxonomy._list_exclusion_of("@%%,@%%", {2: every}, 11) == "@09,@09"
    assert taxonomy._list_exclusion_of("@%%,@%%", {2: {"9": 40}}, 11, 10) == "@8%,@8%"
    assert taxonomy._list_exclusion_of("@%%,@%%", {2: {"9": 40}}, 11, 11) == "@09,@09"
    assert taxonomy._list_exclusion_of("%%,%%", {2: {"9": 40}}, 11, 1_000) == ""
    # ...each width's openings counted only as deep as a field may be written out (a million keys: one).
    assert taxonomy._list_deepest("@%%%%%%,@%%%%%%", 2_188) == 2 and taxonomy._list_deepest("%%%%%%%", 1_000_000) == 1
    assert taxonomy._list_key_firsts(["1234567"], 2) == {7: {"1": 1, "12": 1}}


def test_a_column_of_keys_between_commas_is_asked_and_held() -> None:
    """`asking._keys_between_commas`: letters (at most three) then five figures, or letters then four, one
    to three a cell; a list in one cell in ten; a word in at most one cell in three; the keys repeating.
    Mutant: the route withdrawn (nothing asked: the free-text walk writes the register back)."""
    assert asking._a_list_key("1000123") and asking._a_list_key("R100000") and asking._a_list_key("AB1234")
    assert not asking._a_list_key("1234") and not asking._a_list_key("E11.9")
    assert not asking._a_list_key("ABCD12345")
    cells = hunt._comma_lists(2_000, False)
    assert asking._keys_between_commas(cells * 10, "free_text") > 0
    assert asking._keys_between_commas(cells, "free_text") == 0  # 2,000 cells: 4,000 keys do not repeat
    assert asking._keys_between_commas(hunt._register_lists(600), "categorical") == 40
    assert asking._keys_between_commas(hunt._register_lists(600), "count") == 0
    worded = ["OTHER" if place % 2 else cell for place, cell in enumerate(hunt._register_lists(600))]
    assert asking._keys_between_commas(worded, "free_text") == 0


def test_register_lists_are_held_and_write_no_real_key(tmp_path: pathlib.Path) -> None:
    """HX4's register lists as Codex built them (`R100000` to `R100039`; 40 singles, 240 pairs, 320
    triples), 600 rows through the internal switch: read as free text on this base, the twin wrote
    `R100000` twice (P4-D442's stated limit (c) on the build); now asked, held and written key by key off
    the real. Mutant: the route withdrawn."""
    seen = _run(tmp_path, "register_lists", 600)
    assert seen["role"] == "identifier", seen["role"]
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["real_keys_in_lists"] == 0


def test_list_members_are_kept_off_every_real_key_on_any_draw(tmp_path: pathlib.Path) -> None:
    """LANE HB RULINGS 3: lane HX4's `reglistmixR` (40 keys `R` and six figures from the whole room, one
    to three a cell, the mark `;`, `,` or `|` cell by cell), 20,000 rows, held as record numbers: every
    figure 1 to 9 opens a real key, so the one-figure scan finds none and the list cells were written as
    the spill, whose run could open with a real key's figures; now each list layout of the description
    carries the shortest opening no real key of its width opens with (`@99%%%%,@99%%%%`), read here off
    the real cells by the gate's own count, so no member of any filling equals or carries a real key on
    any draw. The twin itself at seeds 0 and 1 is K-HZ-13's (kpi_run --slow: 0 cells carrying, 0 equal;
    about 470 processor seconds a seed to generate, over the suite's three minutes). Mutants: the full
    room (`_list_exclusion_of` handing the layout back); one figure alone (`_list_opening_of` size 1)."""
    header, rows, column, typed = hunt.table_of("reglistmixR", 20_000)
    folder = tmp_path / "mixed"
    folder.mkdir()
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"] + list(typed)) == 0
    block = [one for one in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]
             if one["name"] == column][0]
    assert block["role"] == "identifier"
    # ...every opening of every real key, by its merged width, counted once a key and read once a cell.
    openings: "dict[int, set[str]]" = collections.defaultdict(set)
    for row in rows:
        for token in hunt._list_tokens(row[header.index(column)]):
            figures = token.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz").lstrip("0")
            openings[len(figures)].update(figures[:size] for size in range(1, len(figures) + 1))
    assert len({one for one in openings[6] if len(one) == 1}) == 9  # every figure opens a real key
    listed = [layout for layout in block["layout_forms"] if taxonomy.a_list_layout(layout)]
    assert len(listed) == 2, block["layout_forms"]
    # ...and the layout of one key, a list of one, kept off by its opening too: never by a letter alone.
    listed += [layout for layout in block["layout_forms"] if taxonomy.one_list_key(layout)]
    assert len(listed) == 3, block["layout_forms"]
    for layout in listed:
        excluded = block["layout_exclusions"].get(layout, "")
        assert excluded and excluded != layout, (layout, block["layout_exclusions"])
        for field in excluded.split(","):
            opening = field.lstrip("@").split("%")[0]
            assert opening and opening not in openings[len(field) - 1], (layout, excluded)


# -- repair 2: Codex's review of lane HB, items 1 to 10 ---------------------------------------


def _uid_facts(layout: str, excluded: str, spill: str) -> contract.IdentifierFacts:
    return contract.IdentifierFacts(
        min_length=len(layout), max_length=len(spill) - 1, all_whole_numbers=False, n_all_digits=0,
        n_code_alphabet=0, n_distinct_by_occurrences={"1": 4}, layout_forms={layout: 4}, layout_prefixes={},
        layout_exclusions={layout: (excluded,), parsing.EXCLUSION_SPILL: (spill,)},
    )


def test_a_rootless_uid_column_is_not_written_as_dates() -> None:
    """Codex item 1: UIDs `0.1.1940` to `2.9.2039` wear `%.%.%%%%`, which a date can wear too; the date
    pass wrote them as dates (one a real UID, 75 of 100 off the UID grammar). A column the final pass
    reads as rootless UIDs is left as that pass wrote it. Mutant: `_rootless_uid_layouts` not asked."""
    facts = _uid_facts("%.%.%%%%", "%.%.9%%%", "%%%%%%%%%")
    column = types.SimpleNamespace(name="uid", time_grain=None)
    cells = ["0.1.9940", "1.2.9941", " 2.3.9942", "0.4.9943"]
    assert generation._dates_in_their_layouts(column, facts, cells, cells, ()) == cells  # type: ignore[arg-type]


def test_a_uids_spelling_partners_stay_one_identity() -> None:
    """Codex item 3: `v` and `v ` (and a value in two cases) are one identity; written in the UID grammar
    one by one, the second took a UID of its own (120 folded identities became 206). Each partner now
    takes its first partner's new core with its own spaces, a space more where the core is taken. Mutant:
    the partners withdrawn (each spelled on its own)."""
    facts = _uid_facts("%.%%.%%%", "%.9%.%%%", "%%%%%%%%%")
    column = types.SimpleNamespace(name="uid", time_grain=None)
    cells = ["5.12.345", "5.12.345 ", "7.20.111", " 7.20.111", "AbCdEfGhIj", "abcdefghij"]
    written, _remarks = generation._spelled_off_the_real(column, facts, cells, ())  # type: ignore[arg-type]
    assert len(set(written)) == len(set(cells)), written
    assert len({parsing.folded(cell) for cell in written}) == 3, written
    assert all(parsing.is_a_uid(parsing.trimmed(cell)) for cell in written), written


def test_values_written_wider_are_counted_on_what_is_written() -> None:
    """Codex item 10: the grammar's own spellings came after the count of values written wider, so a
    value of no layout written as a wider UID went uncounted (2 reported against 47). Mutant: the count
    taken before the grammar."""
    facts = _uid_facts("%.%%.%%%", "%.9%.%%%", "%%%%%%%%%")
    column = types.SimpleNamespace(name="uid", time_grain=None)
    cells = ["1.20.300", "ABCDEFGHIJ"]
    written, remarks = generation._spelled_off_the_real(column, facts, cells, ())  # type: ignore[arg-type]
    wider = sum(1 for before, after in zip(cells, written) if len(after) > len(before))
    assert wider >= 1, written
    assert remarks and remarks[0].held.endswith(f"{wider} of them written wider"), (remarks, written)


def test_the_case_forms_of_a_month_word_take_dates_of_their_own_folds() -> None:
    """Codex item 4: 100 dates `DD-MON-YYYY` and 100 `DD-Mon-YYYY`, read as record numbers: each case form
    started the same dates, so 200 values folded as 100. The forms step one walk and no date is taken
    whose fold was written; a fold partner takes its partner's date in its own case. Mutant: each case
    form walking its own dates and the dates taken read raw."""
    layouts = {"%%-@@@-%%%%": 100, "%%-@&&-%%%%": 100}
    facts = contract.IdentifierFacts(
        min_length=11, max_length=11, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=200,
        n_distinct_by_occurrences={"1": 200}, layout_forms=layouts, layout_prefixes={},
        layout_exclusions={"%%-@@@-%%%%": ("%%-@@@-9%%%",), "%%-@&&-%%%%": ("%%-@&&-9%%%",),
                           parsing.EXCLUSION_SPILL: ("%%%%%%%%%%%%",)},
    )
    column = types.SimpleNamespace(name="dx", time_grain=None)
    walked = [f"{k % 28 + 1:02d}-ABC-{1000 + k}" for k in range(100)]
    walked += [f"{k % 28 + 1:02d}-Abc-{2000 + k}" for k in range(100)]
    walked += ["01-abc-1000"]
    out = generation._dates_in_their_layouts(column, facts, walked, walked, ())  # type: ignore[arg-type]
    assert len({parsing.folded(cell) for cell in out[:200]}) == 200
    assert parsing.folded(out[200]) == parsing.folded(out[0]) and out[200] != out[0], (out[0], out[200])
    assert all(hunt._is_a_date(cell, ("%d-%b-%Y",)) for cell in out)


def test_a_date_of_the_date_pass_is_never_a_spelling_read_as_absent() -> None:
    """Codex item 7: `1940-01-01` declared missing beside a column of ISO dates read as record numbers;
    the date pass wrote it once as a date (present 120 -> 119); every value is still written as a valid
    date. Mutant: the replacement not asked against the holes while the form's dates are walked."""
    facts = contract.IdentifierFacts(
        min_length=10, max_length=10, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=0,
        n_distinct_by_occurrences={"1": 50}, layout_forms={"%%%%-%%-%%": 50}, layout_prefixes={},
        layout_exclusions={"%%%%-%%-%%": ("9%%%-%%-%%",), parsing.EXCLUSION_SPILL: ("%%%%%%%%%%%",)},
    )
    column = types.SimpleNamespace(name="id", time_grain=None)
    walked = [f"2{k:03d}-13-45" for k in range(50)]
    holes = ("1940-01-01", f"{generation._date_filled_form('%%%%-%%-%%', 1, True)}")
    out = generation._dates_in_their_layouts(column, facts, walked, walked, holes)  # type: ignore[arg-type]
    assert not set(out) & set(holes), sorted(set(out) & set(holes))
    assert len(set(out)) == 50 and all(hunt._is_a_date(cell, ("%Y-%m-%d",)) for cell in out), out[:4]


def test_a_year_last_date_form_past_both_readings_goes_on_to_later_years() -> None:
    """Codex item 5: past the 11,520 dates both readings take, `%%/%%/%%%%` wrote its second field 13 to 28,
    valid month first only (13,000 dates `%d/%m/%Y` beside `pending`: 1,480 stand-ins such as `03/25/1956`).
    A year of four figures goes on to the next eighty years; a year of two figures keeps its month-first
    dates (stated limit). Mutant: the month-first dates for four-figure years."""
    for step in range(11_400, 11_800):
        written = f"{generation._date_filled_form('%%/%%/%%%%', step)}"
        assert hunt._is_a_date(written, ("%d/%m/%Y",)) and hunt._is_a_date(written, ("%m/%d/%Y",)), (step, written)
    assert generation._date_form_dates_once("%%/%%/%%%%") == 80 * 12 * 12


def test_a_month_word_form_with_no_mark_of_every_width_is_a_date() -> None:
    """Codex item 6: `%%@@@%%` (`%d%b%y`) was read only with a day of two figures beside a year of four, so
    200 twin cells were written `63TIY12`. Every day of one or two figures beside a year of two or four.
    Mutant: the no-mark month word read at nine places alone."""
    for form, layout in (("%%@@@%%", "%d%b%y"), ("%@@@%%", "%d%b%y"), ("%@&&%%%%", "%d%b%Y"), ("%%&&&%%%%", "%d%b%Y")):
        assert generation._date_form_fields(form) is not None, form
        for step in range(300):
            written = f"{generation._date_filled_form(form, step)}"
            assert hunt._is_a_date(written, (layout,)), (form, step, written)
    assert generation._date_form_fields("%%%@@@%%") is None and generation._date_form_fields("%%@@@%%%") is None


def _the_oracle() -> types.ModuleType:
    """The reference oracle, loaded from its committed file."""
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_hb", path)
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    return oracle


def test_the_oracle_fills_a_month_and_year_beside_dates_as_the_product_does() -> None:
    """Codex item 9: a description from 100 cells `2000-01-01` beside six `02/2001` and six `03/2002`
    publishes ISO and month-and-year forms; the product writes the held-back levels as months and years,
    and the oracle's label walk, given no date context, reached `00/0000` and raised. Mutant: the
    oracle's label walk without the column's date context."""
    oracle = _the_oracle()
    written = oracle.invented_levels({"2000-01-01"}, [6, 6], census={"%%%%-%%-%%": 100, "%%/%%%%": 12},
                                     written=["2000-01-01"] * 100)
    used: "dict[str, int]" = {"2000-01-01": 100}
    product = [generation._made_up_label(6, used, {}, "%%/%%%%", (), {}, dated=True)[1] for _ in range(2)]
    assert [label for label, _size in written] == product, (written, product)
    assert all(hunt._is_a_date(label, ("%m/%Y",)) for label in product)


def test_an_acronym_made_plural_names_a_key() -> None:
    """Codex item 2: `patient_IDs` was cut `patient`, `i`, `ds`, so sixty keys `10` to `69` were asked
    nothing and all 1,200 twin cells were real; `patient_ID` was held. Mutant: `_closes_a_plural`
    answering False."""
    assert asking.key_name_words("patient_IDs") == ["patient", "ids"]
    assert asking.key_name_words("PatientIDsList") == ["patient", "ids", "list"]
    for name in ("patient_IDs", "UIDs", "encounter_CSNs", "PersonIDs"):
        assert asking.named_as_a_key(name), name
    assert asking._named_key_puts("patient_IDs", [f"{10 + k // 20}" for k in range(1_200)], "count")
    assert not asking.named_as_a_key("HTTPServer") and not asking.named_as_a_key("ABCsomething")


# -- repair 2: the verify of lane HB, finding 1: no run of figures of a free-text twin is a real one ----


def test_the_openings_of_free_text_runs_pass_over_held_openings_and_end_at_a_few() -> None:
    """`taxonomy.figure_openings`: each merged width of four figures or more and the shortest opening no
    run of it opens with, an opening held by the floor's runs or more passed over and one held by 1 to 10
    ending its size (ID-ROOM's ruling 3, item 2, option (b)); the noughts opening a run are not read, a width
    no run holds is not named, and a run of four figures or more merged narrower names 3 beside nothing.
    Mutants: the floor's stop withdrawn; the width read at five (LANE HB RULINGS 6, item 4)."""
    cells = [f"x 99{k:05d} y" for k in range(20)] + [f"8{k:06d}" for k in range(3)] + ["0012345", "1234", "x 123 y"]
    assert taxonomy.figure_openings(cells, 11) == {"4": "9|8|7|6|5|4|3|2", "5": "9|8|7|6|5|4|3|2", "7": "98"}
    # ...and one run `99999` held by a single cell ends every size of its width: no opening.
    assert taxonomy.figure_openings(["0099999"], 11) == {"5": ""}
    assert taxonomy.figure_openings(["0000123", "0000"], 11) == {"3": ""}
    assert parsing.is_a_figure_width("3") and parsing.is_a_figure_opening(3, "") and not parsing.is_a_figure_opening(3, "9")


def _none_absent() -> "generation._AbsentSpellings":
    """No absent spelling, read as the run walk reads a column's (LANE HB RULINGS 9 (2))."""
    return generation._absent_spellings_read(())


def _text_facts(openings: "dict[int, str]") -> contract.TextFacts:
    return contract.TextFacts(
        length=contract.LengthStats(minimum=4, maximum=12, mean=None, p50=None),
        words=contract.WordStats(minimum=1, maximum=3, mean=None), n_all_digits=3, n_code_alphabet=5,
        n_distinct_by_occurrences={"1": 7}, shape_forms={}, figure_openings=openings,
    )


def test_free_text_runs_of_a_named_width_are_renamed_one_to_one() -> None:
    """`_figure_runs_off_the_real`: a run of the narrowest named width not wearing its opening is renamed in every
    cell alike, to the opening and the next filling no run holds, one to one, its length kept; a run under the
    narrowest named width, a run wearing its opening, an absent spelling and noughts before a run are kept; a run
    WIDER than the narrowest is renamed whatever it opens with, since a real run could stand inside it. Mutant: no
    run renamed; a wider run wearing its own opening kept."""
    facts = _text_facts({7: "9"})
    cells = ["1000001", "a 1000001;1000002", "9000000", "001000003", "R123456", "1234", "999999", "1000001"]
    written, spent = generation._figure_runs_off_the_real(cells, facts, ("999999",))
    assert spent == [0, 0], written
    assert written[0] == written[7] and written[1] == f"a {written[0]};{written[1][len(written[0]) + 3:]}"
    assert written[0][0] == "9" and len(written[0]) == 7 and written[0] != "9000000", written
    assert written[2] == "9000000" and written[3][:2] == "00" and written[3][2] == "9", written
    assert written[4] == "R123456" and written[5] == "1234" and written[6] == "999999", written
    assert len(set(written)) == len(set(cells))
    # ...two widths: the wider run opens with its own opening and is still led down under the narrower.
    wide, spent = generation._figure_runs_off_the_real(["912345678", "88888"], _text_facts({5: "9", 9: "9"}), ())
    assert wide[0][:5] == "00000" and int(wide[0]) < 10 ** 4 and wide[1][0] == "9" and spent == [0, 0], wide


def test_every_room_of_a_run_is_free_of_the_real_by_construction() -> None:
    """LANE HB RULINGS 6, a walk that runs out of room. Four thousand runs of four figures with one free opening
    are written `9` and three figures, then under the narrowest width with noughts, then a figure wider opening
    `99`, `999`, each run of four inside still opening `9`; past every room, noughts alone, counted; and a real run
    of figures so few merged (`0000123`, key 3) takes no room led by noughts. Mutants: each step withdrawn."""
    openings = {4: "9"}
    taken: "dict[str, bool]" = {}
    steps: "dict[int, int]" = {}
    counts = [0, 0]
    written = [generation._renamed_run(f"{1000 + k}", openings, taken, steps, _none_absent(), counts) for k in range(4000)]
    # ...each spelling of noughts alone counted, the first too (Codex's review of the close round, item 5).
    assert len(set(written)) == 4000 - counts[1] + 1, counts
    assert written[0] == "9000" and written[999] == "9999" and written[1000] == "100" and written[1899] == "999"
    assert written[1998] == "9" and written[1999] == "0000" and written[2000] == "99000", written[1990:2001]
    for run in written:
        width = len(run)
        for at in range(width - 3):
            assert width <= 3 or run == "0000" or run[at] == "9", run
    assert counts[0] > 0 and counts[1] == 1, counts
    # ...padded real runs: no filling led by noughts; a width no real run holds where one is free.
    padded = {3: "", 4: "9"}
    assert generation._renamed_run("1234", padded, {}, {}, _none_absent(), [0, 0]) == "9000"
    assert not generation._figure_run_stands("123", padded) and generation._figure_run_stands("123", {4: "9"})
    only = {3: ""}
    assert generation._renamed_run("123", only, {}, {}, _none_absent(), [0, 0]) == "1000"
    assert generation._figure_run_stands("1234", only)
    # ...no room at all: noughts, named.
    counts = [0, 0]
    assert generation._renamed_run("1234", {3: "", 4: ""}, {"0000": True}, {}, _none_absent(), counts) == "0000" and counts == [0, 1]
    # ...a wider width whose opening differs ends the walk wider.
    counts = [0, 0]
    assert generation._renamed_run("12345", {5: "9", 6: "8"}, {"00000": True},
                                   {-10000: 10_000, -4: 9_000, -3: 900, -2: 90, -1: 9}, _none_absent(), counts) == "00000"
    assert counts == [0, 1]
    # ...each figure a value joined by `|` names is a room in turn.
    several: "dict[str, bool]" = {}
    spots: "dict[int, int]" = {}
    both = [generation._renamed_run(f"{1000 + k}", {4: "9|8"}, several, spots, _none_absent(), [0, 0]) for k in range(2001)]
    assert both[999] == "9999" and both[1000] == "8000" and both[1999] == "8999" and both[2000] == "100"
    assert not generation._figure_run_stands("7000", {4: "9|8"}) and generation._figure_run_stands("8000", {4: "9|8"})


def test_keys_in_free_text_write_no_real_key_at_the_floor(tmp_path: pathlib.Path) -> None:
    """The verify of lane HB, finding 1, at 20,000 rows, one table of four columns read as free text:
    4,000 keys `1000000` to `1003999` one to three a cell joined by `;` and by `|`, keys alone in every
    other cell of a column of notes, and linked order numbers once each between commas. On ad2afb62 the
    twin wrote 4,000, 4,000, 3,334 and 6,813 real key tokens and 3,265, 3,265, 3,334 and 1,192 cells equal
    to a real cell; no run of figures it writes is a real key's now, and no cell a real one. LANE HB RULINGS 6,
    item 4: keys 1000 to 4999 joined by `;` (`short4000_semi`) wrote 4,000 of 4,000 real tokens and 3,265 equal
    cells on every line; runs are read from four figures. Mutants: `_figure_runs_off_the_real` handing the cells
    back; the run read from five figures."""
    names = ("num4000_semicolon", "num4000_bar", "keys_in_free_text", "seq_once_comma", "short4000_semi")
    columns = {name: hunt.SHAPES[name][0](20_000) for name in names}  # type: ignore[operator]
    folder = tmp_path / "free-text-keys"
    folder.mkdir()
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        writer.writerows(zip(*(columns[name] for name in names)))
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"]) == 0
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0", "--replace"]) == 0
    blocks = {one["name"]: one for one in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]}
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    for place, name in enumerate(names):
        assert blocks[name]["role"] == "free_text", (name, blocks[name]["role"])
        wanted = {"4": "9|8|7|6|5"} if name == "short4000_semi" else {"7": "9|8|7|6|5|4|3|2"}
        assert blocks[name]["figure_openings"] == wanted, (name, blocks[name].get("figure_openings"))
        real = columns[name]
        twin = [row[place] for row in table[1:]]
        tokens = {token for cell in real for token in hunt._list_tokens(cell) if hunt._a_key_token(token)}
        merged = {parsing.merged_key(token) for token in tokens}
        assert sum(1 for cell in twin for token in hunt._list_tokens(cell) if parsing.merged_key(token) in merged) == 0, name
        assert room.equal_cells(real, twin) == 0, name


def test_a_wider_list_member_carries_no_narrower_real_key() -> None:
    """Codex item 8: `R30816` beside `R100000`, 120 cells, published `@9%%%%,@9%%%%%`, and the twin wrote
    `K930816`, six figures off every real key of six that hold `30816`, a real key of five. A field wider than
    the narrowest real key opens with one figure no real key of any width up to its own opens with, written
    once more than its width exceeds the narrowest's (`@9%%%%,@99%%%%`), so every run of five inside it opens
    with it too; a layout whose fields are as narrow as every real key keeps its own openings. Mutant:
    `_list_common_opening` answering nothing."""
    cells = [f"R{30816 + k},R{100000 + k}" for k in range(120)]
    firsts = taxonomy._list_key_firsts(cells, 4)
    assert taxonomy._list_exclusion_of("@%%%%%,@%%%%%%", firsts, 11, 120) == "@9%%%%,@99%%%%"
    same = taxonomy._list_key_firsts([f"R{100000 + k},R{200000 + k}" for k in range(120)], 4)
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%%", same, 11, 120) == "@9%%%%%,@9%%%%%"


def test_a_one_key_value_beside_lists_with_no_opening_is_the_spill_of_figures() -> None:
    """The verify of lane HB, finding 2: where a key's noughts leave no room either, the values of a layout
    with no exclusion are the spill's; a one-key value was widened under its letter and two twin cells
    (`R110072044036505063606260`) held a real `R110072` as text. Beside a layout of keys between commas a
    layout of one key is offered its template and the spill of figures alone, never widened under its letter.
    Mutant: `_one_key_beside_lists` answering False."""
    facts = contract.IdentifierFacts(
        min_length=7, max_length=23, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=30,
        n_distinct_by_occurrences={"1": 30}, layout_forms={"@%%%%%%": 10, "@%%%%%%,@%%%%%%": 20},
        layout_prefixes={}, layout_exclusions={parsing.EXCLUSION_SPILL: ("%" * 24,)},
    )
    room_ = generation._off_the_real_room(facts, ())
    assert generation._off_the_real_targets(room_, "R123456") == ["%" * 24]
    alone = dataclasses.replace(facts, layout_forms={"@%%%%%%": 30})
    assert len(generation._off_the_real_targets(generation._off_the_real_room(alone, ()), "R123456")) == 2


def _all_held(widths: "tuple[int, ...]") -> "dict[int, dict[str, int]]":
    """Each width's openings, every opening of one to three figures held by the floor's keys or more."""
    held: "dict[str, int]" = {}
    for opening in range(1, 1000):
        held[f"{opening}"] = 40
    return {width: dict(held) for width in widths}


def test_a_key_no_opening_fits_is_kept_at_its_width_by_its_noughts() -> None:
    """The verify of lane HB, finding 2: random keys hold every opening whose fillings could hold the layout's
    values, so rule 13 had nothing to publish and every cell was the spill: no list, exit 3. A member led by a
    nought is as wide as a real key and, merged, narrower than every one; the next width's opening stands after
    it, read as rule 13 reads it; noughts as many as a wider field needs to fall under the narrowest real key;
    each field holding its share of the layout's values, its letter's places counted. Mutants:
    `_list_nought_opening` answering nothing; one nought for every field; each field asked the whole room."""
    six = _all_held((6,))
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%%", six, 11, 6_000) == "@09%%%%,@09%%%%"
    assert taxonomy._list_exclusion_of("@%%%%%%", six, 11, 6_000) == "@09%%%%"
    # ...its letter's places hold what the figures alone do not (at 30,000 rows the one-key layout of
    # `reglistmixR` lost its exclusion and 6,751 cells were the spill).
    assert taxonomy._list_exclusion_of("@%%%%%%", six, 11, 100_000) == "@09%%%%"
    assert taxonomy._list_exclusion_of("%%%%%%%,%%%%%%%", _all_held((7,)), 11, 6_000) == "09%%%%%,09%%%%%"
    # ...each field its share: two fields of 10^4 fillings each hold 10^8 cells, one figure's opening or not.
    assert taxonomy._list_exclusion_of("%%%%%%,%%%%%%", six, 11, 1_000_000) == "09%%%%,09%%%%"
    assert taxonomy._list_exclusion_of("%%%%%%", six, 11, 1_000_000) == ""
    # ...the next width's openings read as rule 13 reads them: held by the floor's keys passed over, by a few
    # ending the size.
    # (A key of four figures is one a member could carry, Codex's review of batch 4n, item 2: the width down whose
    # openings the noughts read is three figures beside keys of four.)
    beside = _all_held((4,))
    beside[3] = {"9": 40, "8": 3}
    assert taxonomy._list_exclusion_of("@%%%%", beside, 11, 100) == "@099%"
    beside[3] = {"9": 40}
    assert taxonomy._list_exclusion_of("@%%%%", beside, 11, 100) == "@08%%"
    # ...and keys of four beside a field of five, read by no width rule before, are kept off it by its noughts.
    beside = _all_held((5,))
    beside[4] = {"9": 40, "8": 3}
    assert taxonomy._list_exclusion_of("@%%%%%", beside, 11, 100) == "@009%%"
    # ...two widths, no common figure: each member merged narrower than the narrowest real key, so no real key
    # of five figures is carried inside a member of six (Codex's review of lane HB, item 8).
    both = _all_held((5, 6))
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%", both, 11, 400) == "@009%%%,@09%%%"
    # ...a field writing a zero fill of its own takes none.
    assert taxonomy._list_nought_opening(0, 1, 6, six, 11, 100, 1) == ""


def test_a_nought_led_key_alone_is_kept_off_the_real_and_its_census_reported_only() -> None:
    """A one-key cell of figures alone led by a nought (`0941234`) wears the zero-fill layout, not the one its
    exclusion was published for (`parsing.template_layout`): the pass reads it kept off the real under that
    layout, no other value is moved into it, and the validator reads its census entry REPORT-ONLY (V4.1-A1).
    Mutants: `template_layout` answering `prefix_layout`; `nought_led` left empty; `leaves_its_layout` False."""
    plain = parsing.LAYOUT_PLAIN
    assert parsing.template_layout("09%%%%%", plain) == "!%%%%%%"
    assert parsing.template_layout("@09%%%%", plain) == "@%%%%%%"
    assert parsing.template_layout("09%%%%%,09%%%%%", plain) == "%%%%%%%,%%%%%%%"
    assert parsing.leaves_its_layout("%%%%%%%", "09%%%%%")
    assert not parsing.leaves_its_layout("@%%%%%%", "@09%%%%")
    assert not parsing.leaves_its_layout("%%%%%%%", "99%%%%%")
    facts = contract.IdentifierFacts(
        min_length=7, max_length=23, all_whole_numbers=False, n_all_digits=10, n_code_alphabet=10,
        n_distinct_by_occurrences={"1": 30}, layout_forms={"%%%%%%%": 10, "%%%%%%%,%%%%%%%": 20},
        layout_prefixes={},
        layout_exclusions={parsing.EXCLUSION_SPILL: ("%" * 24,), "%%%%%%%": ("09%%%%%",),
                           "%%%%%%%,%%%%%%%": ("09%%%%%,09%%%%%",)},
    )
    room_ = generation._off_the_real_room(facts, ())
    assert room_.nought_led == {"!%%%%%%": ["09%%%%%"]}
    assert generation._kept_off_the_real(room_, "0912345")
    assert not generation._kept_off_the_real(room_, "0812345") and not generation._kept_off_the_real(room_, "9012345")
    assert generation._off_the_real_targets(room_, "0812345") == ["%" * 24]
    assert validation.moved_off_the_real(facts, 30) == (("%%%%%%%",), True)
    column = contract.ColumnBlock.__new__(contract.ColumnBlock)
    object.__setattr__(column, "name", "registers")
    object.__setattr__(column, "time_grain", None)
    cells = ["1234567", "2345678,3456789", "1234567", "4567890,5678901"]
    written, _remarks = generation._spelled_off_the_real(column, facts, cells, ())
    assert written[0] == written[2] and written[0][:2] == "09" and len(written[0]) == 7, written
    for cell in written[1::2]:
        assert [token[:2] for token in cell.split(",")] == ["09", "09"] and len(cell) == 15, written


def test_list_templates_of_one_merged_key_spend_one_room(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keys of two widths kept off by noughts (`@09%%%`, `@009%%%`) fill to one merged key at one step, so each
    template walking from its own step walked over all the others' and, past 4,096 fillings, wrote the spill
    (1,771 of 20,000 cells of `randmix_comma`, exit 3). One room between them. Mutant: `spends` left empty."""
    monkeypatch.setattr(generation, "_OFF_THE_REAL_TRIES", 8)
    ex = {parsing.EXCLUSION_SPILL: ("%" * 24,), "@%%%%%": ("@09%%%",), "@%%%%%%": ("@009%%%",),
          "@%%%%%,@%%%%%%": ("@09%%%,@009%%%",)}
    facts = contract.IdentifierFacts(
        min_length=6, max_length=20, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=60,
        n_distinct_by_occurrences={"1": 80}, layout_forms={"@%%%%%": 40, "@%%%%%%": 40, "@%%%%%,@%%%%%%": 5},
        layout_prefixes={}, layout_exclusions=ex,
    )
    room_ = generation._off_the_real_room(facts, ())
    assert room_.spends["@09%%%"] == room_.spends["@009%%%"] == "@9%%%"
    column = contract.ColumnBlock.__new__(contract.ColumnBlock)
    object.__setattr__(column, "name", "registers")
    object.__setattr__(column, "time_grain", None)
    cells = [f"R{50000 + k}" for k in range(40)] + [f"R{500000 + k}" for k in range(40)]
    written, _remarks = generation._spelled_off_the_real(column, facts, cells, ())
    for cell, wrote in zip(cells, written):
        assert len(wrote) == len(cell) and wrote[1] == "0", (cell, wrote)
    assert len({parsing.merged_key(cell) for cell in written}) == 80


def test_a_run_no_opening_of_its_width_fits_is_kept_at_its_width_by_noughts() -> None:
    """Random keys in free text (`;` between them, or too few rows for rule 11): width 7 names no opening, and a
    run went a figure wider, past `max_length` (exit 3). Noughts and a run of fewer figures than the narrowest named
    width are as long and merged narrower than every real run, whatever the draw. Mutant: the route withdrawn from
    `_renamed_run`."""
    taken: "dict[str, bool]" = {}
    counts = [0, 0]
    steps: "dict[int, int]" = {}
    one = generation._renamed_run("6141847", {7: ""}, taken, steps, _none_absent(), counts)
    two = generation._renamed_run("6722529", {7: ""}, taken, steps, _none_absent(), counts)
    assert (one, two) == ("100000", "100001") and counts == [0, 0], (one, two)
    # ...and where the width's fillings are spent (`999` and two figures: the suite's skeptic's table).
    spent: "dict[int, int]" = {}
    five = [generation._renamed_run(f"{10000 + k}", {5: "999"}, {}, spent, _none_absent(), counts) for k in range(101)]
    assert five[99] == "99999" and five[100] == "1000" and counts == [0, 0], five[99:]
    # ...the narrowest named width governs, a wider run led under it whatever the wider width names.
    three = generation._renamed_run("6141847", {7: "", 6: "9"}, {}, {}, _none_absent(), counts)
    assert three == "10000" and counts == [0, 0], three
    assert generation._figure_runs_off_the_real(["6141847"], _text_facts({7: "", 6: "9"}), ())[0] == ["0010000"]


def test_keys_between_commas_stay_lists_and_write_no_real_key_at_the_floor(tmp_path: pathlib.Path) -> None:
    """At 20,000 rows, one table of four columns held by rule 11 (one case, the list writer). Skeptic 1, item 2
    (LANE HB RULINGS 2, item 2): 4,000 record numbers `1000000` to `1003999`, or `R100000` to `R103999`, one to
    three a cell between commas, read as free text on lane HB's base: 4,008 and 7 real key tokens in the twin,
    3,265 and 2 cells equal to a real cell, validate exit 3. The verify of lane HB, finding 2: 4,000 keys `R` and
    six random figures and 6,000 of seven: on 944f6256 no cell was a list (24 and 25 figures past the published
    `max_length` of 23), validate exit 3. Every list cell stays one, every key is as wide as the real, no token
    equals or merges with a real key, no cell holds a real key as text or as a run (a single key `Z102180` beside
    a real `R102180`: 30 cells while the layout of one key was kept off by its letter alone, LANE HB RULINGS 3),
    and validate exits 0. LANE HB RULINGS 6, item 3: 6,000 random keys of five figures (`rand5_comma`), whose
    6,794 lone keys were 18-figure spills holding 3,920 real keys inside, are noughts and figures (`0%%%%`).
    Mutants: the route withdrawn; `a_list_layout` False; `one_list_key` False; `_list_nought_opening` answering
    nothing; its noughts alone withdrawn."""
    names = ("num4000_comma", "reg4000_comma", "randR_comma", "rand7_comma", "rand5_comma")
    columns = {name: hunt.SHAPES[name][0](20_000) for name in names}  # type: ignore[operator]
    folder = tmp_path / "lists"
    folder.mkdir()
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        writer.writerows(zip(*(columns[name] for name in names)))
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"]) == 0
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0", "--replace"]) == 0
        assert cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                         "--out-dir", f"{folder}", "--replace"]) == 0
    blocks = {one["name"]: one for one in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]}
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    for place, name in enumerate(names):
        assert blocks[name]["role"] == "identifier", (name, blocks[name]["role"])
        real = columns[name]
        twin = [row[place] for row in table[1:]]
        assert sum(1 for cell in twin if "," in cell) == sum(1 for cell in real if "," in cell), name
        assert sorted(len(cell) for cell in twin) == sorted(len(cell) for cell in real), name
        tokens = {token for cell in real for token in hunt._list_tokens(cell)}
        merged = {parsing.merged_key(token) for token in tokens}
        runs = {found.lstrip("0") for token in tokens for found in re.findall(r"\d+", token)}
        assert sum(1 for cell in twin for token in hunt._list_tokens(cell) if parsing.merged_key(token) in merged) == 0
        assert sum(1 for cell in twin if any(found.lstrip("0") in runs for found in re.findall(r"\d+", cell))) == 0
        width = max(len(token) for token in tokens)
        assert sum(1 for cell in twin if any(cell[at:at + width] in tokens for at in range(len(cell)))) == 0, name
        assert room.equal_cells(real, twin) == 0, name
        wholes = {parsing.merged_key(cell) for cell in real}
        assert sum(1 for cell in twin if parsing.merged_key(cell) in wholes) == 0, name
        # ...and no real key inside a longer run (LANE HB RULINGS 6, item 3: `rand5_comma`'s lone keys were
        # 18-figure spills holding 3,920 real keys).
        assert hunt.cells_carrying(tokens, twin) == 0, name
    assert blocks["rand5_comma"]["layout_exclusions"]["%%%%%"] == "0%%%%"


def test_the_oracle_writes_a_nought_led_key_as_the_product_does(monkeypatch: pytest.MonkeyPatch) -> None:
    """A-P4-59: the oracle's final pass reads a key kept off by noughts as the product does, the one-key layout
    under its zero fill and the templates of one merged key from one room, and its free-text runs a nought and a
    run of the next width down. Mutants: `nought_led` left out of the oracle; its own step for each template; the
    route withdrawn from its `rename`."""
    oracle = _the_oracle()
    # ...at two tries a search, a template walking from its own step over another's fillings finds none.
    monkeypatch.setattr(oracle, "LAYOUT_STEPS", 2)
    monkeypatch.setattr(generation, "_OFF_THE_REAL_TRIES", 2)
    block = {
        "layout_forms": {"%%%%%%%": 2, "%%%%%%%%": 2, "%%%%%%%,%%%%%%%": 2},
        "layout_exclusions": {parsing.EXCLUSION_SPILL: "%" * 24, "%%%%%%%": "09%%%%%", "%%%%%%%%": "009%%%%%",
                              "%%%%%%%,%%%%%%%": "09%%%%%,09%%%%%"},
        "layout_prefixes": {},
    }
    cells = ["1234567", "2234567", "3234567", "1234567", "2345678,3456789", "4567890,5678901", "12345678",
             "22345678", "32345678"]
    facts = contract.IdentifierFacts(
        min_length=7, max_length=15, all_whole_numbers=False, n_all_digits=3, n_code_alphabet=3,
        n_distinct_by_occurrences={"1": 3}, layout_forms=block["layout_forms"], layout_prefixes={},
        layout_exclusions={key: (value,) for key, value in block["layout_exclusions"].items()},
    )
    column = contract.ColumnBlock.__new__(contract.ColumnBlock)
    object.__setattr__(column, "name", "registers")
    object.__setattr__(column, "time_grain", None)
    product, _remarks = generation._spelled_off_the_real(column, facts, cells, ())
    assert oracle.spelled_off_the_real(block, cells) == product, product
    runs = ["6141847", "6722529;6141847"]
    facts_text = contract.TextFacts(
        length=contract.LengthStats(minimum=7, maximum=15, mean=None, p50=None),
        words=contract.WordStats(minimum=1, maximum=1, mean=None), n_all_digits=1, n_code_alphabet=1,
        n_distinct_by_occurrences={"1": 2}, shape_forms={}, figure_openings={7: ""},
    )
    written, _wider = generation._figure_runs_off_the_real(runs, facts_text, ())
    assert oracle.figure_runs_off_the_real({"figure_openings": {"7": ""}}, runs) == written, written
    spent = [f"{10000 + k}" for k in range(103)]
    facts_spent = dataclasses.replace(facts_text, figure_openings={5: "999"})
    written, _wider = generation._figure_runs_off_the_real(spent, facts_spent, ())
    assert oracle.figure_runs_off_the_real({"figure_openings": {"5": "999"}}, spent) == written, written
    # ...every room in turn, and a label column's published spellings kept (LANE HB RULINGS 6, item 2).
    many = [f"{1000 + k}" for k in range(4000)] + ["123", "0000123", "R123456"]
    for names in ({4: "9"}, {3: "", 4: "9"}, {3: ""}, {3: "", 4: ""}, {4: "9", 5: "9"}, {4: "", 7: "98"}):
        written, _wider = generation._figure_runs_off_the_real(many, dataclasses.replace(facts_text, figure_openings=names), ())
        said = {"figure_openings": {f"{width}": names[width] for width in names}}
        assert oracle.figure_runs_off_the_real(said, many) == written, names
    kept = {"1500": True, "R123456": True}
    written, _wider = generation._figure_runs_off_the_real(many, dataclasses.replace(facts_text, figure_openings={4: "9"}), (), kept)
    assert oracle.figure_runs_off_the_real({"figure_openings": {"4": "9"}}, many, list(kept)) == written
    assert written[500] == "1500" and written[-1] == "R123456"


# -- the close round: LANE HB RULINGS 6, on batch 4m's merge ------------------------------------------


def _one_table(tmp_path: pathlib.Path, names: "tuple[str, ...]", rows: int = 20_000, typed: "tuple[str, ...]" = ()) -> "tuple[dict[str, object], dict[str, list[str]], dict[str, list[str]]]":
    """Several hunt shapes as one table, profiled with nobody at the keyboard (``typed`` the options), generated at seed 0."""
    columns = {name: hunt.SHAPES[name][0](rows) for name in names}  # type: ignore[operator]
    folder = tmp_path / "one-table"
    folder.mkdir()
    with open(folder / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(names)
        writer.writerows(zip(*(columns[name] for name in names)))
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{folder / 't.csv'}", "--out-dir", f"{folder}", "--replace"] + list(typed)) == 0
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0", "--replace"]) == 0
    blocks = {one["name"]: one for one in json.loads((folder / "t-profile.json").read_text("utf-8"))["columns"]}
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    twins = {name: [row[place] for row in table[1:]] for place, name in enumerate(names)}
    return blocks, columns, twins


def _carrying(real: "list[str]", twin: "list[str]") -> "tuple[int, int, int]":
    """Twin cells equal to a real key (a word with no figure, a published level, kept by design), list tokens real,
    and cells holding a real run: linear."""
    tokens = {token for cell in real for token in hunt._list_tokens(cell) if hunt._a_key_token(token)}
    merged = {parsing.merged_key(token) for token in tokens}
    real_tokens = sum(1 for cell in twin for token in hunt._list_tokens(cell) if parsing.merged_key(token) in merged)
    words = frozenset(cell for cell in real if not re.search(r"\d", cell))
    return room.equal_cells(real, twin, words), real_tokens, hunt.cells_carrying(tokens, twin)


def test_keys_read_as_labels_write_no_real_key_at_the_floor(tmp_path: pathlib.Path) -> None:
    """LANE HB RULINGS 6, item 2 (verify 2, finding 1), one table at 20,000 rows, one case the label writer. Keys once
    each beside `pending` on 35 % of rows, read as labels with no question: on batch 4m's merge 8,366, 200 and 8,362
    twin cells equal a real key, and a real run inside. No twin cell equals or merges with a real key and no run holds
    a real one, by construction; `pending` keeps its spelling. A column held beside them (a register list asked the
    person question) would hold them as record numbers, so they stand in a table of their own; the lists ride with the
    `;` case.
    Mutants: `label_figure_openings` publishing nothing; the walk's stand-ins left as drawn."""
    names = ("lab_R_once", "lab_Rrand_once", "lab_ABC_once")
    blocks, columns, twins = _one_table(tmp_path, names)
    for name in names:
        assert _carrying(columns[name], twins[name]) == (0, 0, 0), name
        assert twins[name].count("pending") == columns[name].count("pending"), name
        assert blocks[name]["role"] == "long_tail_labels", (name, blocks[name]["role"])
        assert "6" in blocks[name]["figure_openings"], name
        assert "@%%%%%%" not in blocks[name].get("shape_form_places", {}), name


def test_keys_marked_by_a_semicolon_read_as_labels_are_kept_off_the_real_at_their_opening(tmp_path: pathlib.Path) -> None:
    """LANE HB RULINGS 6, item 2's `lab_R_list_semi`: held as record numbers, each lone key kept off by a letter
    (`Z102949` beside a real `R102949`). The description at 20,000 rows opens the lone key with no real opening; the
    twin at 20,000 rows is K-HZ-13's (limit (r)'s time, LANE HB RULINGS 4 (1)'s deviation), and at 600 rows here
    (its generate is about 20 processor seconds). Mutant: `_holds_marked_keys` False."""
    cells = hunt.SHAPES["lab_R_list_semi"][0](20_000)  # type: ignore[operator]
    present = [cell for cell in cells if cell != "pending"]
    assert taxonomy._holds_marked_keys(present) and not taxonomy._holds_marked_keys(["R100000", "R100001"])
    firsts = taxonomy._list_key_firsts(present, 6)
    assert taxonomy._list_exclusion_of("@%%%%%%", firsts, 11, 4_000)[:2] == "@9"
    blocks, columns, twins = _one_table(tmp_path, ("lab_R_list_semi", "lab_R_list_comma"), 600)
    assert blocks["lab_R_list_semi"]["role"] == "identifier"
    assert blocks["lab_R_list_semi"]["layout_exclusions"]["@%%%%%%"][:2] == "@9"
    for name in ("lab_R_list_semi", "lab_R_list_comma"):
        assert blocks[name]["role"] == "identifier", name
        assert _carrying(columns[name], twins[name]) == (0, 0, 0), name


def test_the_hunt_reads_a_real_run_inside_a_longer_one() -> None:
    """LANE HB RULINGS 6, item 3: `list_cells_carrying` compared whole runs only, so the 18-figure spills of
    `rand5_comma` read 0 while 3,920 held a real key. Each run is read at each place at each real run's length.
    And a lone key with no opening whose narrower widths no real key holds is noughts and figures (`0%%%%`), and
    with a real key that narrow there is none. Mutants: whole runs only; noughts alone withdrawn."""
    assert hunt.cells_carrying({"46068", "R12345"}, ["18460681863", "Q912345", "Q12345", "4606", "R1234"]) == 3
    held = {5: {f"{figure}": 700 for figure in range(1, 10)}}
    assert taxonomy._list_exclusion_of("%%%%%", held, 11, 6_000) == "0%%%%"
    held[3] = {"1": 20}
    assert taxonomy._list_exclusion_of("%%%%%", held, 11, 6_000) == ""


def test_padded_keys_among_notes_write_no_real_key_at_the_floor(tmp_path: pathlib.Path) -> None:
    """LANE HB RULINGS 6, item 5, at 20,000 rows, alone in its table: a padded key column asked the person question
    holds every other key column of its table as one beside it, so it is not put in another writer's table. Held, its
    keys keep their layout: several free figures after the zero fill, never a spill. Mutant: `_several_after_noughts`
    answering nothing."""
    blocks, columns, twins = _one_table(tmp_path, ("pad_alone_notes",))
    assert blocks["pad_alone_notes"]["role"] == "identifier"
    assert _carrying(columns["pad_alone_notes"], twins["pad_alone_notes"]) == (0, 0, 0)
    assert blocks["pad_alone_notes"]["layout_exclusions"]["!!!%%%%"][:2] == ["!!!9%%%", "!!!8%%%"]
    assert sum(1 for cell in twins["pad_alone_notes"] if re.fullmatch(r"000[1-9]\d{3}", cell)) == 10_000


def test_padded_keys_among_notes_are_asked_whether_or_not_they_repeat() -> None:
    """LANE HB RULINGS 6, item 5: `0001000` upward beside notes holding a small number read as numbers beside labels
    with no question, and the twin held 9,998 real keys at 20,000 rows. A note (a letter, no run of four figures) is
    set aside beside padded keys, which are asked whether or not they repeat. Mutants: `_a_note_beside_padded_keys`
    False; the repeat condition kept."""
    assert asking._a_note_beside_padded_keys("seen by dr 12 in clinic")
    assert not asking._a_note_beside_padded_keys("12345") and not asking._a_note_beside_padded_keys("x 1234")
    six = [f"{(k // 6) + 1000:07d}" if k % 2 == 0 else f"seen by dr {k % 90} in clinic" for k in range(1200)]
    once = [f"{(k // 2) + 1000:07d}" if k % 2 == 0 else f"seen by dr {k % 90} in clinic" for k in range(1200)]
    assert asking._padded_beside_words(six) and asking._padded_beside_words(once)
    assert not asking._padded_beside_words([f"{k}" for k in range(600)] + ["seen by dr 12"] * 20)


def test_a_code_column_keeps_its_published_codes_and_a_width_mostly_published_names_no_opening() -> None:
    """LANE HB RULINGS 6's attack: a real code held back is not a key. A width whose rows mostly stand in published
    levels is a code's and names no opening; a width whose rows are mostly held back is treated as a key's, whatever
    stands beside it; a published level is never renamed. Mutants: every width named; published levels renamed."""
    codes = [f"{10000 + k % 3}" for k in range(600)] + [f"{20000 + k}" for k in range(100)]
    assert taxonomy.label_figure_openings(codes, ["10000", "10001", "10002"], 11) == {}
    keys = ["pending"] * 300 + [f"{20000 + k}" for k in range(700)]
    assert taxonomy.label_figure_openings(keys, ["pending"], 11) == {"5": "9|8|7|6|5|4|3|1"}
    # ...a form holding such a run publishes no places; a shorter run does.
    assert taxonomy.form_holds_a_named_run("@%%%%%", {"5": "9"}) and not taxonomy.form_holds_a_named_run("@%%%%", {"5": "9"})
    facts = dataclasses.replace(_text_facts({5: "9"}))
    written, _spent = generation._figure_runs_off_the_real(["pending", "20001", "20002", "30003"], facts, (), {"30003": True})
    assert written[0] == "pending" and written[3] == "30003" and written[1][0] == "9" and written[2][0] == "9", written


# -- close round 2: Codex's review of the close round (codex-w3/verdict-HBc.md), LANE HB RULINGS 8 ---------------


def _real_runs(cells: "list[str]", published: "set[str]") -> "set[str]":
    """The held-back real cells' runs of four figures or more, as written (noughts kept)."""
    return {found for cell in cells if cell not in published for found in re.findall(r"\d+", cell) if len(found) >= 4}


def _holding(runs: "set[str]", cells: "list[str]") -> "list[str]":
    """The cells holding one of ``runs`` as written, read at each place at each length."""
    lengths = sorted({len(found) for found in runs})
    return [cell for cell in cells if any(found[at:at + size] in runs for found in re.findall(r"\d+", cell)
                                          for size in lengths for at in range(len(found) - size + 1))]


def test_the_majority_of_a_width_counts_rows_not_runs() -> None:
    """Codex's item 1 (LANE HB RULINGS 8 (1)): `label_figure_openings` weighed runs, so 8,000 cells of one level holding
    two runs of six figures (16,000 runs) outweighed 12,000 keys held back once each; the width named no opening and the
    twin wrote 7,202 real keys at 20,000 rows. The reverse, one published level of one run on 11,000 rows beside 4,500
    held-back cells of three runs each, named a width mostly published; since the independent verify 2 of close round 2
    (LANE HB RULINGS 11 (1) (b)) it is named, for no published level writes the held cells' form, and beside a
    published level of their form the width is a code's, its rows mostly published. A width counts once a cell.
    Mutant: each run counted."""
    cells = hunt.SHAPES["two_runs_published"][0](20_000)  # type: ignore[operator]
    assert "6" in taxonomy.label_figure_openings(cells, ["R100000X200000"], 11)
    reverse = (["C500000"] * 11_000 + [f"R{100000 + k}X{200000 + k}Y{300000 + k}" for k in range(4_500)]
               + ["pending"] * 4_500)
    assert "6" in taxonomy.label_figure_openings(reverse, ["C500000", "pending"], 11)
    worn = reverse[:11_000] + ["C500000X500000Y500000"] * 11 + reverse[11_000:-11]
    assert "6" not in taxonomy.label_figure_openings(worn, ["C500000", "C500000X500000Y500000", "pending"], 11)


def test_a_note_in_any_script_beside_padded_keys_is_set_aside() -> None:
    """Codex's item 2 (LANE HB RULINGS 8 (1)): the note rule read ASCII letters alone, so `0001000` upward once each
    beside a note in another script read as numbers beside labels with no question (9,997 real keys at 20,000 rows).
    A letter is any letter, of any script -- an ASCII letter or any character outside ASCII but a mark grouping figures
    -- in Chinese, Cyrillic, Arabic and accented Latin alike, and at the table's floor (eleven keys). Mutant: ASCII
    letters alone."""
    for note in ("门诊 12", "осмотр врача 5",
                 "مراجعة 5", "réévalué 12"):
        assert asking._a_note_beside_padded_keys(note), note
    assert not asking._a_note_beside_padded_keys("门诊 1234") and not asking._a_note_beside_padded_keys("12 34")
    assert not asking._a_note_beside_padded_keys("12 345") and not asking._a_note_beside_padded_keys("12 34")
    for name in ("pad_notes_cjk", "pad_notes_cyrillic", "pad_notes_arabic", "pad_notes_floor"):
        assert asking._padded_beside_words(hunt.SHAPES[name][0](20_000)), name  # type: ignore[operator]


def test_padded_keys_among_notes_in_another_script_write_no_real_key_at_the_floor(tmp_path: pathlib.Path) -> None:
    """Codex's item 2 at 20,000 rows, alone in its table (a padded key column asked the person question holds every
    other key column of its table): keys once each beside notes in Cyrillic holding a small number read as numbers
    beside labels on 46e63afe, 9,997 twin cells real. Held, 0 equal and 0 holding a real run. Mutant: ASCII letters
    alone."""
    blocks, columns, twins = _one_table(tmp_path, ("pad_notes_cyrillic",))
    real, twin = columns["pad_notes_cyrillic"], twins["pad_notes_cyrillic"]
    assert blocks["pad_notes_cyrillic"]["role"] == "identifier"
    assert hunt.cells_holding_a_real_run(real, twin, frozenset()) == 0
    assert not set(twin) & {cell for cell in real if re.fullmatch(r"\d+", cell)}


def test_key_3_lets_no_longer_run_carry_a_real_padded_one() -> None:
    """Codex's item 3 (LANE HB RULINGS 8 (1)): beside key `3` alone, a run of any width stood, so `5390206WX` kept a real
    `0206` (2,750 twin cells at 20,000 rows); and the filling of a run padded it by noughts. Every real run key `3` names
    opens with a nought, so a run holding a nought three figures or more from its end is renamed whole, as written,
    never padded, to a run with none there, product and oracle alike (A-P4-59), whatever width is named beside.
    Mutants: the nought test withdrawn (both the stand and the oracle); the run named on its merged figures."""
    real = hunt.SHAPES["padded_inside_4"][0](20_000)  # type: ignore[operator]
    runs = _real_runs(real, set())
    openings = {int(width): opening for width, opening in taxonomy.label_figure_openings(real, ["pending"], 11).items()}
    assert openings == {3: ""}
    cells = ["5390206WX", "1015238GC", "0206AB", "000206", "0000206BA", "12345678", "1230", "5390206WX"]
    written, _spent = generation._figure_runs_off_the_real(cells, _text_facts(openings), ())
    assert not _holding(runs, written), written
    assert not generation._figure_run_stands("5390206", openings, "5390206")
    assert generation._figure_run_stands("5391236", openings, "5391236") and generation._figure_run_stands("1230", openings, "1230")
    assert written[5] == "12345678" and written[6] == "1230" and written[0] == written[7], written
    assert all(len(after) >= len(before) for before, after in zip(cells, written)) and len(set(written)) == len(set(cells))
    oracle = _the_oracle()
    assert oracle.figure_runs_off_the_real({"figure_openings": {"3": ""}}, cells) == written
    # ...every renaming, with and without a width named beside `3`: no nought three figures or more from its end.
    for names in ({3: ""}, {3: "", 6: "9|8"}, {3: "", 4: "9"}, {3: "", 6: "98"}):
        taken: "dict[str, bool]" = {}
        steps: "dict[int, int]" = {}
        for name in [f"{k:04d}" for k in range(1, 1000)] + [f"{k:07d}" for k in range(1, 1000)] + ["123456", "9123456"]:
            spelled = generation._renamed_run(name, names, taken, steps, _none_absent(), [0, 0])
            assert len(spelled) >= len(name) and (set(spelled) == {"0"} or "0" not in spelled[:-3]), (names, name, spelled)
        said = {"figure_openings": {f"{width}": names[width] for width in names}}
        many = cells + [f"{k:07d}X" for k in range(1, 400)]
        product, _spent = generation._figure_runs_off_the_real(many, _text_facts(names), ())
        assert oracle.figure_runs_off_the_real(said, many) == product, names


def test_a_rebuilt_cell_is_never_a_declared_absent_spelling() -> None:
    """Codex's item 4 (LANE HB RULINGS 8 (2)): the renaming asked its new run `900000` alone, so `A187860` was rebuilt
    as a declared `A900000` and the twin wrote 12 absent cells for 11. The whole rebuilt cell is read; one spelled
    absent takes its first renamed run's next spelling, every cell holding it alike, product and oracle alike
    (A-P4-59). Mutant: the rebuilt cell not read."""
    cells = [f"A{187860 + k}" for k in range(5)] + [f"B{187860 + k}" for k in range(3)] + ["pending"]
    facts = _text_facts({6: "9"})
    written, _spent = generation._figure_runs_off_the_real(cells, facts, ("A900000",))
    assert "A900000" not in written and len(set(written)) == len(set(cells)), written
    assert written[0][1:] == written[5][1:] and written[0] != "A900000" and written[0][:2] == "A9", written
    oracle = _the_oracle()
    assert oracle.figure_runs_off_the_real({"figure_openings": {"6": "9"}, "missing_by_source": {"A900000": 1}}, cells) == written


def test_a_rebuilt_cell_absent_through_a_spent_run_tries_its_other_runs() -> None:
    """Codex's review of close round 2, item 1 (LANE HB RULINGS 9 (1)): beside key `3` with `4` opening `98`, the
    first run of `X01234Y0001` has no room but noughts, so the cell was rebuilt as the declared `X00000Y9800` and the
    retry asked that spent run again and stopped. The cell's other renamed runs are asked before it is written absent,
    product and oracle alike (A-P4-59). Where the second run is spent too, the cell stays absent (limit (ac)). Since
    LANE HB RULINGS 10 (2) a spent run is noughts one figure wider than every width named or written (six here), so
    Codex's own cell is written the present `X000000Y9800` and the case declares that spelling absent: the second run
    then takes `9801`. Mutant: the first run alone asked."""
    oracle = _the_oracle()
    openings = {3: "", 4: "98"}
    said = {"figure_openings": {"3": "", "4": "98"}, "missing_by_source": {"X000000Y9800": 11}}
    written, _spent = generation._figure_runs_off_the_real(["X01234Y0001"], _text_facts(openings), ("X00000Y9800",))
    assert written == ["X000000Y9800"], written
    written, _spent = generation._figure_runs_off_the_real(["X01234Y0001"], _text_facts(openings), ("X000000Y9800",))
    assert written == ["X000000Y9801"], written
    assert oracle.figure_runs_off_the_real(said, ["X01234Y0001"]) == written
    # ...a cell holding the same second run beside it moves with it: every cell holding a run alike.
    cells = ["X01234Y0001", "W0001", "X01234Y0002"]
    written, _spent = generation._figure_runs_off_the_real(cells, _text_facts(openings), ("X000000Y9800",))
    assert written == ["X000000Y9802", "W9802", "X000000Y9801"], written
    assert oracle.figure_runs_off_the_real(said, cells) == written
    # ...the room of four figures opening `98` spent first, the second run is spent too: the cell stays absent.
    spent = [f"Z{k:04d}" for k in range(2, 102)] + ["X01234Y0001"]
    written, _spent = generation._figure_runs_off_the_real(spent, _text_facts(openings), ("X000000Y000000",))
    assert written[-1] == "X000000Y000000" and len(set(written[:-1])) == 100, written[-3:]
    said = {"figure_openings": {"3": "", "4": "98"}, "missing_by_source": {"X000000Y000000": 11}}
    assert oracle.figure_runs_off_the_real(said, spent) == written


def test_absent_spellings_read_once_answer_as_each_spelling_read_in_turn() -> None:
    """LANE HB RULINGS 9 (2): the run walk reads a column's absent spellings once (`_absent_spellings_read`) and asks
    each filling and rebuilt cell in time independent of how many there are; it answers as `_is_a_hole_spelling`
    reading them in turn does, the vocabulary, a member of the exact vocabulary byte for byte, folding and the exact
    number included. Mutants: the number reading left out; the exact member folded."""
    texts = ["9000", "9000.0", "+9000", "9e3", "9,000", "(9000)", "-9000", "NA", "na", " NaT", "NaT", "nat", "A900000",
             "a900000", " A900000 ", "0009000", "9000.5", "9.0E+3", "", "-", "N/A", "pending", "-0", "0", "00"]
    for holes in ((), ("9000",), ("-9000.0",), ("NaT",), ("A900000",), ("na",), ("9e3", "pending"), ("0",), ("00.0",)):
        read = generation._absent_spellings_read(holes)
        for text in texts:
            assert generation._is_an_absent_spelling(text, read) == generation._is_a_hole_spelling(text, holes), (
                holes, text)


def _the_walk_reading_again(cells: "list[str]", openings: "dict[int, str]", holes: "tuple[str, ...]") -> "list[str]":
    """The run walk as committed before LANE HB RULINGS 9 (2) (343c29c2): every planned cell rebuilt, and the column
    read again from its first cell, after each renaming of the absence repair. The reference of the differential case."""
    absent = generation._absent_spellings_read(holes)
    distinct = list(dict.fromkeys(cells))
    taken: "dict[str, bool]" = {}
    for cell in distinct:
        for whole, start, end in generation._figure_runs_of(cell):
            if end - whole >= 4:
                taken[cell[start:end]] = True
    wide = 1 + max([*openings, *[generation._longest_figure_run(cell) for cell in distinct]])
    renamed: "dict[str, str]" = {}
    steps: "dict[int, int]" = {}
    plan: "dict[str, list[tuple[int, int, str]]]" = {}
    counts = [0, 0]
    for cell in distinct:
        if generation._is_a_hole_spelling(cell, holes):
            continue
        parts: "list[tuple[int, int, str]]" = []
        for whole, start, end in generation._figure_runs_of(cell):
            if end - whole < 4 or generation._figure_run_stands(cell[start:end], openings, cell[whole:end]):
                continue
            name = cell[whole:end] if 3 in openings else cell[start:end]
            if name not in renamed:
                renamed[name] = generation._renamed_run(name, openings, taken, steps, absent, counts, wide)
            parts += [(whole, end, name)]
        if parts:
            plan[cell] = parts
    if not plan:
        return cells
    moved = generation._runs_rebuilt(plan, renamed)
    tried: "dict[tuple[str, str], bool]" = {}
    again = True
    while again:
        again = False
        for cell in plan:
            if not generation._is_a_hole_spelling(moved[cell], holes):
                continue
            for _whole, _end, name in plan[cell]:
                tried[(name, renamed[name])] = True
                fresh = generation._renamed_run(name, openings, taken, steps, absent, counts, wide)
                if (name, fresh) in tried:
                    continue
                renamed[name] = fresh
                moved = generation._runs_rebuilt(plan, renamed)
                again = True
                break
            if again:
                break
    return [moved[cell] if cell in moved else cell for cell in cells]


def test_the_absence_repair_writes_what_reading_the_column_again_wrote() -> None:
    """LANE HB RULINGS 9 (2), the differential case: on 2,000 seeded random columns -- one to three runs a cell, noughts
    before them or none, letters between, beside `3` or not, rooms of one or two figures' openings spent, absent
    spellings taken from the cells the walk writes, numbers among them written another way -- the heap and the index of
    runs to cells write exactly the cells the walk that rebuilt every cell and read the column again wrote. Mutants:
    the cells holding the renamed run left unrebuilt; the heap taken in the order of arrival."""
    import random
    # ...first, a column where the order decides the cells: `B9000` and `D9002` read as absent at once; renaming the
    # run `1111` makes the earlier `A9003` absent, which the walk takes before `D9002` (the first absent cell), so
    # `1111` takes `9004` and `3333` `9005`; taken in the order of arrival they would be `9005` and `9004`.
    order = ["A1111", "B1111", "C2222", "D3333"]
    holes = ("A9003", "B9000", "D9002")
    written, _spent = generation._figure_runs_off_the_real(order, _text_facts({4: "9"}), holes)
    assert written == _the_walk_reading_again(order, {4: "9"}, holes) == ["A9004", "B9004", "C9001", "D9005"], written
    draw = random.Random(20261103)
    choices = ({4: "9"}, {4: "98"}, {4: "9|8"}, {3: "", 4: "98"}, {3: "", 4: ""}, {3: ""}, {5: "9"}, {6: "9"},
               {4: "9", 6: "9|8"}, {3: "", 5: "9|8|7"}, {4: ""}, {3: "", 4: "9"})
    repaired = 0
    for _case in range(2000):
        openings = choices[draw.randrange(len(choices))]
        cells: "list[str]" = []
        for _cell in range(draw.choice((6, 12, 30, 130))):
            cell = draw.choice(("", "A", "XB", "Q"))
            for _run in range(draw.choice((1, 1, 2, 3))):
                width = draw.randrange(1, 8)
                figures = f"{draw.randrange(10 ** (width - 1), 10 ** width)}"
                cell += "0" * draw.choice((0, 0, 1, 3)) + figures + draw.choice(("", "Y", "-", ".0"))
            cells += [cell]
        plain, _spent = generation._figure_runs_off_the_real(cells, _text_facts(openings), ())
        holes: "list[str]" = []
        for cell in plain:
            if cell not in cells and draw.random() < 0.3:
                holes += [cell if draw.random() < 0.7 else cell + ".00"]
        holes += [f"{9800 + draw.randrange(4)}"] if draw.random() < 0.2 else []
        absent = tuple(sorted(set(holes)))
        written, _spent = generation._figure_runs_off_the_real(cells, _text_facts(openings), absent)
        assert written == _the_walk_reading_again(cells, openings, absent), (openings, cells, absent)
        repaired += written != plain
    assert repaired >= 300, repaired


def test_the_absence_repair_is_linear_in_the_cells(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of close round 2, item 2 (LANE HB RULINGS 9 (2)): `"B"` keys, then `"A"` keys whose renamed runs
    each land on a declared absent spelling (openings `{6: "9"}`, the last tenth absent), rebuilt every planned cell
    and read the column again for each: 161 whole rebuilds at 1,600 cells and 9.09 s. Machine-free: the cells rebuilt
    and the absence readings grow with the cells, at most four readings a cell and one rebuild a cell beside two a renaming. Mutant: the
    reading again from the first cell after each renaming."""
    calls = {"rebuilt": 0, "read": 0}
    rebuilt, read = generation._cell_rebuilt, generation._is_an_absent_spelling

    def counted_rebuilt(*arguments: object) -> str:
        calls["rebuilt"] += 1
        return rebuilt(*arguments)  # type: ignore[arg-type]

    def counted_read(*arguments: object) -> bool:
        calls["read"] += 1
        return read(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_cell_rebuilt", counted_rebuilt)
    monkeypatch.setattr(generation, "_is_an_absent_spelling", counted_read)
    for n in (1600, 6400):
        h = n // 10
        cells = [("B" if i < n - h else "A") + str(100000 + i) for i in range(n)]
        holes = tuple("A" + str(900000 + i) for i in range(n - h, n))
        calls["rebuilt"] = calls["read"] = 0
        written, _spent = generation._figure_runs_off_the_real(cells, _text_facts({6: "9"}), holes)
        assert not set(written) & set(holes) and len(set(written)) == n, n
        assert calls["rebuilt"] <= n + 2 * h and calls["read"] <= 4 * n, (n, calls)


def test_the_oracle_reads_a_declared_number_as_a_number_as_the_product_does() -> None:
    """Codex's review of close round 2, item 3 (LANE HB RULINGS 9 (3)): the oracle's whole-cell check compared folded
    text, so `-1234` renamed onto `-9000` beside a declared `-9000.0` stayed `-9000` there while the product, matching
    the exact number as the contract's `declaration_matching` clause says, wrote `-9001`. The oracle reads a declared
    number as a number from that clause, written apart from the product's reader: Codex's case, and a leading plus,
    trailing noughts and the power of ten each both ways -- the absent value in the plain form and the cell renamed
    onto the spelled form, and the reverse -- write the same cells, product and oracle (A-P4-59); and the two readers
    agree on every spelling of a corpus of the format's forms. Mutants: the oracle's number reading left out; the
    accounting brackets read as no number."""
    oracle = _the_oracle()
    cases = (
        (["-1234"], "-9000.0", ["-9001"]),
        (["1234"], "9000.00", ["9001"]),
        (["-1234.00"], "-9000", ["-9001.00"]),
        (["1234"], "+9000", ["9001"]),
        (["+1234"], "9000", ["+9001"]),
        (["1234"], "9.0E+3", ["9001"]),
        (["-1234e0"], "-9000", ["-9001e0"]),
        (["(1234)"], "-9000", ["(9001)"]),
    )
    for cells, absent, expected in cases:
        written, _spent = generation._figure_runs_off_the_real(cells, _text_facts({4: "9"}), (absent,))
        assert written == expected, (cells, absent, written)
        said = {"figure_openings": {"4": "9"}, "missing_by_source": {absent: 11}}
        assert oracle.figure_runs_off_the_real(said, cells) == written, (cells, absent)
    corpus = ["(9000)", "\u22129000", "9000-", " 9000 ", "9,000", "9 000", "9.000,0", "+9000", "9e3", "9E+3", "09000",
              "9000.", ".9e4", "0x10", "9_000", "9000%", "-0", "1e400", "1e308", "1.8e308", "1e-320", "2e-324",
              "5e-324", "(+9000)", "( 9000 )", "(9,000)", "-(9000)", "+ 9000", "1,234.5678", "12,3456", "1,23,456",
              "1 234 567", "1\u00a0234", "1\u202f234", "1\u2009234", "1'234", "1\u2019234", "1.234.567", "(\u22129000)",
              "-.5", "+.5e1", "1e", "e5", "00", "-00.000", "\t9000\n", "1,234 567", "0,123", "1,000.", "(.5)", "()",
              "9.e3", ".e3", "9..0", "1.234,5", "-9.0E+3", "1e5e3", "1,0000", ",123", "1,,234", "A900000", "NA"]
    for text in corpus:
        assert oracle.number_the_format_holds(text) == parsing.exact_of_spelling(text), text


def test_the_driver_names_as_many_run_shapes_as_the_hunt_holds() -> None:
    """Codex's review of close round 2, item 4 (LANE HB RULINGS 9 (4)): `K-HZ-13`'s driver, the changelog and the plan
    said the round added thirteen shapes where the registry holds twelve. The driver's docstring states the count in
    words and it is read here against the registry's shapes of kind `runs`, so the two cannot drift apart. Mutant: a
    shape of that kind added to the registry and not to the docstring."""
    import ast
    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_held_layouts.py"
    text = " ".join((ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or "").split())
    words = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen"
             " eighteen nineteen twenty").split()
    found = re.search(r"on the (\w+) shapes of `hunt\.SHAPES` whose kind is `runs`", text)
    assert found is not None and found.group(1) in words, text[-600:]
    runs = [name for name, shape in hunt.SHAPES.items() if shape[3] == "runs"]
    assert words.index(found.group(1)) + 1 == len(runs), (found.group(1), runs)
    for name in runs:
        assert f"`{name}`" in text or name.startswith("padded_inside_"), name


def test_the_spent_room_is_counted_on_what_is_written() -> None:
    """Codex's item 5 (LANE HB RULINGS 8 (2)): the report counted a run wider beside the narrowest width named, so 1,099
    six-figure runs written as five figures led by a nought were called wider, and the first nought conversion at each
    width went uncounted (2,785 reported for 2,788). Measured on what is written: a run is wider where its spelling is
    longer than the run as written, noughts before it included, and every spelling of noughts alone is counted. Beside
    key `3` (LANE HB RULINGS 10 (1)): `0000206` renamed whole to `1111000` counts no run wider, and a padded run whose
    room is spent counts one written as noughts. Mutants: the width read against the narrowest; the first noughts
    uncounted; the width read against the merged run (M37a)."""
    # ...every room of four figures and under spent by runs that stand: one six-figure run is noughts, one figure
    # wider than every width named or written (LANE HB RULINGS 10 (2)), the next is `99` and three figures, led by a
    # nought to its six, no wider than written.
    stand = [f"{k}" for k in range(9000, 10000)] + [f"{k:04d}" for k in range(1, 1000)]
    written, spent = generation._figure_runs_off_the_real(stand + ["123456", "234567"], _text_facts({4: "9"}), ())
    assert written[-2:] == ["0000000", "099000"] and spent == [1, 1], (written[-2:], spent)
    cells = [f"R{k}" for k in range(1000, 9000)] + [f"R{k}" for k in range(100000, 108000)]
    written, spent = generation._figure_runs_off_the_real(cells, _text_facts({4: "9", 6: "9|8|7|6|5|4|3|2"}), ())
    wider: "dict[str, bool]" = {}
    noughts: "dict[str, bool]" = {}
    for before, after in zip(cells, written):
        if before == after:
            continue
        if len(after) > len(before):
            wider[before[1:]] = True
        if set(after[1:]) == {"0"}:
            noughts[before[1:]] = True
    assert spent == [len(wider), len(noughts)] and spent[1] > 0, (spent, len(wider), len(noughts))
    # ...beside key `3`, read on the runs as written: no wider, and one padded run spent to noughts.
    written, spent = generation._figure_runs_off_the_real(["0000206"], _text_facts({3: ""}), ())
    assert written == ["1111000"] and spent == [0, 0], (written, spent)
    padded = [f"Z{k:04d}" for k in range(2, 102)] + ["X0001"]
    written, spent = generation._figure_runs_off_the_real(padded, _text_facts({3: "", 4: "98"}), ())
    assert written[-1] == "X00000" and len(set(written[:-1])) == 100 and spent == [1, 1], (written[-2:], spent)


def test_keys_zero_filled_from_nought_keep_their_published_form(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Rule 42 as LANE HB RULINGS 13 restates it, and limit (af) at the original width, OPEN-held, owner lane HB2 (the
    independent verify of close round 2, item 2; LANE HB RULINGS 10 (2)), one table at 20,000 rows, the label writer:
    keys `Q00000` and `ACC0000000` upward once each beside `pending`, and `Q00000` upward beside four-figure codes and
    a letter, read as labels with no question. Beside `3` and an empty opening every held stand-in's room is spent. A
    published form writes a run of the spent runs' own widths, so their noughts keep those widths and the key columns'
    twins wear only forms the real columns hold (one figure wider, rule 42 wrote every stand-in of the key columns in a
    form neither holds). The price is limit (af): the one real key of noughts alone, the first key of a sequence
    zero-filled from nought, is written as itself -- 497, 1 and 267 twin cells, all of that one value, as on d9c1c5b2
    (the pushed line wrote 62 other equal cells on the first shape). The counts are held as measured, so a change is
    seen, and on the two key columns no twin cell holds a held real run that is not noughts alone (the codes' column
    keeps limit (ae)'s runs inside, owner HB2: 2,694 cells, each figures alone, a held code read as a number, which the
    report's sentence names as its third case). Mutants: the noughts one figure wider at every width, rule 42 as it
    stood (K42e); the sentence of two cases (finding 2 of the independent verify of batch 4n's fix round)."""
    shapes = {
        "noughts_once": hunt._beside_a_word(20_000, lambda k: f"Q{k:05d}"),
        "noughts_acc_once": hunt._beside_a_word(20_000, lambda k: f"ACC{k:07d}"),
        "noughts_beside_codes": hunt._beside_a_word(
            20_000, lambda k: f"{k % 999 + 1:04d}E{k % 7}" if k % 2 else f"Q{k:05d}", 0.3),
    }
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, "ref", (), "runs"))
    names = tuple(shapes)
    blocks, columns, twins = _one_table(tmp_path, names)

    def form_of(cell: str) -> str:
        return re.sub(r"[A-Za-z]", "@", re.sub(r"[0-9]", "%", cell))

    taken: "dict[str, int]" = {}
    for name in names:
        assert blocks[name]["role"] == "long_tail_labels", (name, blocks[name]["role"])
        published: "dict[str, bool]" = {}
        hunt._spellings_of(blocks[name], published)
        held = {cell for cell in columns[name] if re.search(r"\d", cell) and cell not in published}
        equal = {cell for cell in twins[name] if cell in held}
        assert len(equal) <= 1 and all(set(re.sub(r"[^0-9]", "", cell)) == {"0"} for cell in equal), (name, sorted(equal)[:3])
        taken[name] = sum(1 for cell in twins[name] if cell in held)
        runs = {run for cell in held for run in re.findall(r"\d{4,}", cell) if run.strip("0")}
        widths = {len(run) for run in runs}
        holding = [cell for cell in twins[name] if any(
            span[at:at + width] in runs for span in re.findall(r"\d{4,}", cell) for width in widths
            for at in range(len(span) - width + 1))]
        if name == "noughts_beside_codes":
            # ...where limit (ae)'s runs stand inside, owner HB2 (the independent verify of batch 4n's fix round, finding
            # 2; LANE I4m RULINGS 15 (4)): every cell holding a held real run is a held code the column reads as a
            # number, written as figures alone, the report's third case.
            assert all(re.fullmatch(r"\d+", cell) for cell in holding), [cell for cell in holding if not cell.isdigit()][:3]
            taken["codes_holding_a_real_run"] = len(holding)
            continue
        forms = {form_of(cell) for cell in columns[name]}
        assert not [cell for cell in twins[name] if form_of(cell) not in forms], (name, twins[name][:3])
        assert not holding, name
    assert taken == {"noughts_once": 497, "noughts_acc_once": 1, "noughts_beside_codes": 267,
                     "codes_holding_a_real_run": 2_694}, taken
    # ...and the twin's report says so (Codex's review of batch 4n, item 3; LANE I4m RULINGS 14 (4)): it said no run
    # a made-up label writes is a real one or holds one while `Q00000` stood in 497 cells; it names the noughts alone
    # and the one real value they may spell. Mutant: the sentence as it stood.
    report = " ".join((tmp_path / "one-table" / "t-twin-report.txt").read_text("utf-8").split())
    assert " ".join(generation._RUNS_OFF_THE_REAL_LABELS.split()) in report
    assert "noughts alone, a spelling one real value may also have" in report
    assert "is a real one or holds one, and the room a width leaves was spent" not in report
    # ...and it names the third case the codes' column writes (finding 2 of the independent verify; LANE I4m RULINGS 15
    # (4)): it named two while the codes' column held real runs inside its numbers. Mutant: the sentence of two cases.
    assert "except in three cases" in report
    assert "a held label the column reads as a number is written as a number, whose figures are not kept off the real runs" in report


def test_an_opening_names_each_figure_once() -> None:
    """Codex's item 6 (LANE HB RULINGS 8 (2)): the loader took any number of copies of one figure joined by `|` (a
    description of one opening of 100,000 `9`s loaded, and its walk asked each copy in turn, 100,001 checks for
    1,001). Each figure is named at most once, so nine at most; a description repeating one is refused. Mutant: the
    repeat allowed."""
    assert not parsing.is_a_figure_opening(4, "9|9") and not parsing.is_a_figure_opening(4, "|".join(["9"] * 100_000))
    assert parsing.is_a_figure_opening(4, "9|8|7|6|5|4|3|2|1") and not parsing.is_a_figure_opening(4, "9|8|7|6|5|4|3|2|1|9")
    assert not profile._is_figure_opening("9|8|9")
    with pytest.raises(errors.ProfileError):
        contract._figure_openings({"figure_openings": {"4": "9|8|9"}}, "column 'ref'")
    assert contract._figure_openings({"figure_openings": {"4": "9|8"}}, "column 'ref'") == {4: "9|8"}


def test_codex_s_label_shapes_write_no_real_run_at_the_floor(tmp_path: pathlib.Path) -> None:
    """Codex's items 1, 3 and 4 at 20,000 rows, one table, one case the label writer (each read as labels with no
    question). On 46e63afe: a level of two runs beside keys once each, 7,202 twin cells real; runs zero-filled to four
    and seven figures, 2,750 cells holding a real padded run; keys beside eleven cells of a declared absent spelling,
    12 absent twin cells. No twin cell equals or holds a held-back real run, and the absent cells stay 11. Mutants: the
    runs counted; the nought test withdrawn; the rebuilt cell not read."""
    names = ("two_runs_published", "padded_inside_4", "rebuilt_as_absent")
    blocks, columns, twins = _one_table(tmp_path, names, typed=("--missing-value", "A900000"))
    for name in names:
        assert blocks[name]["role"] == "long_tail_labels", (name, blocks[name]["role"])
        published: "dict[str, bool]" = {}
        hunt._spellings_of(blocks[name], published)
        assert hunt.cells_holding_a_real_run(columns[name], twins[name], frozenset(published)) == 0, name
    assert twins["rebuilt_as_absent"].count("A900000") == 11
    assert twins["two_runs_published"].count("R100000X200000") == 8_000


# -- fix 3 of close round 2: the independent verify 2 (wave6/HB-close2-verify2.md), LANE HB RULINGS 11 ---------------


def test_keys_beside_a_level_at_a_tie_or_of_another_form_write_no_real_key(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The independent verify 2 of close round 2, item 1 (LANE HB RULINGS 11 (1)), one table at 20,000 rows and one at
    600, the label writer: keys once each beside one published level of two runs on half the rows (`c1_tie`), or two
    such levels (`c1_tie2`); keys beside a published level of their own form (`v_runs_pub_held`); and keys beside
    levels of two runs on 51 % of rows (`v_many400_x`, 400 levels, 12 at 600 rows), each read as labels with no
    question. On 6b3c0e95 no width was named, and 10,000, 10,000, 10,000 and 9,604 twin cells were or held a real key
    at 20,000 rows (300, 300, 300 and 288 at 600). A tie is the keys', and held-back cells of a form no published level
    writes name their width once they reach the floor: no twin cell is a held real cell or holds a held real run, and
    every published level keeps its count. Mutants: the tie a code's (`rows > shown`); the form term withdrawn."""
    def keys(prefix: str, low: int, count: int, suffix: str = "") -> "list[str]":
        return [f"{prefix}{low + k}{suffix}" for k in range(count)]

    carrying: "dict[tuple[int, str], int]" = {}
    for rows in (20_000, 600):
        levels = 400 if rows >= 20_000 else 12
        shapes = {
            "c1_tie": ["R100000X200000"] * (rows // 2) + keys("R", 100000, rows - rows // 2),
            "c1_tie2": (["R100000X200000"] * (rows // 4) + ["R300000X400000"] * (rows // 4)
                        + keys("R", 100000, rows - 2 * (rows // 4))),
            "v_runs_pub_held": ["P123456Q7890"] * (rows // 2) + keys("P", 200000, rows - rows // 2, "Q4444"),
            "v_many400_x": ([f"R{500000 + j % levels}X{200000 + j % levels}" for j in range(51 * rows // 100)]
                            + keys("R", 100000, rows - 51 * rows // 100)),
        }
        for name, cells in shapes.items():
            monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, "ref", (), "runs"))
        (tmp_path / f"{rows}").mkdir()
        blocks, columns, twins = _one_table(tmp_path / f"{rows}", tuple(shapes), rows)
        for name in shapes:
            assert blocks[name]["role"] == "long_tail_labels", (rows, name, blocks[name]["role"])
            published: "dict[str, bool]" = {}
            hunt._spellings_of(blocks[name], published)
            carrying[(rows, name)] = hunt.cells_holding_a_real_run(columns[name], twins[name], frozenset(published))
            for level in blocks[name]["levels"]:  # type: ignore[union-attr]
                label = level["label"]
                assert twins[name].count(label) == columns[name].count(label), (rows, name, label)
    assert not [key for key in carrying if carrying[key]], sorted(carrying.items())


def _label_figure_openings_reading_every_form(
    present: "list[str]", labels: "list[object]", floor: int, census: "dict[str, int] | None" = None
) -> "dict[str, str]":
    """`taxonomy.label_figure_openings` as fix 3 of close round 2 committed it (e8261e63): the census form of every
    published spelling and of every held-back cell holding a run read, whatever the majority. The reference of the
    differential case of LANE HB RULINGS 14."""
    openings = taxonomy.figure_openings(present, floor)
    if not openings:
        return {}
    named: "dict[str, bool]" = {}
    for label in labels:
        named[parsing.folded(f"{label}")] = True
    forms: "dict[str, int]" = {} if census is None else census
    spelled: "dict[str, bool]" = {}
    worn: "dict[str, bool]" = {}
    for cell in present:
        if cell not in spelled and parsing.folded(cell) in named:
            spelled[cell] = True
            worn[parsing.census_form(cell, forms)] = True
    held: "dict[str, int]" = {}
    shown: "dict[str, int]" = {}
    unworn: "dict[str, int]" = {}
    for cell in present:
        published = cell in spelled
        tally = shown if published else held
        once: "dict[str, bool]" = {}
        for width in taxonomy._figure_widths_of(cell):
            once[width] = True
        foreign = False
        if once and not published:
            form = parsing.census_form(cell, forms)
            foreign = form != "" and form not in worn
        for width in once:
            tally[width] = (tally[width] if width in tally else 0) + 1
            if foreign:
                unworn[width] = (unworn[width] if width in unworn else 0) + 1
    kept: "dict[str, str]" = {}
    for width in openings:
        rows = held[width] if width in held else 0
        if rows >= (shown[width] if width in shown else 0) or (unworn[width] if width in unworn else 0) >= floor:
            kept[width] = openings[width]
    return kept


def test_the_form_term_reads_forms_only_where_the_majority_leaves_a_width_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """LANE HB RULINGS 14: fix 3's form term read the census form of every held-back cell holding a run of figures, so
    1,000 stamps beside rare words asked `parsing.shape_form` 2,941 times, past the census's bound of two a cell (H7).
    The form term changes the answer only for a width the majority leaves out, so the forms are read only once such a
    width exists, for the published spellings and the held-back cells holding it. The answer is fix 3's for every
    input: on 2,000 seeded random label columns -- levels and keys of one to three runs of four to nine figures, noughts
    before them or none, letters between, lower case or upper, words, a census or none, floors of 2, 3 and 11 -- and on
    fix 3's label shapes at 600 rows, the same widths and openings in the same order. A column whose widths the
    majority all names reads no form; one that leaves a width out reads one form a published spelling and at most one a
    held-back cell holding that width, stopping once each such width has the floor's cells of an unworn form (twelve
    levels of two runs beside keys once each: 12 and 11). Mutants: the forms read whatever the majority; the stop
    withdrawn; the tie read as a code's; the form term withdrawn. H7 is red on fix 3's pass itself."""
    import random

    asked = {"forms": 0}
    census_form = parsing.census_form

    def counted(text: str, census: "dict[str, int]") -> str:
        asked["forms"] += 1
        return census_form(text, census)

    draw = random.Random(20261104)

    def run_of(width: int) -> str:
        return f"{draw.randrange(10 ** (width - 1), 10 ** width)}"

    def spelled() -> str:
        cell = draw.choice(("", "R", "ab", "Q", "X-"))
        for _run in range(draw.choice((1, 1, 2, 3))):
            cell += "0" * draw.choice((0, 0, 1, 2)) + run_of(draw.randrange(4, 10)) + draw.choice(("", "X", "y", "-", ".0"))
        return cell if draw.random() < 0.8 else cell.upper()

    columns: "list[tuple[list[str], list[object], int]]" = []
    for _case in range(2000):
        levels = [spelled() for _level in range(draw.choice((1, 2, 5, 40)))]
        rows = draw.choice((40, 120, 300))
        share = draw.choice((0.3, 0.45, 0.5, 0.55, 0.7, 0.9))
        keys = [spelled() for _key in range(draw.choice((5, 30, 200)))]
        cells = [levels[draw.randrange(len(levels))] if draw.random() < share else
                 (draw.choice(keys) if draw.random() < 0.8 else draw.choice(("pending", "n/a", "A1-2")))
                 for _row in range(rows)]
        labels: "list[object]" = [*dict.fromkeys(levels + ["pending"])] if draw.random() < 0.7 else [*levels]
        columns += [(cells, labels, draw.choice((2, 3, 11)))]
    for rows in (600,):
        columns += [
            (["R100000X200000"] * (rows // 2) + [f"R{100000 + k}" for k in range(rows - rows // 2)], ["R100000X200000"], 11),
            (["R100000X200000"] * (rows // 4) + ["R300000X400000"] * (rows // 4)
             + [f"R{100000 + k}" for k in range(rows - 2 * (rows // 4))], ["R100000X200000", "R300000X400000"], 11),
            (["P123456Q7890"] * (rows // 2) + [f"P{200000 + k}Q4444" for k in range(rows - rows // 2)], ["P123456Q7890"], 11),
            ([f"R{500000 + j % 12}X{200000 + j % 12}" for j in range(51 * rows // 100)]
             + [f"R{100000 + k}" for k in range(rows - 51 * rows // 100)],
             [f"R{500000 + j}X{200000 + j}" for j in range(12)], 11),
        ]
    monkeypatch.setattr(parsing, "census_form", counted)
    short_columns = 0
    for cells, labels, floor in columns:
        counts: "dict[str, int]" = {}
        for cell in cells:
            form = parsing.shape_form(cell)
            counts[form] = (counts[form] if form in counts else 0) + 1
        census = None if draw.random() < 0.3 else {form: counts[form] for form in counts if counts[form] >= floor}
        before = _label_figure_openings_reading_every_form(cells, labels, floor, census)
        asked["forms"] = 0
        after = taxonomy.label_figure_openings(cells, labels, floor, census)
        assert list(after.items()) == list(before.items()), (labels, floor, cells[:6], before, after)
        named = {parsing.folded(f"{label}") for label in labels}
        openings = taxonomy.figure_openings(cells, floor)
        shown_rows: "dict[str, int]" = {}
        held_rows: "dict[str, int]" = {}
        for cell in cells:
            tally = shown_rows if parsing.folded(cell) in named else held_rows
            for width in set(taxonomy._figure_widths_of(cell)):
                tally[width] = (tally[width] if width in tally else 0) + 1
        short = {width for width in openings if held_rows.get(width, 0) < shown_rows.get(width, 0)}
        if not short:
            assert asked["forms"] == 0, (labels, cells[:6])
            continue
        short_columns += 1
        published = {cell for cell in cells if parsing.folded(cell) in named}
        holding = sum(1 for cell in cells if cell not in published and short & set(taxonomy._figure_widths_of(cell)))
        assert len(published) <= asked["forms"] <= len(published) + holding, (asked["forms"], len(published), holding)
        if labels == [f"R{500000 + j}X{200000 + j}" for j in range(12)]:
            assert asked["forms"] == 12 + 11, asked["forms"]
    assert short_columns >= 200, short_columns


def test_the_noughts_keep_a_width_a_published_form_writes_and_else_pass_every_run() -> None:
    """The independent verify 2 of close round 2, item 3 (LANE HB RULINGS 11 (3)), amended to rule 42 as LANE HB
    RULINGS 13 restates it, product and oracle alike (A-P4-59). A published form whose run of figures is the widest
    (`@%%%%%%%`, seven figures) beside cells whose runs are narrower (six at most): the spent run's own width, six, is
    one no published form writes, so it is written as noughts alone one figure wider than that form's run, eight.
    Where a published form writes a run of six figures (`@%%%%%%`), the spent run keeps its six. Mutants: the published
    forms' runs left out of the width (K42c); the noughts one figure wider at every width, rule 42 as it stood (K42e);
    the noughts at the run's own width at every width, as before rule 42 (K42f); the oracle's published-form term
    withdrawn (K42p)."""
    cells = [f"{k}" for k in range(9000, 10000)] + [f"{k:04d}" for k in range(1, 1000)] + ["123456", "234567"]
    facts = dataclasses.replace(_text_facts({4: "9"}), shape_forms={"@%%%%%%%": 11})
    written, spent = generation._figure_runs_off_the_real(cells, facts, ())
    assert written[-2] == "0" * 8 and spent[1] == 1, (written[-2:], spent)
    assert max(len(run) for cell in cells for run in re.findall(r"\d+", cell)) == 6
    oracle = _the_oracle()
    column = {"figure_openings": {"4": "9"}, "shape_forms": {"@%%%%%%%": 11}}
    assert oracle.figure_runs_off_the_real(column, cells) == written
    # ...a published form writing the spent run's own width: its noughts keep that width.
    facts = dataclasses.replace(_text_facts({4: "9"}), shape_forms={"@%%%%%%": 11})
    written, spent = generation._figure_runs_off_the_real(cells, facts, ())
    assert written[-2:] == ["000000", "099000"] and spent == [0, 1], (written[-2:], spent)
    column = {"figure_openings": {"4": "9"}, "shape_forms": {"@%%%%%%": 11}}
    assert oracle.figure_runs_off_the_real(column, cells) == written


def test_real_keys_of_noughts_alone_wider_than_their_form_are_not_written(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Limit (af) (the independent verify 2 of close round 2, item 2; LANE HB RULINGS 11 (2) and 13), one table at
    20,000 rows, the label writer: keys `Q00000` upward once each beside `pending`, the last three real keys `Q000000`,
    `Q0000000` and `Q00000000`; keys of three letters and seven figures, the last two real keys of eight and nine
    noughts. One figure wider at every width, rule 42 wrote the real `Q000000` and the real eight noughts (497 and 1
    twin cells). The spent runs now keep the width their published form writes, so no twin cell is one of the wider
    keys; the equal cells are the one real key of noughts alone at that width, the first key of each sequence (497 and
    1, limit (af) at the original width, owner lane HB2). The counts are held as measured, so a change is seen. Mutant:
    the noughts one figure wider at every width, rule 42 as it stood (K42e)."""
    shapes = {
        "noughts_wider": hunt._beside_a_word(20_000, lambda k: f"Q{k:05d}")[:-3] + ["Q000000", "Q0000000", "Q00000000"],
        "noughts_acc_wider": (hunt._beside_a_word(20_000, lambda k: f"ACC{k:07d}")[:-2]
                              + ["ACC00000000", "ACC000000000"]),
    }
    wider = {"noughts_wider": ("Q000000", "Q0000000", "Q00000000"), "noughts_acc_wider": ("ACC00000000", "ACC000000000")}
    lowest = {"noughts_wider": "Q00000", "noughts_acc_wider": "ACC0000000"}
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, "ref", (), "runs"))
    blocks, columns, twins = _one_table(tmp_path, tuple(shapes))
    taken: "dict[str, int]" = {}
    for name in shapes:
        assert blocks[name]["role"] == "long_tail_labels", (name, blocks[name]["role"])
        published: "dict[str, bool]" = {}
        hunt._spellings_of(blocks[name], published)
        held = {cell for cell in columns[name] if re.search(r"\d", cell) and cell not in published}
        assert not [cell for cell in twins[name] if cell in wider[name]], name
        assert {cell for cell in twins[name] if cell in held} <= {lowest[name]}, name
        taken[name] = sum(1 for cell in twins[name] if cell in held)
    assert taken == {"noughts_wider": 497, "noughts_acc_wider": 1}, taken


# -- batch 4n's fix round: Codex's review of batch 4n, items 1 to 3 (LANE I4m RULINGS 14) -------------------------------


def _alternating(n: int, *makers: "object") -> "list[str]":
    """``n`` cells taken from ``makers`` in turn, each maker given its own count from nought."""
    taken = [0] * len(makers)
    cells: "list[str]" = []
    for row in range(n):
        place = row % len(makers)
        cells += [makers[place](taken[place])]  # type: ignore[operator]
        taken[place] = taken[place] + 1
    return cells


def _uid_columns(n: int) -> "dict[str, list[str]]":
    """Declared identifier columns that name a layout a UID can wear: under a published root of two groups (Codex's
    `1.2.1000` to `1.2.2999`) and under another root, and beside six or eight figures, beside dates written day first
    with points or in ISO, and beside UIDs of one to four groups after the first arc."""
    def uid(k: int) -> str:
        return f"1.2.{1000 + k % 1000}"

    return {
        "uid_root": [f"1.2.{1000 + row % 2000}" for row in range(n)],
        "uid_other_root": [f"2.25.{1000 + row % 2000}" for row in range(n)],
        "uid_beside_six": _alternating(n, uid, lambda k: f"{100000 + k % 1000}"),
        "uid_beside_eight": _alternating(n, uid, lambda k: f"{19400101 + k % 1000}"),
        "uid_beside_days": _alternating(n, uid, lambda k: f"{1 + k % 28}.{1 + k % 12}.{1950 + k % 50}"),
        "uid_beside_iso": _alternating(n, uid, lambda k: f"{1950 + k % 50}-{1 + k % 12:02d}-{1 + k % 28:02d}"),
        "uid_groups": _alternating(n, lambda k: f"1.{1000 + k % 1000}", uid, lambda k: f"1.2.3.{1000 + k % 1000}",
                                   lambda k: f"1.2.3.4.{1000 + k % 1000}"),
    }


def _uids_written(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, rows: int) -> None:
    """The UID columns as one table of ``rows`` rows, each declared an identifier, generated at seed 0: no twin cell is
    a real one, as written or by its merged key, and a column under a published root keeps it on every cell."""
    shapes = _uid_columns(rows)
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, name, (), "keys"))
    typed: "tuple[str, ...]" = ()
    for name in shapes:
        typed = typed + ("--identifier", name)
    blocks, columns, twins = _one_table(tmp_path, tuple(shapes), rows, typed)
    assert blocks["uid_root"]["layout_prefixes"] == {parsing.PREFIX_OF_THE_COLUMN: "1.2."}, blocks["uid_root"]
    for name in shapes:
        assert blocks[name]["role"] == "identifier", (name, blocks[name]["role"])
        real = set(columns[name])
        merged = {parsing.merged_key(cell) for cell in real}
        equal = [cell for cell in twins[name] if cell in real]
        merging = [cell for cell in twins[name] if parsing.merged_key(cell) in merged]
        assert not equal and not merging, (rows, name, len(equal), len(merging), equal[:3], merging[:3])
        root = blocks[name]["layout_prefixes"].get(parsing.PREFIX_OF_THE_COLUMN, "")
        assert all(cell.startswith(root) for cell in twins[name]), (rows, name, root, twins[name][:3])


def test_a_column_naming_a_uid_layout_keeps_its_root_and_writes_no_real_key(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's review of batch 4n, item 1 (LANE I4m RULINGS 14 (2)), one table at 20,000 rows, the identifier writer:
    `1.2.1000` to `1.2.2999` declared an identifier publish the root `1.2.` and wear `%.%.%%%%`, which a date can wear,
    and the date pass wrote them as dates after the final pass had kept them off the real -- 260 twin cells equal to
    26 real keys and 19,740 off the root on 286c8ba6, none on 591b356f or f39334aa. Beside six or eight figures,
    dates or UIDs of other lengths the same layout wrote real keys too (90, 200, 1,229, 672 and 345 twin cells), and
    under the root `2.25.` 20,000 cells lost it. A column naming any layout a UID can wear is left as the final pass
    wrote it: no twin cell is a real key, as written or merged, and the root stays on every cell. Mutant: only a
    rootless column of UIDs alone left (`_rootless_uid_layouts`, the date pass's test on 286c8ba6)."""
    _uids_written(tmp_path, monkeypatch, 20_000)


def test_a_column_naming_a_uid_layout_keeps_its_root_at_the_gate_s_size(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 1 at the gate's size, the same columns at 600 rows through the internal switch: on 286c8ba6 592 of the
    600 cells of `1.2.1000` to `1.2.1599` lost their root. Mutant: as above."""
    _uids_written(tmp_path, monkeypatch, 600)


def test_the_date_pass_leaves_every_column_naming_a_uid_layout_as_the_final_pass_wrote_it() -> None:
    """Item 1, the rule alone, product and oracle (A-P4-59): a layout a UID can wear under a published root, or beside
    figures alone or a date's form, leaves the column as the final pass wrote it; a column of dates whose forms no UID
    can wear is still written as dates by the product (the oracle walks every date of a form, so the frozen vectors
    compare the two there). Mutants: `_names_a_uid_layout` answering only for a rootless column of UIDs alone; the
    oracle's test the same."""
    oracle = _the_oracle()
    column = types.SimpleNamespace(name="ref", time_grain=None)
    passed = ["1.2.9940", "1.2.9941", " 1.2.9942", "1.2.9943"]
    for forms, prefixes in (
        ({"%.%.%%%%": 4}, {parsing.PREFIX_OF_THE_COLUMN: "1.2."}),
        ({"%.%.%%%%": 2, "%%%%%%": 2}, {}),
        ({"%.%.%%%%": 2, "%%%%-%%-%%": 2}, {}),
        ({"%.%%.%%%%": 4}, {parsing.PREFIX_OF_THE_COLUMN: "2.25."}),
    ):
        facts = dataclasses.replace(_uid_facts("%.%.%%%%", "%.%.9%%%", "%%%%%%%%%"), layout_forms=forms,
                                    layout_prefixes=prefixes)
        assert generation._names_a_uid_layout(facts), forms
        walked = ["1.2.1000", "1.2.1001", " 1.2.1002", "1.2.1003"]
        assert generation._dates_in_their_layouts(column, facts, walked, passed, ()) == passed, forms  # type: ignore[arg-type]
        described = {"layout_forms": forms, "layout_prefixes": prefixes, "time_grain": None}
        assert oracle.dates_in_their_layouts(described, walked, passed) == passed, forms
    dates = dataclasses.replace(_uid_facts("%%%%-%%-%%", "9%%%-%%-%%", "%%%%%%%%%%%"), layout_forms={"%%%%-%%-%%": 4})
    assert not generation._names_a_uid_layout(dates)
    walked = ["1950-01-02", "1950-01-03", "1950-01-04", "1950-01-05"]
    written = generation._dates_in_their_layouts(column, dates, walked, ["9950-91-02"] * 4, ())  # type: ignore[arg-type]
    assert all(re.fullmatch(r"(19|20)\d\d-\d\d-\d\d", cell) for cell in written), written


def test_a_free_text_column_keeps_no_made_up_date_of_a_uid_form(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 1's mixed layouts in the free-text writer (LANE I4m RULINGS 14 (2)), one table at 20,000 rows: the same keys
    left to the product to read -- `1.2.1000` to `1.2.1999` beside six figures, beside dates written day first with
    points and beside ISO dates -- are read as free text (each alone; in one table the last two as record numbers), and
    the date keep kept made-up dates of `%.%.%%%%` that were real keys: 90, 351 and 90 twin cells, 9, 46 and 9
    different real keys on 286c8ba6 (10, 20 and 10 cells of 1, 3 and 1 on 591b356f). A form a UID can wear is no date's for the keep, so its runs are kept off the real as every other
    run is: no twin cell is one of the real keys. Mutant: the keep reading a form a UID can wear as a date's."""
    def uid(k: int) -> str:
        return f"1.2.{1000 + k % 1000}"

    shapes = {
        "entry_a": _alternating(20_000, uid, lambda k: f"{100000 + k % 1000}"),
        "entry_b": _alternating(20_000, uid, lambda k: f"{1 + k % 28}.{1 + k % 12}.{1950 + k % 50}"),
        "entry_c": _alternating(20_000, uid, lambda k: f"{1950 + k % 50}-{1 + k % 12:02d}-{1 + k % 28:02d}"),
    }
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, name, (), "lists"))
    blocks, columns, twins = _one_table(tmp_path, tuple(shapes))
    # ...beside six figures the column is free text here; beside dates this table reads it as record numbers, which
    # the date pass's own rule keeps (the cases above).
    assert blocks["entry_a"]["role"] == "free_text", blocks["entry_a"]["role"]
    for name in shapes:
        keys = {cell for cell in columns[name] if cell.startswith("1.2.")}
        written = [cell for cell in twins[name] if cell in keys]
        assert not written, (name, blocks[name]["role"], len(written), written[:3])


def _pairs_of(keys: "list[str]", cells: int, mark: str = ",", size: int = 2, seed: int = 42) -> "list[str]":
    """Codex's draw (`random.Random(42)`, ``size`` keys a cell by `sample`), 2,000 cells repeated to ``cells``."""
    draw = random.Random(seed)
    drawn = [mark.join(draw.sample(keys, size)) for _cell in range(2_000)]
    return (drawn * (cells // 2_000 + 1))[:cells]


def _list_columns(n: int) -> "dict[str, list[str]]":
    """Declared identifier columns of keys between marks: Codex's `R9000` to `R9099` and `R10000` to `R10099` in pairs
    (`R0936,S90007` carried the real `9000` on 286c8ba6), keys of three and four figures in triples, of four and five
    marked `;`, keys zero filled to five from `R09000` and from `R00001`, and random keys of four, five and six figures,
    every first figure of each width held."""
    def run(prefix: str, low: int, count: int) -> "list[str]":
        return [f"{prefix}{low + k}" for k in range(count)]

    draw = random.Random(7)
    dense: "list[str]" = []
    for low, high in ((1000, 9999), (10000, 99999), (100000, 999999)):
        dense += [f"R{value}" for value in draw.sample(range(low, high + 1), 3_000)]
    return {
        "record_list": _pairs_of(run("R", 9000, 100) + run("R", 10000, 100), n),
        "keys_three_four": _pairs_of(run("R", 100, 100) + run("R", 1000, 100), n, ",", 3),
        "keys_four_five_marked": _pairs_of(run("R", 1000, 100) + run("R", 10000, 100), n, ";", 3),
        "keys_padded_nine": _pairs_of([f"R0{9000 + k}" for k in range(100)] + run("R", 10000, 100), n),
        "keys_padded_from_one": _pairs_of([f"R{k:05d}" for k in range(1, 4_001)], n),
        "keys_four_to_six": _pairs_of(dense, n, ",", 2, 42),
    }


def _lists_written(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, rows: int) -> "dict[str, object]":
    """The list columns as one table, each declared an identifier, generated at seed 0: no twin cell or member is a real
    key, as written or merged, and no cell holds a real key's run of four figures or more, as written or merged."""
    shapes = _list_columns(rows)
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, name, (), "lists"))
    typed: "tuple[str, ...]" = ()
    for name in shapes:
        typed = typed + ("--identifier", name)
    blocks, columns, twins = _one_table(tmp_path, tuple(shapes), rows, typed)
    for name in shapes:
        assert blocks[name]["role"] == "identifier", (name, blocks[name]["role"])
        tokens = {token for cell in columns[name] for token in hunt._list_tokens(cell)}
        merged = {parsing.merged_key(token) for token in tokens}
        members = [token for cell in twins[name] for token in hunt._list_tokens(cell)]
        assert not [token for token in members if token in tokens or parsing.merged_key(token) in merged], name
        assert room.equal_cells(columns[name], twins[name]) == 0, name
        assert hunt.cells_holding_a_real_run(columns[name], twins[name], frozenset()) == 0, name
        assert hunt.cells_carrying(tokens, twins[name]) == 0, name
    assert not [cell for cell in twins["record_list"] if "9000" in cell]
    return blocks


def test_list_members_carry_no_real_key_of_any_width_the_list_route_admits(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's review of batch 4n, item 2 (LANE I4m RULINGS 14 (3)), one table at 20,000 rows, the identifier list
    writer: `_list_narrowest` and `_list_common_opening` read no real key under five figures, so `R9000` to `R9099` beside
    `R10000` to `R10099` wrote members of five figures opening `9` that carried a real key of four (the run `9000` in 20
    twin cells, some real run of four figures in 2,178; none of `9000` on 591b356f or f39334aa); and the noughts a
    member opens with read openings no count was taken of (keys of four to six figures: 3,898 twin cells merging with
    a real key). Every merged width of four figures or more a real key holds is kept off, each field's room is its share
    with its letters' places, and no opening deeper than the counts is offered: no member is a real key, no cell holds a
    real key's run, as written or merged, and keys zero filled from `R00001` keep their list exclusion. Mutants: the
    width rule at five (as on 286c8ba6); the counted depth unread; the layout's whole count asked of the common
    opening."""
    blocks = _lists_written(tmp_path, monkeypatch, 20_000)
    exclusions = blocks["keys_padded_from_one"]["layout_exclusions"]  # type: ignore[index]
    assert [layout for layout in exclusions if layout != parsing.EXCLUSION_SPILL], exclusions


def test_list_members_carry_no_real_key_at_the_gate_s_size(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 2 at the gate's size, the same columns at 600 rows through the internal switch: on 286c8ba6 Codex's
    `R8750,T90007` carried the real `9000` there too. Mutants: as above."""
    _lists_written(tmp_path, monkeypatch, 600)


def test_a_list_key_of_four_figures_is_kept_out_of_a_wider_member() -> None:
    """Item 2, the rule alone: Codex's keys counted at the depth the product counts them to publish a common opening no
    real key of four or five figures opens with, written once more on the field of five (`@8%%%,@88%%%`), so every run of
    four inside a member opens with it; keys zero filled from `R00001` find it within each field's share
    (`@99%%%,@99%%%`); and a scan never reads an opening deeper than the counts (`@09%%%%`, not `@999%%%`, where only
    two figures were counted). Mutants: as above."""
    draw = random.Random(42)
    keys = [f"R{9000 + k}" for k in range(100)] + [f"R{10000 + k}" for k in range(100)]
    cells = [",".join(draw.sample(keys, 2)) for _cell in range(2_000)]
    firsts = taxonomy._list_key_firsts(cells, 1)
    assert taxonomy._list_narrowest(firsts, 5) == 4
    assert taxonomy._list_exclusion_of("@%%%%,@%%%%%", firsts, 11, 2_000, 1) == "@8%%%,@88%%%"
    assert taxonomy._list_exclusion_of("@%%%%%,@%%%%%", firsts, 11, 2_000, 1) == "@88%%%,@88%%%"
    draw = random.Random(42)
    padded = [f"R{k:05d}" for k in range(1, 4_001)]
    zero_filled = taxonomy._list_key_firsts([",".join(draw.sample(padded, 2)) for _cell in range(2_000)], 1)
    assert taxonomy._list_exclusion_of("@%%%%%,@%%%%%", zero_filled, 11, 2_000, 1) == "@99%%%,@99%%%"
    every = {opening: 40 for opening in "123456789"}
    every.update({"99": 40, "98": 12, "97": 3})
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%%", {6: every}, 11, 1, 2) == "@09%%%%,@09%%%%"
    assert taxonomy._list_exclusion_of("@%%%%%%,@%%%%%%", {6: every}, 11) == "@999%%%,@999%%%"


# -- batch 4n's second fix round: the independent verify of the first, finding 1 (LANE I4m RULINGS 15) ------------------


def _spread_list_columns(n: int) -> "dict[str, list[str]]":
    """Declared identifier columns of lettered keys of three and four figures, every first figure of both widths held:
    `R107` upward by nine beside `R1007` upward by ninety, a hundred of each, in pairs and in triples, and three hundred
    random keys of each width in pairs; 2,000 drawn cells repeated to ``n``."""
    spread = [f"R{107 + 9 * k}" for k in range(100)] + [f"R{1007 + 90 * k}" for k in range(100)]
    loose = [f"R{value}" for value in random.Random(1).sample(range(100, 1_000), 300)]
    loose += [f"R{value}" for value in random.Random(2).sample(range(1_000, 10_000), 300)]
    return {
        "keys_spread_pairs": _pairs_of(spread, n, ",", 2, 101),
        "keys_spread_triples": _pairs_of(spread, n, ",", 3, 12),
        "keys_random_pairs": _pairs_of(loose, n, ",", 2, 14),
    }


def _spread_lists_written(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, rows: int) -> None:
    """The spread list columns as one table of ``rows`` rows, each declared an identifier, generated at seed 0 and
    validated: validation passes, every layout carries its exclusion (none is written as the spill), no member is a real
    key as written or merged, and no cell holds a real key's run of four figures or more, as written or merged."""
    shapes = _spread_list_columns(rows)
    for name, cells in shapes.items():
        monkeypatch.setitem(hunt.SHAPES, name, (lambda n, cells=cells: cells, name, (), "lists"))
    typed: "tuple[str, ...]" = ()
    for name in shapes:
        typed = typed + ("--identifier", name)
    blocks, columns, twins = _one_table(tmp_path, tuple(shapes), rows, typed)
    folder = tmp_path / "one-table"
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"])
    assert validated == 0, (rows, validated)
    for name in shapes:
        assert blocks[name]["role"] == "identifier", (name, blocks[name]["role"])
        exclusions = blocks[name]["layout_exclusions"]  # type: ignore[index]
        bare = [layout for layout in blocks[name]["layout_forms"] if layout != contract.WITHHELD and layout not in exclusions]  # type: ignore[index]
        assert not bare, (rows, name, bare, exclusions)
        tokens = {token for cell in columns[name] for token in hunt._list_tokens(cell)}
        merged = {parsing.merged_key(token) for token in tokens}
        members = [token for cell in twins[name] for token in hunt._list_tokens(cell)]
        assert not [token for token in members if token in tokens or parsing.merged_key(token) in merged], (rows, name)
        assert room.equal_cells(columns[name], twins[name]) == 0, (rows, name)
        assert hunt.cells_holding_a_real_run(columns[name], twins[name], frozenset()) == 0, (rows, name)
        assert hunt.cells_carrying(tokens, twins[name]) == 0, (rows, name)


def test_list_keys_beside_narrower_keys_of_every_opening_are_kept_under_them_by_noughts(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The independent verify of batch 4n's fix round, finding 1 (LANE I4m RULINGS 15 (2)), one table at 20,000 rows,
    the identifier list writer: beside keys of three figures holding every first figure, a field of four found no free
    opening at its width nor at three within the depth counted, and the layout was written as the spill, eleven random
    figures holding a real key of four at chance (1,172, 2,254 and 3,504 twin cells on these three columns, validation
    exit 3; none on 286c8ba6, 120, 220 and 944 on 591b356f). A list layout is never the spill while a member has room:
    such a field is written with noughts down to a merged width under the narrowest real key of any width (`@00%%`).
    Mutant: the fall to the spill restored (`_list_nought_opening` answering nothing where a real key is as narrow as
    the narrower width)."""
    _spread_lists_written(tmp_path, monkeypatch, 20_000)


def test_list_keys_beside_narrower_keys_of_every_opening_are_kept_at_the_gate_s_size(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Finding 1 at the gate's size, the same columns at 600 rows through the internal switch (32, 66 and 116 twin cells
    holding a real key of four, validation exit 3, on the first fix round's head). Mutant: as above."""
    _spread_lists_written(tmp_path, monkeypatch, 600)


def test_a_field_with_no_free_opening_is_written_under_every_real_key() -> None:
    """Finding 1, the rule alone: keys of three and four figures, every first figure held, counted at the first figure;
    a field of four is written `@00%%` (merged two figures at most, a hundred fillings against a share of two), a field
    of three `@09%` as before; beside keys of two figures too, `@000%` and `@00%`; a real key of one figure leaves no
    width under every real key, so the spill stays (a stated limit); nor where the share is larger than the room left.
    Mutant: as above."""
    spread = [f"R{107 + 9 * k}" for k in range(100)] + [f"R{1007 + 90 * k}" for k in range(100)]
    draw = random.Random(101)
    firsts = taxonomy._list_key_firsts([",".join(draw.sample(spread, 2)) for _cell in range(2_000)], 1)
    assert taxonomy._list_exclusion_of("@%%%%,@%%%", firsts, 11, 1_951, 1) == "@00%%,@09%"
    assert taxonomy._list_exclusion_of("@%%%%,@%%%%", firsts, 11, 1_951, 1) == "@00%%,@00%%"
    assert taxonomy._list_exclusion_of("@%%%,@%%%", firsts, 11, 1_951, 1) == "@09%,@09%"
    two = dict(firsts)
    two[2] = {figure: 40 for figure in "123456789"}
    assert taxonomy._list_exclusion_of("@%%%%,@%%%", two, 11, 1_951, 1) == "@000%,@00%"
    one = dict(two)
    one[1] = {figure: 40 for figure in "123456789"}
    assert taxonomy._list_exclusion_of("@%%%%,@%%%", one, 11, 1_951, 1) == ""
    # ...figures alone, two fields: a field's share is the square root of the layout's values, 45, which a hundred
    # fillings hold and ten do not.
    wide = {5: firsts[4], 4: firsts[4], 3: firsts[3]}
    assert taxonomy._list_exclusion_of("%%%%%,%%%%%", wide, 11, 1_951, 1) == "000%%,000%%"
    wide[2] = two[2]
    assert taxonomy._list_exclusion_of("%%%%%,%%%%%", wide, 11, 1_951, 1) == ""


def test_the_runs_remark_of_free_text_names_the_noughts_alone() -> None:
    """Item 3's second sentence (LANE I4m RULINGS 14 (4)): the remark of a free-text column said no run it makes up is
    written as a real one or holds one; where a width's room is spent its noughts alone may spell one real value
    (limit (af)), and a made-up date is kept as a date. Mutant: the sentence as it stood."""
    column = types.SimpleNamespace(name="note")
    remark = generation._runs_widened_remark(column, [3, 2])  # type: ignore[arg-type]
    assert remark.note == generation._RUNS_OFF_THE_REAL_TEXT
    assert "noughts alone, a spelling one real value may also have" in remark.note
    assert "a made-up date is kept as a date" in remark.note and remark.held.endswith("2 written as noughts")
