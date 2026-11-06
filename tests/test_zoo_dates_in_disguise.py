"""P4-D446 (lane CZ-H): Safe Harbor dates in disguise are held while their question is open.

THE DEFECT, measured on the base a5702b71 (planning-notes wave6/CZ-H).
Real health tables hold a person's dates -- a birth, an admission, a
discharge, a service time -- where no column name and no cell shape says
"date". Two forms published them:

* a day count from the MUMPS $H epoch with a two-figure contact index
  after the point on most rows (`66123.01`) was never put question Q3,
  whose rule A asked at least half of such a column to write no contact:
  read as a measurement it published 70 real days in its points and tails
  at 600 rows and its twin wrote 224 cells on real days; at 20,000 rows,
  one row a record, answered `keep` to its identity question, 101 real
  days and 19,865 twin cells;
* an answer column under a question key, a few of whose answers are day
  counts, epoch seconds or dates, answered `keep` to its identity
  question at 20,000 rows, published two shared admission days as levels
  (14 and 13 rows) and wrote them on 28 twin cells.

THE RULE. (1) Q3 asks a column of band counts whose contacts write at most
two figures after the point, whatever their spread
(`date_counts.contacts_shaped`), and an open Q3 offers `identifier`, so
the column is held until answered (P4-D401's hold). (2) In a column read
as labels or as numbers, each value that reads as a date in disguise is
read as a blank cell while the column's Safe Harbor question about them
is open or answered `yes` (`date_counts.dated_values_blanked`), whatever
ordinary values stand beside it; `no`, or `measurement` to Q3, describes
the column as before, byte for byte.

THE GATE: the forms of `tests/dates_in_disguise.py` at 600 rows through
the library, unanswered and answered as the zoo answers; the reviews'
attacks, cell by cell and through the command at 600 rows; each rule red
on its mutant; one case at the owner's table floor (the answer column,
answered, at 20,000 rows). The forms and every attack at 600 and 20,000
rows are K-HZ-16's driver (`tools/measurements/kpi_dates_in_disguise.py`,
under `kpi_run.py --slow`).
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

from synthtwin import asking, contract, date_counts, generation, parsing, profile, reading, taxonomy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dates_in_disguise as forms  # noqa: E402
import health_zoo  # noqa: E402

# The forms' tables at 600 rows, but the day numbers on one row a record,
# the same columns as the wide table's, which K-HZ-16's driver measures
# (the suite's time rule of 2026-10-26: a test file adds at most 3 minutes).
TABLES = [table.name for table in forms.TABLES if table.name != "day_numbers_flat"]


DAY_TABLES = ("day_numbers", "day_numbers_flat", "contact_days")


def _bar(result: "dict[str, object]") -> "list[str]":
    """Every way a run broke the bar: a real date shown or written, a column not asked its date question."""
    broken: "list[str]" = []
    shown = result["shown"]
    twin = result.get("twin", {})
    for column, entry in shown.items():  # type: ignore[attr-defined]
        if result.get("table") == "paired_clocks":
            continue
        if entry["days"]:
            broken += [f"{column}: shown {entry}"]
        # A column answered as dates publishes their span under its date rules
        # (plan P4-D446); any other reading shows no date in another form.
        if (entry["other_forms"] or entry["elsewhere"]) and not (result["answered"] and result["table"] in DAY_TABLES):
            broken += [f"{column}: shown in another form {entry}"]
        if twin and twin[column]["cells"]:  # type: ignore[index, operator]
            broken += [f"{column}: twin {twin[column]}"]  # type: ignore[index]
    if "dates_held" in result and result["dates_held"]["few"]:  # type: ignore[index]
        broken += [f"dates one to ten people hold printed: {result['dates_held']}"]
    return broken


@pytest.mark.parametrize("name", TABLES)
def test_unanswered_no_form_shows_or_writes_a_real_date(name: str, tmp_path: pathlib.Path) -> None:
    result = forms.run_form(forms.table_named(name), tmp_path, health_zoo.SMOKE_ROWS, answered=False)
    assert result["steps"] == {"profile": 0, "generate": 0, "validate": 0}, result["steps"]
    assert _bar(result) == []


@pytest.mark.parametrize("name", TABLES)
def test_answered_every_form_is_asked_its_date_question_and_shows_none(name: str, tmp_path: pathlib.Path) -> None:
    result = forms.run_form(forms.table_named(name), tmp_path, health_zoo.SMOKE_ROWS, answered=True)
    assert _bar(result) == []
    # ...and the validator reads the column as its description did: a hold moves no role.
    assert [line for line in result["missed"] if "axes." in line] == []  # type: ignore[attr-defined]
    for where in forms.DISGUISED[name]:
        if not where.shaped:
            assert result["asked"][where.column], (where.column, result["offered"])  # type: ignore[index]


# -- rule (1): day counts with contacts on most rows are asked ------------------


def _contact_cells(contacts_share: float, count: int = 600) -> "list[str]":
    """Day counts of 2019 to 2023 since 1840, the given share written with a contact `.01` to `.12`."""
    import random

    draw = random.Random(7)
    cells: "list[str]" = []
    for _place in range(count):
        day = forms.day_count(forms.FIRST_DAY) + draw.randrange(1800)
        contact = draw.randint(1, 12) if draw.random() < contacts_share else 0
        cells += [forms.float_day(day, contact)]
    return cells


def _asked(cells: "list[str]") -> "tuple[str, ...]":
    numbers = [float(cell) for cell in cells]
    found = date_counts.asked_of(
        cells, numbers, len(cells), sorted(numbers)[len(numbers) // 2], False, floor=11,
    )
    return () if found is None else found.members


def test_day_counts_with_contacts_on_most_rows_are_asked() -> None:
    assert date_counts.DAYS_SINCE_1840 in _asked(_contact_cells(0.7))
    # ...as they were where half or more write none.
    assert date_counts.DAYS_SINCE_1840 in _asked(_contact_cells(0.3))


def test_without_the_contact_rule_they_are_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "contacts_shaped", lambda with_contact, small: False)
    assert date_counts.DAYS_SINCE_1840 not in _asked(_contact_cells(0.7))


def test_money_in_cents_in_the_band_is_asked_too() -> None:
    """The spread of the figures after the point decides nothing: `measurement` answers it."""
    import random

    draw = random.Random(11)
    cells = [f"{draw.randint(55_000, 75_000)}.{draw.randint(1, 99):02d}" for _place in range(600)]
    assert date_counts.DAYS_SINCE_1840 in _asked(cells)


@pytest.mark.parametrize(
    ("top", "written"),
    [(30, "{day}.{contact:02d}"), (40, "{day}.{contact:02d}"), (12, "{day}.{contact:02d}0"), (12, "{day}.{contact}")],
)
def test_contacts_are_asked_whatever_their_spread(top: int, written: str) -> None:
    """Seventy in a hundred write a contact (`.01` to `.40` at most): Q3 is put, as contract section 6.6 now says (Codex's item 6)."""
    import random

    draw = random.Random(3)
    cells: "list[str]" = []
    for _place in range(600):
        day = forms.day_count(forms.FIRST_DAY) + draw.randrange(1800)
        cells += [written.format(day=day, contact=draw.randint(1, top)) if draw.random() < 0.7 else f"{day}"]
    assert date_counts.DAYS_SINCE_1840 in _asked(cells)


def test_three_real_figures_after_the_point_are_no_contact() -> None:
    import random

    draw = random.Random(4)
    cells = [f"{draw.randint(60_000, 66_000)}.{draw.randint(101, 999)}" for _place in range(600)]
    assert date_counts.DAYS_SINCE_1840 not in _asked(cells)


def test_a_member_offered_beside_a_hit_takes_contacts_on_most_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_contacts_fit` reads the same shape as the walk: red without it."""
    cells = _contact_cells(0.8)
    assert date_counts._contacts_fit(cells, date_counts.DAYS_SINCE_1840, len(cells), date_counts.POINT)
    monkeypatch.setattr(date_counts, "contacts_shaped", lambda with_contact, small: False)
    assert not date_counts._contacts_fit(cells, date_counts.DAYS_SINCE_1840, len(cells), date_counts.POINT)


# -- rule (2): dates in disguise beside anything ----------------------------------


def test_a_memo_past_its_bound_changes_no_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    cells = ["66497", "mild", "66497", "mild", "1"]
    whole = date_counts.dated_values_blanked(cells)
    monkeypatch.setattr(date_counts, "_MEMO_AT_MOST", 0)
    assert date_counts.dated_values_blanked(cells) == whole == ["", "mild", "", "mild", "1"]


@pytest.mark.parametrize(
    ("text", "dated"),
    [
        # Counts, however written.
        ("66497", True), ("66497.01", True), ("66497.010", True), ("44264.625", True), ("+66497", True),
        ("66,497", True), ("66497,0", True), ("66497,43200", True), ("-12345", True), ("6.6497e4", False),
        ("1601234567", True), ("1601234567890", True), ("999999999", True), ("-86400000", False),
        ("-999999999", True), ("631152000000", True),
        # Stamps in figures alone.
        ("20210314", True), ("03142021", True), ("202103080000", True), ("20210308000000", True),
        # Dates as text.
        ("03/14/2021", True), ("03/14/21", True), ("2021-03-14", True), ("03-14-2021", True), ("03-14-21", True),
        ("14.03.2021", True), ("2021.03.14", True), ("03-14-2021 00:00", True), ("2021-03-14 08:30:00", True),
        ("3/14/2021 2:15 PM", True), ("14MAR2021", True), ("14-Mar-2021", True), ("Mar 14, 2021", True),
        ("March 2021", True), ("2021-067", True), ("03/2021", True), ("2021-03", True), ("2021-Q1", True),
        # A clock alone names no date (LANE CZ-H RULINGS 3 (2)); a date with one stays a date.
        ("14:30", False), ("14:30:05", False), ("2:15 PM", False), ("2:15PM", False), ("0930", False),
        ("2021-03-14 14:30", True),
        # What is left out: a titer, a pressure, small numbers and codes.
        ("1:40", False), ("1:80", False), ("1:40:00", False),
        ("1", False), ("mild", False), ("99213", False), ("120/80", False), ("37.2", False), ("12.2021", False),
        ("2021", False), ("5000", False), ("13-13-2021", False), ("Q6001", False), ("00123", False), ("210314", False),
        ("2021067", False), ("76800", False), ("3195551212x", False), ("1-2", False), ("10-20", False),
        # An eight-figure code reads as a compact date of 3834: no person's year.
        ("38341003", False),
        # THE HEAD OF A CELL, whatever follows a full date there (the verify of
        # the first repair, item 1): a zone word, an offset, a bare clock, the
        # `T` of the basic form; a weekday's name before it; an ordinal day.
        ("2021-03-08 00:00 EST", True), ("2021-03-08 0000", True), ("2021-03-08Z", True),
        ("2021-03-08+00:00", True), ("2021-03-08T0930", True), ("20210308T000000", True), ("20210308 0930", True),
        ("Mon Mar 08 2021", True), ("Tue Mar 08 2021", True), ("Monday, March 8, 2021", True),
        ("8th March 2021", True), ("March 8th, 2021", True), ("1.6409952e+09", True),
        ("2021-03-08 seen at the clinic for a follow up after the fall, stable", True),
        # ...and what it leaves: no day at the head, an exponent of days.
        ("Monday clinic", False), ("March madness", False), ("03/2021 batch", False), ("2021-12 lot", False),
        ("the 3rd visit", False), ("4.5E+04", False), ("12 tablets daily", False), ("319-555-1212", False),
        ("123-45-6789", False), ("10-12 times a day", False),
        ("seen at the clinic for a follow up after the fall on 2021-03-08", False),
    ],
)
def test_a_value_reads_as_a_date_in_disguise(text: str, dated: bool) -> None:
    assert date_counts.date_in_disguise(text) is dated


@pytest.mark.parametrize(
    ("mutant", "text"),
    [
        ("_head_is_a_date", "2021-03-08 00:00 EST"),
        ("_head_is_a_date", "20210308T000000"),
        ("_plainly_written", "Mon Mar 08 2021"),
        ("_plainly_written", "8th March 2021"),
    ],
)
def test_each_reading_of_the_head_is_red_on_its_mutant(mutant: str, text: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each spelling of the verify's item 1 is read by one piece of the rule, which its mutant takes out."""
    monkeypatch.setattr(date_counts, mutant, (lambda body: False) if mutant == "_head_is_a_date" else (lambda body: body))
    assert date_counts.date_in_disguise(text) is False


def test_an_exponent_of_seconds_is_read_and_one_of_days_is_not() -> None:
    assert date_counts.counted_figures("1.6409952e+09") == 10
    assert date_counts.counted_figures("6.6497e4") == 0


def test_the_counter_reads_each_spelling_it_stamps() -> None:
    """K-HZ-16's counter decodes the spellings of the verify's items 1 and 5, as a token in a text and as a twin cell."""
    day = forms.SHARED_ADMISSIONS[0]
    real = forms.RealDates({day.toordinal(): {"p"}}, set(), set(), ("iso-lead", "month-first-named"), False)
    for text in (
        day.strftime("%Y-%m-%d 00:00 EST"), day.strftime("%Y-%m-%d 0000"), day.strftime("%a %b %d %Y"),
        day.strftime("%Y%m%dT000000"), day.strftime("%A, %B %d, %Y"), "8th March 2021",
    ):
        days, _clocks, other = forms._hits(f"level {text} held", real)
        assert days | other == {day.toordinal()}, text
        assert any(decode(text) == day.toordinal() for decode in forms.DECODERS.values()), text


@pytest.mark.parametrize("stray", ["90210", "12345.678", "-12345", "44264.625", "99999", "5551234567", "1", "mild"])
def test_no_stray_frees_the_counts_beside_it(stray: str) -> None:
    """One ordinary value beside day counts or epoch seconds frees none of them (the reviews' first BLOCKER)."""
    days = ["66497", "1601234567", "1", "0", "mild", "66497"]
    blanked = date_counts.dated_values_blanked(days + [stray])
    assert blanked is not None
    assert blanked[:6] == ["", "", "1", "0", "mild", ""]


def test_a_code_in_the_band_is_held_and_one_past_it_is_not() -> None:
    """Codes pay in a question: `36415` lies in the band, `99213` past it; `no` restores both."""
    assert date_counts.dated_values_blanked(["99213", "36415", "G0439"]) == ["99213", "", "G0439"]
    assert date_counts.dated_values_blanked(["mild", "1"]) is None


def test_a_count_and_a_date_as_text_are_held_at_any_share() -> None:
    """No share frees a count or a date as text (LANE CZ-H RULINGS 2 (1), 3 (1); the verify of the first repair, item 2).

    A column read under the date rules -- a date role, or declared or
    answered as dates -- is not handed to the rule at all (`profile`).
    """
    assert date_counts.dated_values_blanked(["66497", "66498", "1"]) == ["", "", "1"]
    assert date_counts.dated_values_blanked(["66497", "66498"]) == ["", ""]
    assert date_counts.dated_values_blanked(["2021-03-14", "2021-03-15", "pending"]) == ["", "", "pending"]
    assert date_counts.dated_values_blanked(["2021-03-14", "pending", "mild"]) == ["", "pending", "mild"]
    assert date_counts.dated_values_blanked(["2021-03-14", "2021-03-15", "66497"]) == ["", "", ""]
    assert date_counts.dated_values_blanked(["14:30", "pending"]) is None


def test_a_missing_value_is_no_date_in_disguise() -> None:
    """A cell spelled as a missing value is set aside in reading and in writing (Codex's review of the first repair, item 2)."""
    cells = ["999999999", "150", "66274", "999999999"]
    assert date_counts.dated_values_blanked(cells, frozenset({"999999999"})) == ["999999999", "150", "", "999999999"]
    assert date_counts.dated_values_blanked(cells) == ["", "150", "", ""]
    assert date_counts.dated_values_blanked(["999999999", "150"], frozenset({"999999999"})) is None


def test_an_age_inside_its_unit_s_oldest_stays_an_age() -> None:
    """A count no older than the oldest age the unit allows is an age, whatever band it lies in (LANE CZ-H RULINGS 5 (1)).

    In years no count of five figures is one; in days (125 years of 366)
    `14600` to `36500` are ages and `66274`, past them, is held.
    """
    days = ["14600", "36500", "66274"]
    assert date_counts.dated_values_blanked(days, frozenset(), 125 * 366) == ["14600", "36500", ""]
    assert date_counts.dated_values_blanked(days, frozenset(), taxonomy.TOP_CODE_REACH_CEILING) == ["", "", ""]
    assert date_counts.dated_values_blanked(["95", "66274"], frozenset(), taxonomy.TOP_CODE_REACH_CEILING) == ["95", ""]


# The shared admission day, written as date text: a day count alone beside
# 1/0 is read as ZIP-shaped (plan P4-D427's ZIP reach holds the column
# whole); the answer column at the floor below holds day counts.
SHARED_DAY = "2021-03-08"


def _answer_table(tmp_path: pathlib.Path) -> pathlib.Path:
    """600 answers: words, 1/0, small numbers, and one shared admission day on 15 rows."""
    rows = ["answer_value"]
    words = ("mild", "moderate", "severe", "none")
    for place in range(600):
        if place % 40 == 0:
            rows += [SHARED_DAY]
        elif place % 5 == 0:
            rows += [f"{place % 9 + 2}"]
        elif place % 3 == 0:
            rows += [words[place % 4]]
        else:
            rows += ["1" if place % 2 else "0"]
    path = tmp_path / "answers.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return path


def _described(
    path: pathlib.Path, no: "list[str] | None" = None, held: "tuple[str, ...]" = ("answer_value",),
    measured: "list[str] | None" = None, dates_no: "list[str] | None" = None,
) -> "tuple[dict, list[str]]":
    settings = taxonomy.Settings()
    table = reading.read_table(str(path))
    named: "list[str]" = []
    document = profile.build_document(
        table, settings, [], [], measured or [], [], top_code=True, safe_harbor_no=no or [], dated_values=named,
        dated_held=held, dated_values_no=dates_no or [],
    )
    return json.loads(json.dumps(document, default=str)), named


def test_a_shared_admission_day_is_no_level_while_its_question_is_open(tmp_path: pathlib.Path) -> None:
    document, named = _described(_answer_table(tmp_path))
    assert named == ["answer_value"]
    assert SHARED_DAY not in json.dumps(document["columns"])


def test_without_the_hold_the_admission_day_is_a_level(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "dated_values_blanked", lambda cells, *held: None)
    document, named = _described(_answer_table(tmp_path))
    assert named == []
    assert SHARED_DAY in json.dumps(document["columns"])


def test_the_first_description_names_the_column_and_reads_every_cell(tmp_path: pathlib.Path) -> None:
    """The questions are worked out from a description of every cell; the one written blanks them (``dated_held``)."""
    document, named = _described(_answer_table(tmp_path), held=())
    assert named == ["answer_value"]
    assert SHARED_DAY in json.dumps(document["columns"])


def _numbers_table(tmp_path: pathlib.Path, rows: "list[str]") -> pathlib.Path:
    path = tmp_path / "numbers.csv"
    path.write_text("\n".join(["answer_value"] + rows) + "\n", encoding="utf-8", newline="\n")
    return path


def _block(document: "dict") -> "dict":
    return next(block for block in document["columns"] if block["name"] == "answer_value")


@pytest.mark.parametrize(
    ("role", "cells"),
    [
        (taxonomy.ROLE_CONTINUOUS, [f"{place % 40}.{place % 7}" for place in range(576)] + ["66274"] * 24),
        (taxonomy.ROLE_COUNT, [f"{place % 40}" for place in range(576)] + ["66274"] * 24),
        (taxonomy.ROLE_COMPOUND, [f"{place % 40}.{place % 7}" for place in range(536)] + ["Detected"] * 20 + ["Low"] * 20 + ["66274"] * 24),
    ],
)
def test_every_number_role_reaches_the_rule(
    role: str, cells: "list[str]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A date in a column of numbers is a rung or a tail: each role red on its mutant."""
    path = _numbers_table(tmp_path, cells)
    document, named = _described(path)
    assert named == ["answer_value"]
    assert _block(document)["role"] == role
    assert "66274" not in json.dumps(_block(document))
    monkeypatch.setattr(profile, "_DATED_VALUE_ROLES", tuple(one for one in profile._DATED_VALUE_ROLES if one != role))
    _document, named = _described(path)
    assert named == []


def test_measurement_to_the_date_question_frees_the_column_and_to_another_question_does_not(tmp_path: pathlib.Path) -> None:
    """`measurement` says the numbers are numbers only where Q3 is the question put (the column's NF113)."""
    days = _numbers_table(tmp_path, [f"{60_000 + place * 7}.{place % 12 + 1:02d}" for place in range(600)])
    _document, named = _described(days, measured=["answer_value"])
    assert named == []
    _document, named = _described(days)
    assert named == ["answer_value"]
    beside = _numbers_table(tmp_path, [f"{place % 40}.{place % 7}" for place in range(576)] + ["66274"] * 24)
    _document, named = _described(beside, measured=["answer_value"])
    assert named == ["answer_value"]


def test_a_column_declared_as_dates_is_read_by_the_date_rules(tmp_path: pathlib.Path) -> None:
    """`--date-count` or `--date-column` says the column holds dates: the value rule stands aside (plan P4-D446)."""
    cells = [f"{60_000 + place % 40}.{place % 3 + 1:02d}" for place in range(576)] + ["unknown"] * 24
    path = _numbers_table(tmp_path, cells)
    table = reading.read_table(str(path))
    for settings in (
        taxonomy.Settings(forced_date_counts=(("answer_value", date_counts.DAYS_SINCE_1840),)),
        taxonomy.Settings(forced_date_columns=("answer_value",)),
    ):
        named: "list[str]" = []
        profile.build_document(table, settings, [], [], [], [], top_code=True, safe_harbor_no=[], dated_values=named)
        assert named == []
    named = []
    profile.build_document(table, taxonomy.Settings(), [], [], [], [], top_code=True, safe_harbor_no=[], dated_values=named)
    assert named == ["answer_value"]


def test_the_real_table_meets_the_description_that_held_its_dates(tmp_path: pathlib.Path) -> None:
    """The validator holds what the description held (NF135): the real table misses no count of its present cells."""
    from synthtwin import validation

    path = _answer_table(tmp_path)
    code, said = forms._command(["profile", f"{path}", "--replace"], False)
    assert code == 0, said
    described = contract.load_profile(str(tmp_path / "answers-profile.json"))
    outcome = validation.measure(described, str(path))
    missed = [check.subcheck or check.fact for check in outcome.checks if check.verdict == "MISSED"]
    assert [one for one in missed if "n_present" in one or "n_missing" in one] == []


def _results_table(tmp_path: pathlib.Path) -> pathlib.Path:
    """Results read as long-tail labels for their date text alone, as form 4's are at the floor."""
    import random

    draw = random.Random(9)
    rows = ["answer_value"]
    words = ("Positive", "Negative", "Detected", "See note")
    for place in range(2000):
        roll = draw.random()
        if roll < 0.03:
            rows += [f"{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}-{draw.randint(2015, 2023)}"]
        elif roll < 0.23:
            rows += [draw.choice(words)]
        else:
            rows += [f"{draw.uniform(1, 300):.1f}"]
    path = tmp_path / "results.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return path


def test_the_validator_reads_a_twin_of_held_dates_as_its_description_did(tmp_path: pathlib.Path) -> None:
    """A twin holding the results' labels and numbers alone, its dates blank, is read as the labels its description named (NF135)."""
    from synthtwin import validation

    path = _results_table(tmp_path)
    block = _block(_answered(tmp_path, path, {"answer_value": "keep"}))
    assert block["role"] in profile._DATED_LABEL_ROLES, block["role"]
    assert taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in block["remarks"]
    described = contract.load_profile(str(tmp_path / "results-profile.json"))
    cells = path.read_text(encoding="utf-8").split("\n")
    twin = tmp_path / "twin.csv"
    twin.write_text(
        "\n".join([cells[0]] + ['""' if date_counts.date_in_disguise(cell) else cell for cell in cells[1:-1]]) + "\n",
        encoding="utf-8", newline="\n",
    )
    outcome = validation.measure(described, str(twin))
    assert [check.subcheck for check in outcome.checks if check.verdict == "MISSED" and "axes" in check.subcheck] == []


def test_a_hold_moves_no_role(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Results read as labels stay labels with their dates held; red where the hold reads them as numbers beside labels."""
    path = _results_table(tmp_path)
    document, _named = _described(path, no=["answer_value"])
    role = _block(document)["role"]
    assert role in profile._DATED_LABEL_ROLES
    document, named = _described(path)
    assert named == ["answer_value"]
    assert _block(document)["role"] == role
    monkeypatch.setattr(profile, "_DATED_LABEL_ROLES", ())
    document, _named = _described(path)
    assert _block(document)["role"] == taxonomy.ROLE_COMPOUND


def test_no_describes_the_column_as_before_byte_for_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _answer_table(tmp_path)
    answered_no, named = _described(path, dates_no=["answer_value"])
    assert named == []
    # ...and `no` to the column's age or ZIP question frees nothing of its
    # dates (LANE CZ-H RULINGS 6 (1), item 3).
    other_no, still = _described(path, ["answer_value"])
    assert still == ["answer_value"] and SHARED_DAY not in json.dumps(other_no["columns"])
    monkeypatch.setattr(date_counts, "dated_values_blanked", lambda cells, *held: None)
    before, _named = _described(path)
    assert answered_no == before


def test_the_question_is_put_and_yes_keeps_the_rest_of_the_column(tmp_path: pathlib.Path) -> None:
    path = _answer_table(tmp_path)
    first, said = forms._command(["profile", f"{path}", "--replace"], False)
    assert first == 0, said
    questions = tmp_path / "answers-questions.json"
    offered = forms.date_questions(questions, "answer_value")
    assert [forms.DATES_ASKED in answers for answers in offered] == [True], offered
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in health_zoo._entries(document):
        if entry.get("column") == "answer_value":
            entry["your_answer"] = asking.ANSWER_SAFE_HARBOR_YES
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    code, said = forms._command(["profile", f"{path}", "--replace", "--answers", f"{questions}"], False)
    assert code == 0, said
    described = json.loads((tmp_path / "answers-profile.json").read_text(encoding="utf-8"))
    block = next(block for block in described["columns"] if block["name"] == "answer_value")
    assert block["role"] != taxonomy.ROLE_IDENTIFIER
    assert SHARED_DAY not in json.dumps(block)


def _answered(tmp_path: pathlib.Path, path: pathlib.Path, answer: "dict[str, str]") -> "dict":
    """The command run on `path`, then again with those answers given to the questions they fit; the description."""
    code, said = forms._command(["profile", f"{path}", "--replace"], False)
    assert code == 0, said
    questions = tmp_path / f"{path.stem}-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in health_zoo._entries(document):
        offered = health_zoo._offered(entry)
        given = answer.get(f"{entry.get('column', '')}", "")
        if given in offered:
            entry["your_answer"] = given
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    code, said = forms._command(["profile", f"{path}", "--replace", "--answers", f"{questions}"], False)
    assert code == 0, said
    return json.loads((tmp_path / f"{path.stem}-profile.json").read_text(encoding="utf-8"))


def test_no_through_the_command_restores_the_column(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _answer_table(tmp_path)
    answered_no = _answered(tmp_path, path, {"answer_value": asking.ANSWER_SAFE_HARBOR_NO})
    monkeypatch.setattr(date_counts, "dated_values_blanked", lambda cells, *held: None)
    before = _answered(tmp_path, path, {})
    assert _block(answered_no) == _block(before)


def _two_answers(age_answer: str, dates_answer: str) -> "dict[str, object]":
    """A questions file whose column `v` was put its age question and, a round later, its question about dates."""
    ages = asking._safe_harbor_question("v", taxonomy.ROLE_CONTINUOUS, asking.BECAUSE_SAFE_HARBOR_AGES)
    dated = asking._safe_harbor_question("v", taxonomy.ROLE_CONTINUOUS, asking.BECAUSE_SAFE_HARBOR_DATED_VALUES)
    entries: "list[dict[str, object]]" = []
    for question, answer in ((ages, age_answer), (dated, dates_answer)):
        entries += [{
            "column": "v", "what_synthtwin_saw": question.shape, "read_as_now": question.taken,
            "answers_you_can_give": [{"answer": choice.answer, "means": "", "then_the_description_publishes": ""}
                                     for choice in question.choices],
            "your_answer": answer,
        }]
    return {"asked": entries, "checklist": {"columns": []}}


def test_a_safe_harbor_no_is_kept_by_the_question_it_answers() -> None:
    """`no` to the age question frees the top-code alone; the question about dates keeps its own answer (LANE CZ-H RULINGS 6 (1), item 3)."""
    read = asking.answers_in(_two_answers("no", "yes"), "questions.json")
    assert (read.safe_harbor_no, read.safe_harbor_yes) == (("v",), ())
    assert (read.safe_harbor_dates_no, read.safe_harbor_dates_yes) == ((), ("v",))
    read = asking.answers_in(_two_answers("", "no"), "questions.json")
    assert (read.safe_harbor_no, read.safe_harbor_dates_no) == ((), ("v",))
    # ...and kept so in the file the next run writes, each by its own question.
    kept = asking.answered_before(asking.Given(columns=("v",), safe_harbor_no=("v",), safe_harbor_dates_yes=("v",)))
    again = asking.answers_in({"asked": [], "checklist": {"columns": []}, "answered_before": kept}, "questions.json")
    assert (again.safe_harbor_no, again.safe_harbor_dates_yes) == (("v",), ("v",))


def test_after_no_to_the_age_question_the_dates_question_is_put() -> None:
    document: "dict[str, object]" = {"columns": [{"name": "v", "role": taxonomy.ROLE_CONTINUOUS}]}
    put = asking.safe_harbor_questions(document, (), [], answered=("v",), dated=("v",))
    assert [question.reason for question in put] == [asking.BECAUSE_SAFE_HARBOR_DATED_VALUES]
    assert asking.safe_harbor_questions(document, (), [], answered=("v",), dated=("v",), dates_answered=("v",)) == []
    assert asking.safe_harbor_questions(document, (), [], answered=("v",), dated=()) == []


def test_the_dates_question_waits_beside_another_question() -> None:
    """One question a column (P4-D427): a column put its codes or mostly-dates question this run is put the dates question after it."""
    document: "dict[str, object]" = {"columns": [{"name": "v", "role": taxonomy.ROLE_LONG_TAIL}]}
    assert asking.safe_harbor_questions(document, (), [], dated=("v",), beside=("v",)) == []
    put = asking.safe_harbor_questions(document, (), [], dated=("v",), beside=("w",))
    assert [question.reason for question in put] == [asking.BECAUSE_SAFE_HARBOR_DATED_VALUES]


def test_a_column_whose_date_codes_question_was_answered_is_not_read_by_the_rule(tmp_path: pathlib.Path) -> None:
    """Answered `missing` or `real-value` about its codes, a column of dates stays under the date rules (RULINGS 6 (1), item 2)."""
    path = _answer_table(tmp_path)
    table = reading.read_table(str(path))
    named: "list[str]" = []
    document = profile.build_document(
        table, taxonomy.Settings(), [], top_code=True, safe_harbor_no=[], dated_values=named, dated_held=("answer_value",),
        dates_answered=("answer_value",),
    )
    assert named == [] and SHARED_DAY in json.dumps(document["columns"])


def test_ages_beside_many_day_counts_are_top_coded_once_those_are_set_aside(tmp_path: pathlib.Path) -> None:
    """Day counts on 1 row in 8, more than the ages' strays allow: the age reach reads the cells the date rule leaves (RULINGS 5 (1))."""
    path = tmp_path / "ages.csv"
    # Each day count different, so none is set aside as a placeholder the
    # floor's rows repeat: 100 strays in 800, past the one in twenty the
    # ages' reach allows on the cells as written.
    rows = ["age_value"] + [f"{66000 + place}" if place % 8 == 7 else f"{40 + place % 61}" for place in range(800)]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    named: "list[str]" = []
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), [], top_code=True, safe_harbor_no=[], dated_values=named,
        dated_held=("age_value",),
    )
    block = json.loads(json.dumps(document["columns"][0], default=str))
    assert named == ["age_value"] and block["top_coded"] == taxonomy.TOP_CODE
    assert "660" not in json.dumps(block["percentiles"])
    printed = [number for number in block["percentiles"].values() if number is not None]
    assert printed and max(printed) <= taxonomy.TOP_CODE, block["percentiles"]


def test_a_date_question_left_blank_in_a_file_publishes_no_day(tmp_path: pathlib.Path) -> None:
    """A blank Q3 is no answer: the other columns answered, its column's day counts stay blank until `no` or `measurement`."""
    case = forms._contact_table()
    header, rows = case.build(600, 5)
    path = tmp_path / "contact.csv"
    path.write_bytes(case.write(header, rows))
    described = _answered(tmp_path, path, {"encounter_id": "identifier"})
    block = next(block for block in described["columns"] if block["name"] == "visit_day_number")
    assert not [token for token in json.dumps(block).split('"') if token[:3] in ("635", "640", "650", "660")]
    assert block["n_present"] == 0 or block["role"] == taxonomy.ROLE_IDENTIFIER


def test_a_person_at_the_keyboard_is_asked_again_of_the_new_reading(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An interview's rebuild names afresh: a column answered `identifier` is no column of held values, red on a stale name."""
    from synthtwin import cli

    rows = [f"P{place % 150:05d},{place % 40},{'66274' if place % 25 == 0 else place % 9}" for place in range(600)]
    path = tmp_path / "table.csv"
    path.write_text("\n".join(["record_id,dose,answer_value"] + rows) + "\n", encoding="utf-8", newline="\n")
    named: "list[list[str]]" = []
    real = profile.build_document

    def described(*arguments: object, **options: object) -> "dict":
        found = real(*arguments, **options)  # type: ignore[arg-type]
        if isinstance(options.get("dated_values"), list):
            named.extend([list(options["dated_values"])])  # type: ignore[arg-type]
        return found

    answers = iter(["identifier"])
    monkeypatch.setattr(profile, "build_document", described)
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda *_given: next(answers, ""))
    code, said = forms._command(["profile", f"{path}", "--replace"], False)
    assert code == 0, said
    assert named == [["answer_value"], ["answer_value"]], said


@pytest.mark.parametrize(
    "name",
    [
        # The rest of the reviews' attacks are K-HZ-16's at 20,000 rows, their
        # spellings and contacts pinned cell by cell above (THE SUITE'S TIME).
        "stray_zip", "numbers_alone", "contacts_to_40",
        # The second repair's: dates as text on most of a column, two
        # spellings, numbers beside them (the verify's item 2); `no` to the
        # age question and `yes` to the dates question (its item 3).
        "results_mostly_mixed", "many_keys_no_to_ages",
    ],
)
def test_a_review_s_attack_is_held_through_the_command(name: str, tmp_path: pathlib.Path) -> None:
    """Each attack at 600 rows, answered as the zoo answers: no real date shown or written, and asked."""
    case = forms.case_named(name)
    result = forms.run_form(
        case.table, tmp_path, health_zoo.SMOKE_ROWS, answered=True, disguised=case.disguised,
        dates_answer=case.dates_answer, extra=case.extra,
    )
    assert result["failed"] == [], result["steps"]
    assert _bar(result) == []
    for column in result["shown"]:  # type: ignore[attr-defined]
        assert result["asked"][column], (column, result["offered"])  # type: ignore[index]
        # ...and the second repair's are held by the value rule (NF135).
        assert result["held"][column] or name not in ("results_mostly_mixed", "many_keys_no_to_ages"), column  # type: ignore[index]


def test_ages_beside_an_admission_day_hold_the_day_and_top_code_the_ages(tmp_path: pathlib.Path) -> None:
    """Codex's review of the first repair, item 1: the age reach no longer leaves the day counts to print as p99 and max.

    The date rule decides first: the day counts are blank, the ages beside
    them top-coded, and the age question is the one put (LANE CZ-H RULINGS
    5 (1)).
    """
    case = forms.case_named("ages_beside_days")
    result = forms.run_form(case.table, tmp_path, health_zoo.SMOKE_ROWS, answered=False, disguised=case.disguised)
    assert result["failed"] == [], result["steps"]
    assert _bar(result) == []
    assert result["held"]["age_value"]  # type: ignore[index]
    block = next(block for block in json.loads((tmp_path / "ages_days-profile.json").read_text(encoding="utf-8"))["columns"]
                 if block["name"] == "age_value")
    assert block["top_coded"] == taxonomy.TOP_CODE
    assert f"{forms.day_count(forms.AGE_BESIDE_DAYS)}" not in json.dumps(block)



# -- LIMIT (h), WIRED AT LANE SH3'S MERGE (batch 4o; LANE CZ-H RULINGS 5 (1) and 7 (5)) --------------------------
# The date rule keeps as an age every count no older than 125 years IN THE UNIT
# OF THE COLUMN'S AGES -- the mark lane SH3 reads from the column's name, its
# answer or its description (plan P4-D454: 32,871 days stand for 90 years, so
# 125 years are 45,654 days) -- and holds the day counts past it. Both cases are
# red on the mutant that reads 125 years in years whatever the unit
# (`profile.build_document`'s `ages_up_to` given `TOP_CODE_REACH_CEILING`): every
# age written in days, five figures, is then held as a date.

_DAYS_MARK = taxonomy.AGE_MARKS["d"]


def _ages_in_days(n: int) -> "list[str]":
    """Ages of 40 to 100 written in days, on 24 rows in 25, and the admission day as a count on the 25th."""
    return [
        f"{forms.day_count(forms.AGE_BESIDE_DAYS)}" if row % 25 == 24 else f"{(40 + row % 61) * 365}"
        for row in range(n)
    ]


def test_ages_named_in_days_keep_every_age_and_hold_the_day(tmp_path: pathlib.Path) -> None:
    """A column whose name states days (`age_in_days`): its ages are kept, top-coded at the days' mark, and the day held."""
    path = tmp_path / "ages_in_days.csv"
    path.write_text("\n".join(["age_in_days", *_ages_in_days(600)]) + "\n", encoding="utf-8", newline="\n")
    named: "list[str]" = []
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), [], top_code=True, safe_harbor_no=[], dated_values=named,
        dated_held=("age_in_days",),
    )
    block = json.loads(json.dumps(document["columns"][0], default=str))
    assert named == ["age_in_days"]
    assert block["top_coded"] == _DAYS_MARK, block
    # The 576 ages are kept, the 24 day counts are blank: no age is a date.
    assert block["n_missing"] == 24, block
    assert f"{forms.day_count(forms.AGE_BESIDE_DAYS)}" not in json.dumps(block)


def _rounds(
    tmp_path: pathlib.Path, source: pathlib.Path, wanted: "dict[str, tuple[str, ...]]", validated: int = 0,
) -> "list[str]":
    """The command's profile run on `source`, then round by round with each column's first wanted answer its question offers.

    Returns the answers given, in order. Then generate, which exits 0, and
    validate, which exits ``validated``.
    """
    questions = tmp_path / f"{source.stem}-questions.json"
    code, said = forms._command(["profile", f"{source}", "--replace"], False)
    assert code == 0, said
    given_all: "list[str]" = []
    for _round in range(4):
        document = json.loads(questions.read_text(encoding="utf-8"))
        changed = False
        for entry in health_zoo._entries(document):
            if f"{entry.get('your_answer') or ''}":
                continue
            offered = health_zoo._offered(entry)
            given = next((answer for answer in wanted.get(f"{entry.get('column', '')}", ()) if answer in offered), "")
            if given:
                entry["your_answer"] = given
                given_all += [given]
                changed = True
        if not changed:
            break
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        code, said = forms._command(["profile", f"{source}", "--replace", "--answers", f"{questions}"], False)
        assert code == 0, said
    profile_file = tmp_path / f"{source.stem}-profile.json"
    code, said = forms._command(["generate", f"{profile_file}", "--replace", "--seed", "0"], False)
    assert code == 0, said
    code, said = forms._command(["validate", f"{profile_file}", "--replace"], False)
    assert code == validated, said
    return given_all


def _held_day(tmp_path: pathlib.Path, stem: str, column: str, mark: int) -> None:
    """The column's block top-coded at `mark`, its 24 day cells blank and said so, and the day in no file and no twin cell."""
    day = f"{forms.day_count(forms.AGE_BESIDE_DAYS)}"
    profile_file = tmp_path / f"{stem}-profile.json"
    block = next(block for block in json.loads(profile_file.read_text(encoding="utf-8"))["columns"] if block["name"] == column)
    assert block["top_coded"] == mark, block
    assert block["n_missing"] == 24, block
    assert taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in json.dumps(block)
    for name in (f"{stem}-profile.json", f"{stem}-questions.json", f"{stem}-profile.txt", f"{stem}-twin-report.txt"):
        if (tmp_path / name).is_file():
            assert day not in (tmp_path / name).read_text(encoding="utf-8"), name
    twin_header, twin_rows = forms.read_csv(tmp_path / f"{stem}-twin.csv")
    assert [row for row in twin_rows if row[twin_header.index(column)] == day] == []


def test_ages_named_in_days_through_the_command_keep_their_ages_and_hold_the_day(tmp_path: pathlib.Path) -> None:
    """The same through the command: its identity question answered `measurement`, its age and dates questions left open.

    A STATED LIMIT OF THE MERGE, pinned so that its repair is a visible
    decision: method G7.15 keeps the twin's numbers off the date bands
    without the unit's oldest age, so the twin's ages in days, all inside a
    band, are moved off it and `validate` misses this column's percentiles,
    tails and mean (exit 3). Nothing real is shown or written.
    """
    header, rows = forms.ages_beside_days(health_zoo.SMOKE_ROWS, forms.SEEDS["ages_in_days"], True)
    source = tmp_path / "ages_named_days.csv"
    lines = [",".join(["record_id", "age_in_days", "status_word"])] + [",".join(row) for row in rows]
    source.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    assert len(header) == 3
    given = _rounds(tmp_path, source, {"record_id": ("identifier",), "age_in_days": ("measurement",)}, validated=3)
    assert "measurement" in given
    _held_day(tmp_path, "ages_named_days", "age_in_days", _DAYS_MARK)


def test_a_unit_answered_to_the_age_question_keeps_the_day_held(tmp_path: pathlib.Path) -> None:
    """The batch notes' AT CZ-H'S MERGE, ADDED 2: a unit answered to lane SH3's age question leaves the day cells held.

    Codex's ages of 40 to 100 beside the admission day as a count, through the
    command round by round: the age question answered `years` (a unit, which
    keeps the top-code), the column's next question `measurement`, the
    question about dates `yes`; the day cells stay blank until that question
    says `no`, and no file or twin cell holds the day.
    """
    case = forms.case_named("ages_beside_days")
    header, rows = case.table.build(health_zoo.SMOKE_ROWS, forms.SEEDS["ages_days"])
    source = tmp_path / "ages_days.csv"
    source.write_bytes(case.table.write(header, rows))
    wanted = {"record_id": ("identifier",), "age_value": ("years", "measurement", asking.ANSWER_SAFE_HARBOR_YES)}
    given = _rounds(tmp_path, source, wanted)
    assert [answer for answer in given if answer in asking.AGE_UNIT_ANSWERS] == ["years"]
    _held_day(tmp_path, "ages_days", "age_value", taxonomy.TOP_CODE)


def test_a_zip_in_the_day_band_is_still_a_zip(tmp_path: pathlib.Path) -> None:
    """The ZIP reach reads the cells as written: ZIP codes of 10,000 to 76,700 are held whole and put the ZIP question first.

    The date rule names the column too, its question following the ZIP
    question's `no` (one question a column); the ages' reach alone reads
    the cells the date rule leaves (`profile._reach_here`).
    """
    path = tmp_path / "zips.csv"
    path.write_text("\n".join(["zip"] + [f"{52200 + place % 80}" for place in range(600)]) + "\n", encoding="utf-8", newline="\n")
    five: "list[str]" = []
    named: "list[str]" = []
    profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), [], top_code=True, safe_harbor_no=[], dated_values=named,
        five_figures=five,
    )
    assert (five, named) == (["zip"], ["zip"])


def test_a_declared_missing_marker_stays_a_missing_value(tmp_path: pathlib.Path) -> None:
    """Codex's review of the first repair, item 2: `--missing-value 999999999` keeps its cells, which no longer read as seconds."""
    found = forms.column_run(
        forms.MARKER_TABLE, tmp_path, health_zoo.SMOKE_ROWS, "reading_value", ("--missing-value", forms.MISSING_MARKER),
        answered=True, dates_answer="",
    )
    assert found["failed"] == [], found["steps"]
    block = found["block"]
    assert block["missing_by_source"] == {forms.MISSING_MARKER: health_zoo.SMOKE_ROWS // 25}, block["missing_by_source"]
    assert taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) not in block["remarks"]
    assert [cell for cell in found["twin"] if cell == forms.MISSING_MARKER] != []  # type: ignore[attr-defined]


def test_a_run_whose_generation_fails_is_measured_by_no_key(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of the first repair, item 3: a failed stage turns K-HZ-16 red, named, and no twin before it is read."""
    import kpi_rules

    real = forms._command

    def refused(arguments: "list[str]", small_tables_refused: bool) -> "tuple[int, str]":
        if arguments[0] == "generate":
            return 2, "generation refused"
        return real(arguments, small_tables_refused)

    case = forms.case_named("stray_zip")
    monkeypatch.setattr(forms, "_command", refused)
    result = forms.run_form(case.table, tmp_path, health_zoo.SMOKE_ROWS, answered=True, disguised=case.disguised)
    assert result["failed"] == ["generate", "validate"] and "twin" not in result
    assert forms.case_values("stray_zip", result, False) == {}
    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-HZ-16"]
    measured = {key: number for key, number in entry["value_at"]["value"].items() if not key.startswith("case_stray_zip_")}
    measured["stages_failed"] = 2
    verdict = kpi_rules.judge(entry, measured)
    # A drop whatever the entry's status: FAIL while it is GREEN, OPEN-WORSE since batch 4o's seal opened it on the
    # recorded keys its merges moved (LANE I4m RULINGS 20 (3)).
    assert verdict.is_drop and "case_stray_zip_twin: not measured" in verdict.message, verdict
    # ...and a chance seed whose generation fails reads no twin left before it.
    twin = tmp_path / "chance" / "twin.csv"
    twin.parent.mkdir()
    twin.write_text("stale\n", encoding="utf-8", newline="\n")
    found = forms.chance_cells(case.table, {}, tmp_path / "chance" / "profile.json", twin, 600, 1, False, (0,), None)
    assert found == {"0": {"exit": 2}} and not twin.exists()


def test_every_output_says_what_the_twin_of_a_held_day_column_writes() -> None:
    """No false sentence (LANE CZ-H RULINGS 1 (2) (i)): a held column of counted dates, whose twin the walk writes, says so."""
    from synthtwin import grains

    cells = [f"{60_000 + place}" for place in range(200)]
    column = taxonomy.profile_column("day", 1, cells, len(cells), taxonomy.Settings(), True)
    made_up = taxonomy.rendered(taxonomy.REMARK_HELD_COUNTS_ARE_MADE_UP, ())
    valid = taxonomy.rendered(taxonomy.REMARK_HELD_DATES_ARE_VALID, ())
    said = [f"{remark}" for remark in taxonomy.with_held_dates(column, {"kind": grains.COUNTED}).remarks]
    assert said == [made_up]
    said = [f"{remark}" for remark in taxonomy.with_held_dates(column, {"kind": "dates"}).remarks]
    assert said == [valid]


# -- a held day number written wider decodes to no day (method G9.6b) --------------


def _widened_day_room(layout: str = "%%%%%.%%", excluded: str = "9%%%%.%%") -> "generation._OffTheReal":
    facts = contract.IdentifierFacts(
        layout_forms={layout: 600},
        layout_prefixes={},
        layout_exclusions={layout: (excluded,), parsing.EXCLUSION_SPILL: ("%%%%%%%%%",)},
        min_length=len(layout),
        max_length=len(layout),
        all_whole_numbers=False,
        n_all_digits=0,
        n_code_alphabet=0,
        n_distinct_by_occurrences={"2": 300},
    )
    return generation._off_the_real_room(facts, ())


def test_a_day_number_written_wider_keeps_what_no_real_day_holds() -> None:
    room = _widened_day_room()
    assert generation._widened_template(room, "%%%%%.%%") == "9%%%%.%%%%"
    # A filling of it is kept off the real and no day of the band reads in it.
    taken = generation._respelled(room, "66123.00")
    assert taken.startswith("9") and len(taken) == 10, taken
    assert date_counts.counted_figures(taken[:5]) == 0


def test_widened_without_that_rule_a_day_number_decodes_to_a_day(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant kept as a case (LANE CZ-H RULINGS 1 (4)): `%%%%%.%%%%`, whose whole figures read a real day's."""
    monkeypatch.setattr(generation, "_widens_off_the_real", lambda layout: False)
    room = _widened_day_room()
    assert generation._widened_template(room, "%%%%%.%%") == "%%%%%.%%%%"


def test_a_layout_that_is_no_decimal_widens_as_it_did(monkeypatch: pytest.MonkeyPatch) -> None:
    """The rule is a decimal number's: a layout holding a dash keeps what `parsing.widened_layout` gives, red on the rule asked of any layout."""
    room = _widened_day_room("%%%%-%%", "9%%%-%%")
    plain = generation._widened_template(room, "%%%%-%%")
    assert not plain.startswith("9"), plain
    monkeypatch.setattr(generation, "_widens_off_the_real", lambda layout: True)
    room = _widened_day_room("%%%%-%%", "9%%%-%%")
    assert generation._widened_template(room, "%%%%-%%").startswith("9")


# -- the owner's table floor: one case ---------------------------------------------


def test_at_the_floor_the_answer_column_answered_shows_and_writes_no_real_date(tmp_path: pathlib.Path) -> None:
    result = forms.run_form(forms.table_named("answers_long"), tmp_path, health_zoo.KPI_ROWS, answered=True)
    assert _bar(result) == []
    assert result["asked"]["answer_value"], result["offered"]  # type: ignore[index]
    assert "yes" in result["given"]["answer_value"], result["given"]  # type: ignore[index]


# THE TWIN WRITES NO NUMBER INSIDE A BAND OF A COLUMN WHOSE DATES IN
# DISGUISE ARE HELD (method G7.15; repair 1's whole suite on 5ab38ff6,
# tests/test_moment_window_anchor.py). Its description read every count
# inside a band as a blank cell, and the validator reads the twin the same
# way, so a number the twin drew across the gap was one blank more than
# the description held: five thousand amounts, three such numbers, nine
# checks missed.


def _charges(tmp_path: pathlib.Path) -> pathlib.Path:
    """Two thousand amounts with cents, 68 of them five-figure counts in a day band, read as a measurement."""
    import random

    draw = random.Random(3)
    path = tmp_path / "charges.csv"
    rows = ["amount"] + [f"{draw.lognormvariate(7, 1.3):.2f}" for _place in range(2000)]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    return path


def _charges_twin(tmp_path: pathlib.Path) -> "tuple[int, list[str]]":
    """profile, generate and validate the amounts, unanswered: validate's exit and the twin's cells."""
    path = _charges(tmp_path)
    for arguments in (
        ["profile", f"{path}", "--replace"],
        ["generate", f"{tmp_path / 'charges-profile.json'}", "--replace", "--seed", "0"],
    ):
        code, said = forms._command(arguments, False)
        assert code == 0, said
    document = json.loads((tmp_path / "charges-profile.json").read_text(encoding="utf-8"))
    block = next(block for block in document["columns"] if block["name"] == "amount")
    assert block["role"] == taxonomy.ROLE_CONTINUOUS, block["role"]
    assert taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in block["remarks"]
    code, _said = forms._command(["validate", f"{tmp_path / 'charges-profile.json'}", "--replace"], False)
    cells = (tmp_path / "charges-twin.csv").read_text(encoding="utf-8").split("\n")[1:-1]
    return code, cells


def test_a_twin_draws_no_number_inside_a_band_and_meets_its_description(tmp_path: pathlib.Path) -> None:
    code, cells = _charges_twin(tmp_path)
    assert [cell for cell in cells if cell and date_counts.date_in_disguise(cell)] == []
    assert code == 0


def test_without_the_move_the_twin_misses_its_own_description(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generation, "_numbers_kept_off_the_bands", lambda column: 0)
    code, cells = _charges_twin(tmp_path)
    assert [cell for cell in cells if cell and date_counts.date_in_disguise(cell)] != []
    assert code == 3


# Each cell beside what it is written as, in one column: below the band or
# the width, or past them, the nearer; a value taken moves the next on.
_MOVED = [
    ("12345.67", "9999.67"),
    ("12,345.67", "9,999.67"),
    ("70000.50", "76702.50"),
    ("-12345", "-9999"),
    ("-20000.5", "-25567.5"),
    ("+43351", "+76702"),
    (" 12345 ", " 9999 "),
    ("66274,43200", "76703,43200"),
    ("1600000000", "2871763200"),
    ("2000000000", "2871763201"),
    ("1600000000000", "2871763200000"),
    ("9999.5", "9999.5"),
    ("NA", "NA"),
]


def test_each_number_inside_a_band_goes_to_the_nearest_value_none_reads() -> None:
    cells = [cell for cell, _written in _MOVED]
    written = date_counts.kept_off_the_bands(cells, [True] * len(cells), frozenset({"NA"}))
    assert written == [moved for _cell, moved in _MOVED]
    assert [cell for cell in written if date_counts.date_in_disguise(cell)] == []


def test_each_different_value_keeps_its_cells_and_meets_no_other() -> None:
    cells = ["12000", "12000", "13000", "9999", "9998", "14000.25", "abc", "12000"]
    numbers = [True, True, True, True, True, True, False, False]
    written = date_counts.kept_off_the_bands(cells, numbers, frozenset())
    assert written == ["9997", "9997", "9996", "9999", "9998", "9999.25", "abc", "12000"]


def test_a_missing_value_and_a_label_stay_as_written() -> None:
    """A cell spelled as one of the column's missing values, or one the numeric machinery did not write, is kept."""
    cells = ["11111", "12000", "13000"]
    assert date_counts.kept_off_the_bands(cells, [True, True, False], frozenset({"11111"})) == ["11111", "9999", "13000"]


def test_the_oracle_writes_the_same_cells() -> None:
    import importlib.util
    import random

    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors",
        pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py",
    )
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    assert oracle.DATED_VALUES_HELD == taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    draw = random.Random(7)
    for _case in range(20):
        cells = [
            draw.choice([
                f"{draw.lognormvariate(8, 1.5):.2f}", f"{draw.randint(5000, 99999)}", f"-{draw.randint(9000, 30000)}",
                f"{draw.randint(10**8, 3 * 10**9)}", "9999", f"{draw.randint(9990, 9999)}.{draw.randint(0, 99):02d}",
            ])
            for _place in range(60)
        ]
        assert date_counts.kept_off_the_bands(cells, [True] * len(cells)) == oracle.kept_off_the_date_bands(cells), cells
    # The oracle reads the plain numbers its cases write, the MUMPS day with
    # its seconds and a missing value aside.
    plain = [pair for pair in _MOVED if "," not in pair[0] or "." in pair[0]][:-1]
    assert oracle.kept_off_the_date_bands([cell for cell, _written in plain]) == [moved for _cell, moved in plain]


def _random_column(draw: "object") -> "tuple[list[str], list[bool], frozenset[str]]":
    """One seeded column of the differential test: counts in and near the bands, with cents, signs, groups and seconds."""
    import random

    assert isinstance(draw, random.Random)
    shape = draw.randrange(7)
    count = 400 if shape == 6 else draw.choice((5, 20, 60, 200))
    cells: "list[str]" = []
    for _place in range(count):
        if draw.random() < 0.08:
            cells += [draw.choice(("", "NA", "pending", "-9", "  "))]
        elif shape == 0:
            cells += [f"{draw.randint(9_000, 78_000)}"]
        elif shape == 1:
            cells += [f"{draw.lognormvariate(8.83, 1.08):.2f}"]
        elif shape == 2:
            whole = draw.randint(9_990, 10_010) if draw.random() < 0.5 else draw.randint(76_690, 76_710)
            cells += [f"{whole}.{draw.randint(0, 99):02d}" if draw.random() < 0.3 else f"{whole}"]
        elif shape == 3:
            whole = draw.randint(-70_000, 70_000)
            cells += [f"{whole:,}" if draw.random() < 0.3 else f"{whole}"]
        elif shape == 4:
            whole = draw.choice((66_274, 66_275, 10_000, 9_999, 76_700, 76_699))
            cells += [f"{whole},{draw.randint(0, 86_399)}" if draw.random() < 0.3 else f" {whole} "]
        elif shape == 5:
            cells += [f"{draw.randint(1_500_000_000, 1_700_000_000) if draw.random() < 0.5 else draw.randint(9_990, 12_000)}"]
        else:
            # A dense run of values kept just below the band: the first
            # build read the cells again, four times as far, to place past it.
            cells += [f"{draw.randint(10_000, 10_400)}" if draw.random() < 0.2 else f"{9_999 - len(cells)}"]
    numbers = [draw.random() < 0.9 for _cell in cells]
    absent = frozenset(draw.sample(cells, min(2, len(cells)))) if draw.random() < 0.2 else frozenset()
    return cells, numbers, absent


def test_the_cells_are_read_once_and_write_what_the_first_build_wrote(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of the first repair, item 4 (LANE CZ-H RULINGS 5 (2)): 2,000 seeded columns, the same cells as 160ea30f.

    The first build is `tests/kept_off_the_bands_first.py`; columns where it
    read its cells again farther out are among them.
    """
    import random

    import kept_off_the_bands_first as first

    widened = [0]
    once = first.first_taken_near

    def counted(*given: object) -> "dict":
        widened[0] += 1
        return once(*given)  # type: ignore[arg-type]

    monkeypatch.setattr(first, "first_taken_near", counted)
    draw = random.Random(20261103)
    differ = moved = farther = 0
    for _case in range(2000):
        cells, numbers, absent = _random_column(draw)
        widened[0] = 0
        before = first.first_kept_off_the_bands(cells, numbers, absent)
        farther += widened[0] > 1
        after = date_counts.kept_off_the_bands(cells, numbers, absent)
        differ += before != after
        moved += sum(1 for cell, written in zip(cells, after) if cell != written)
    assert differ == 0
    assert moved > 50_000 and farther > 0, (moved, farther)
