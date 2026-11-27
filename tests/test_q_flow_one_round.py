"""Lane Q-FLOW, step 2: the twin's questions in ONE ROUND, before anything is written, grouped by kind.

The question review (lane Q-REVIEW, section 6) measured 5 to 13 prompts in up
to four rounds on three ordinary invented tables, each Safe Harbor prompt
380 to 470 words, the same column asked two or three times, and Enter
quietly damaging the twin (a ward read as made-up codes, 585 real costs
blanked, every case date lost). The owner's decisions of 2026-11-23,
delegated: ACCEPT 1 (one round before anything is written), 2 (Safe Harbor
questions grouped by kind into lists: Enter protects every column, a release
takes the column's name typed, the last screen lists every release), 3 (a
repeating column of fewer than 1,000 different values is not asked as the
person), 4 (numbers that may be dates: Enter takes the one plausible
counting system where the column's name says date), 5 (values that read as
dates stay blank by default, the cost said in counts on the screen, and a
name that says money decides they are not dates), 6 (for a possible age,
not sure caps at 90, never hides the column); REJECT 7 (no value on the
screen or in the questions file).

Each case drives `synthtwin twin` through `cli.run` with a stand-in keyboard
(`_Planned`: it answers each prompt by the heading on screen, and records,
at each line read, whether any file of the run exists yet). Every table is
the suite's own seeded one, at the floor of 20,000 rows. Each guarded
behaviour is red on its mutant, named in its case's docstring.
"""

from __future__ import annotations

import csv
import json
import pathlib
import re

import analyst_tables
import health_zoo
from synthtwin import asking, cli, results

ROWS = 20_000

# Every heading a prompt of the twin's keyboard opens with, the one round's and the first prompt's.
_HEADS = re.compile(
    r"QUESTION \d+ OF \d+: [^\n]*|BEFORE ANYTHING IS WRITTEN|WHO ARE THE ROWS ABOUT\?"
    r"|Column \d+ of \d+: '[^'\n]*'|Columns \d+ to \d+ of \d+|COLUMN\(S\) LOOK LIKE RECORD NUMBERS"
)


class _Planned(list):  # type: ignore[type-arg]
    """A keyboard answering each prompt by its heading: the plan's line where a key of it is in the heading, Enter elsewhere.

    A prompt put again (a line it refused) is answered with Enter, so no
    plan loops. ``heads`` are the headings read, in order; ``files_seen``
    whether the twin's folder held any file when each line was read; a
    heading in ``end_at`` is answered with the end of input.
    """

    def __init__(self, plan: "dict[str, str]", folder: pathlib.Path, end_at: str = "") -> None:
        super().__init__([""] * 80)
        self.plan = plan
        self.folder = folder
        self.end_at = end_at
        self.heads: "list[str]" = []
        self.files_seen: "list[bool]" = []
        self._answered: "set[int]" = set()

    def __getitem__(self, place):  # type: ignore[no-untyped-def]
        if not isinstance(place, int):
            return super().__getitem__(place)
        self.files_seen += [self.folder.is_dir() and any(self.folder.iterdir())]
        session = cli._current()
        shown = ""
        if session is not None and isinstance(session.screen, list):
            shown = "".join(text for _stream, text in session.screen)
        found = list(_HEADS.finditer(shown))
        if not found:
            return ""
        head = found[len(found) - 1]
        self.heads += [head.group(0)]
        if self.end_at and self.end_at in head.group(0):
            return None
        if head.start() in self._answered:
            return ""
        self._answered.add(head.start())
        for key in self.plan:
            if key in head.group(0):
                return self.plan[key]
        return ""


def _twin(table: pathlib.Path, plan: "dict[str, str]", end_at: str = "") -> "tuple[results.Result, str, _Planned]":
    """`synthtwin twin TABLE` at the planned keyboard; its result, every line it printed, and the keyboard."""
    keyboard = _Planned(plan, table.parent / f"{table.stem}-synthtwin", end_at)
    screen: "list[tuple[str, str]]" = []
    result = cli.run(["twin", f"{table}"], screen=screen, ask=keyboard)
    return result, "".join(text for _stream, text in screen), keyboard


def _cohort(folder: pathlib.Path) -> pathlib.Path:
    """The review's cohort: the suite's seeded table ST1 at 20,000 rows, one row a patient."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "cohort.csv"
    analyst_tables.write(table, "ST1", ROWS, 1)
    return table


def _zoo(folder: pathlib.Path, name: str) -> pathlib.Path:
    """One of the health zoo's seeded tables at 20,000 rows (`patients`, `perioperative`)."""
    folder.mkdir(parents=True, exist_ok=True)
    for one in health_zoo.TABLES:
        if one.name == name:
            header, body = one.build(ROWS, 1)
            table = folder / f"{name}.csv"
            table.write_bytes(one.write(header, body))
            return table
    raise AssertionError(name)


def _out(table: pathlib.Path, ending: str) -> pathlib.Path:
    return table.parent / f"{table.stem}-synthtwin" / f"{table.stem}{ending}"


def _block(table: pathlib.Path, name: str) -> "dict[str, object]":
    document = json.loads(_out(table, "-profile.json").read_text(encoding="utf-8"))
    for block in document["columns"]:
        if block["name"] == name:
            assert isinstance(block, dict)
            return block
    raise AssertionError(name)


def _column(path: pathlib.Path, name: str) -> "list[str]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    place = rows[0].index(name)
    return [row[place] for row in rows[1:]]


def _numbers(path: pathlib.Path, name: str) -> "list[float]":
    found: "list[float]" = []
    for cell in _column(path, name):
        try:
            found += [float(cell.replace(",", ""))]
        except ValueError:
            continue
    return found


def _prompts(keyboard: _Planned) -> int:
    """The prompts put, each heading once (a line asked again is the same prompt)."""
    return len(keyboard.heads)


def _section(said: str, head: str) -> str:
    """The words of one prompt on screen, from its heading to the next heading."""
    start = said.index(head)
    rest = said[start + len(head):]
    after = _HEADS.search(rest)
    return said[start: start + len(head) + (after.start() if after else len(rest))]


# -- ONE ROUND, BEFORE ANYTHING IS WRITTEN (decision 1) ---------------------------


def test_the_cohort_is_asked_in_one_round_before_anything_is_written(tmp_path: pathlib.Path) -> None:
    """Enter at every prompt: no file exists while any question is on screen, at most five prompts, the long description shown once, after them, and the twin is built.

    MUTANT: `_holding_now` answering False (the held description writes its
    files) -- a file exists while the round's questions are on screen.
    """
    table = _cohort(tmp_path / "c")
    result, said, keyboard = _twin(table, {})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2500:]
    assert keyboard.files_seen and not any(keyboard.files_seen), keyboard.files_seen
    assert _out(table, "-twin.csv").is_file()
    assert 2 <= _prompts(keyboard) <= 5, keyboard.heads
    assert "MORE QUESTION(S), FROM THE QUESTIONS FILE" not in said
    assert "described before" not in said
    assert said.count("These three files will be written") == 1
    assert said.index("BEFORE ANYTHING IS WRITTEN") < said.index("These three files will be written")


def test_the_end_of_input_at_the_last_screen_writes_nothing(tmp_path: pathlib.Path) -> None:
    """Ctrl+D at the last screen: no folder and no file, the run refused in the first prompt's words."""
    table = _cohort(tmp_path / "s")
    result, said, _keyboard = _twin(table, {}, end_at="BEFORE ANYTHING IS WRITTEN")
    assert result.verdict == results.REFUSED, said[-2000:]
    assert not (table.parent / "cohort-synthtwin").exists()


# -- THE KINDS, GROUPED (decisions 2 and 6) -----------------------------------------


def test_ages_are_one_list_where_enter_caps_and_a_name_typed_releases(tmp_path: pathlib.Path) -> None:
    """`age` and `crp` in one list with the legal paragraph once: Enter caps both at 90; `crp` typed releases its tail, `age` stays capped.

    MUTANT: the ages list answering a name typed `yes` -- crp stays capped.
    """
    table = _cohort(tmp_path / "a")
    result, said, _keyboard = _twin(table, {})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    ages = _section(said, [one for one in _HEADS.findall(said) if "AGES OVER 89" in one][0])
    assert "age" in ages and "crp" in ages and ages.count("45 CFR 164.514(b)(2)(i)") == 1
    assert "months" not in ages.split("Enter =")[0]
    assert "top_coded" in _block(table, "crp") and "top_coded" in _block(table, "age")
    assert max(_numbers(_out(table, "-twin.csv"), "crp")) <= 90
    released = _cohort(tmp_path / "b")
    result, said, _keyboard = _twin(released, {"AGES OVER 89": "crp"})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert "top_coded" not in _block(released, "crp") and "top_coded" in _block(released, "age")
    assert max(_numbers(_out(released, "-twin.csv"), "crp")) > 90
    assert "crp (not an age)" in _section(said, "BEFORE ANYTHING IS WRITTEN")


def test_a_release_takes_the_column_name_typed_never_a_bare_yes(tmp_path: pathlib.Path) -> None:
    """The Safe Harbor list of the demographics export: `yes`, `no` and `1` are refused and asked again (then Enter), so every listed column stays hidden; Enter everywhere publishes no birth date, ZIP code or city.

    MUTANT: the list reader taking any word as Enter -- the refusal's words
    are not shown.
    """
    table = _zoo(tmp_path / "p", "patients")
    result, said, keyboard = _twin(table, {"MAY NAME A PERSON": "yes"})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    harbor = [one for one in keyboard.heads if "MAY NAME A PERSON" in one]
    assert len(harbor) == 2, keyboard.heads
    assert "Please type the names of columns listed above" in said
    for name in ("dob_iso", "dob_us", "dob_text", "zip5", "birth_city"):
        assert _block(table, name)["role"] == "identifier", name
    real = set(_column(table, "zip5")) | set(_column(table, "dob_iso"))
    twin = set(_column(_out(table, "-twin.csv"), "zip5")) | set(_column(_out(table, "-twin.csv"), "dob_iso"))
    assert not (real & twin - {""})
    assert "released by your answers: none" in _section(said, "BEFORE ANYTHING IS WRITTEN")


# -- DECISIONS 3, 4 AND 5 ----------------------------------------------------------


def test_a_few_valued_column_is_not_asked_as_the_person_and_keeps_its_values(tmp_path: pathlib.Path) -> None:
    """The cohort's `ward` (12 values) is put no question, is read as categories, and its twin writes its real wards; the last screen says why.

    MUTANT: `_few_valued_not_the_person` answering False -- ward is put
    the person question and Enter holds it (its twin writes made-up codes).
    """
    table = _cohort(tmp_path / "w")
    result, said, keyboard = _twin(table, {})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert not [one for one in keyboard.heads if "'ward'" in one], keyboard.heads
    assert _block(table, "ward")["role"] == "categorical"
    assert set(_column(_out(table, "-twin.csv"), "ward")) <= set(_column(table, "ward"))
    assert "not asked whether it names the person" in _section(said, "BEFORE ANYTHING IS WRITTEN")
    assert "ward (12 values)" in _section(said, "BEFORE ANYTHING IS WRITTEN")


def test_a_money_name_keeps_its_values_that_read_as_dates(tmp_path: pathlib.Path) -> None:
    """The cohort's `cost`: no question, its values read as written, and the twin's mean cost within 5% of the real (22% low when they were blanked).

    MUTANT: `_says_money` answering False -- cost is put the dated-values
    question, Enter blanks its five-figure costs and the mean falls.
    """
    table = _cohort(tmp_path / "m")
    result, said, _keyboard = _twin(table, {})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert "NUMBERS THAT MAY BE DATES OF PEOPLE" not in said
    real = _numbers(table, "cost")
    twin = _numbers(_out(table, "-twin.csv"), "cost")
    assert abs(sum(twin) / len(twin) - sum(real) / len(real)) < 0.05 * (sum(real) / len(real))
    assert "its name says an amount of money: cost" in _section(said, "BEFORE ANYTHING IS WRITTEN")
    questions = _out(table, "-questions.json").read_text(encoding="utf-8")
    assert "585" not in questions and "of 20,000 values" not in questions


def test_a_date_named_count_of_days_is_read_as_dates_on_enter(tmp_path: pathlib.Path) -> None:
    """The operating-room log's `case_date_serial`: Enter takes days from 30 December 1899 (2023 to 2024), it is not asked whether it holds ZIP codes, and every twin value reads as a date.

    MUTANT: `_plausible_date_count` answering none -- Enter holds the column
    and no twin value reads as a date.
    """
    table = _zoo(tmp_path / "o", "perioperative")
    result, said, keyboard = _twin(table, {"'surgery_id'": "3", "'patient_id'": "3"})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    case = [one for one in keyboard.heads if "'case_date_serial'" in one]
    assert len(case) == 1, keyboard.heads
    assert "Press Enter to read them as dates" in _section(said, case[0])
    assert _block(table, "case_date_serial")["role"] != "identifier"
    # Every twin value reads as a day of 2000 to 2030 counted from 30 December
    # 1899 (none did with Enter before); the dates zone's own spread of the
    # days past the real months is lane IN-5's (the 2026-11-22 ruling).
    cells = [one for one in _column(_out(table, "-twin.csv"), "case_date_serial") if one.strip()]
    days = [int(one) for one in cells if one.strip().isdigit()]
    assert cells and len(days) == len(cells) and all(36526 <= day <= 47483 for day in days), (min(days), max(days))
    assert "not asked whether its numbers are ZIP codes" in _section(said, "BEFORE ANYTHING IS WRITTEN")
    assert "case_date_serial (read as dates" in _section(said, "BEFORE ANYTHING IS WRITTEN")


def test_the_rules_read_names_as_whole_words() -> None:
    """Decision 5's money words and decision 4's date words are read as whole words of a column's name; decision 3 spares a key or a person name."""
    assert cli._says_money("cost_in_total") and cli._says_money("ChargeAmount") and not cli._says_money("costume_code")
    assert cli._says_date("case_date_serial") and cli._says_date("admitDt") and not cli._says_date("fu_days")
    question = asking.Question("ward", "categorical", asking.BECAUSE_REPEATS_AND_MANY, "", [asking.Choice(asking.ANSWER_KEEP, "", "")], asking.ANSWER_KEEP)
    assert cli._few_valued_not_the_person(question, {"ward": 12})
    assert not cli._few_valued_not_the_person(question, {"ward": 1200})
    for name in ("patient_id", "subject", "household_no", "family", "visit_id"):
        named = asking.Question(name, "categorical", asking.BECAUSE_REPEATS_AND_MANY, "", [asking.Choice(asking.ANSWER_KEEP, "", "")], asking.ANSWER_KEEP)
        assert not cli._few_valued_not_the_person(named, {name: 12}), name


def test_a_list_line_names_whole_columns_and_their_words() -> None:
    """The grouped prompts' reader: names whatever their capitals, the longest first, a word after a name, anything else refused."""
    names = ("age", "age_m", "crp")
    assert cli._names_typed("crp", names) == [("crp", "")]
    assert cli._names_typed("AGE_M months, crp", names, ("months", "weeks")) == [("age_m", "months"), ("crp", "")]
    assert cli._names_typed("", names) == []
    assert cli._names_typed("yes", names) is None
    assert cli._names_typed("crpx", names) is None
    assert cli._names_typed("age weeks;crp", names, ("months", "weeks")) == [("age", "weeks"), ("crp", "")]


def test_record_numbers_are_one_list_and_a_code_answer_brings_its_safe_harbor_question_into_the_round(tmp_path: pathlib.Path) -> None:
    """The demographics export: `patient_id` and `zip5` in one list of record numbers; `zip5 code` typed, its ZIP code question is put in the same round's Safe Harbor list, and Enter there keeps it hidden.

    MUTANT: the list left empty (each column put alone) -- `patient_id` and
    `zip5` are each put a question of their own.
    """
    table = _zoo(tmp_path / "z", "patients")
    result, said, keyboard = _twin(table, {"LOOK LIKE RECORD NUMBERS": "zip5 code"})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    listed = [one for one in keyboard.heads if "LOOK LIKE RECORD NUMBERS" in one]
    assert len(listed) == 1, keyboard.heads
    shown = _section(said, "COLUMN(S) LOOK LIKE RECORD NUMBERS")
    assert "patient_id" in shown and "zip5" in shown
    assert not [one for one in keyboard.heads if "'patient_id'" in one or "'zip5'" in one], keyboard.heads
    harbor = _section(said, [one for one in _HEADS.findall(said) if "MAY NAME A PERSON" in one][0])
    assert "zip5" in harbor
    assert keyboard.files_seen and not any(keyboard.files_seen)
    assert _block(table, "zip5")["role"] == "identifier"
    assert _block(table, "patient_id")["role"] == "identifier"
    assert "MORE QUESTION(S), FROM THE QUESTIONS FILE" not in said


def test_a_length_of_time_is_an_answer_of_its_own(tmp_path: pathlib.Path) -> None:
    """The operating-room log's `case_duration` (hours and minutes): `duration` typed is taken, and the column keeps its times reading and layout.

    MUTANT: `duration` left out of the words the question takes -- it is
    refused and asked again.
    """
    table = _zoo(tmp_path / "d", "perioperative")
    result, said, keyboard = _twin(table, {"'case_duration'": "duration"})
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    asked = [one for one in keyboard.heads if "'case_duration'" in one]
    assert len(asked) == 1, keyboard.heads
    assert "Type duration if they are lengths of time" in _section(said, asked[0])
    assert "Please type one of the answers offered" not in _section(said, asked[0])
    assert _block(table, "case_duration")["role"] == "time_of_day"


def test_a_question_answered_again_from_the_last_screen_replaces_its_answers(tmp_path: pathlib.Path) -> None:
    """`crp` released at the ages list, then question 2 put again from the last screen and answered with Enter: crp is capped again, and the second last screen no longer says it released.

    MUTANT: the last screen reading a question's number as nothing it
    knows -- crp stays released.
    """
    table = _cohort(tmp_path / "g")
    screen: "list[tuple[str, str]]" = []
    result = cli.run(["twin", f"{table}"], screen=screen, ask=["", "crp", "", "2", "", ""])
    said = "".join(text for _stream, text in screen)
    assert result.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert said.count("BEFORE ANYTHING IS WRITTEN") == 2
    first = said.index("BEFORE ANYTHING IS WRITTEN")
    second = said.index("BEFORE ANYTHING IS WRITTEN", first + 1)
    assert "crp (not an age)" in said[first:second]
    assert "crp (not an age)" not in _section(said[second - 80:], "BEFORE ANYTHING IS WRITTEN")
    assert "top_coded" in _block(table, "crp")
