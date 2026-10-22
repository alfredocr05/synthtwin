"""The zoo-fix stand-ins page holds what it computes (plan P4-D422).

WHY A FILE OF ITS OWN. The zoo-fix stand-ins page in
`docs/plans/phase-4-columns.md` is written before the code of lanes
CODES-1, CODES-2, CODES-3 and GG: nothing in the product reads it yet.
The disposition seal turns red on any edit of a sealed passage and is
re-sealed by whoever makes the edit, so it cannot tell a correction from
its undoing. This file can, for the figures the page computes, for its
reading of the product it describes, and for the one sentence of each
rule that carries the rule.

WHAT IS COMPUTED HERE, NOT READ. Rule A3's debt of the measured row 44
from the published block the page quotes; rule A2's positional census on
cells shaped like the measured i2b2 ones, its vocabulary prefix kept in
rows and gone when the same cells are counted in ten people; path (ii)'s
shape screen over a shape of each class it can refuse and over the result
words it must let through, with its named residual; the golden fixture's
`region` holding back `outlying` and its `note` naming nothing; a lone
held-back level printing its own row count (the owner's B); the code-look
test the page's `code` offer reads; the categories ceiling GG's class
reads at 600 rows; the mark set today; the twelve zoo kinds whose
`OWNERS` lines name the four lanes; and the holding questions of plan
P4-D401 that rule U reads, from that decision's own sentences.

WHAT IS NOT HERE. No lane's code exists, so nothing here says a twin
meets anything. The functions below are the page's rules written once as
the test reads them, not the product's: each lane builds its own and its
gate holds the cases.
"""
import collections
import contextlib
import csv
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import asking
from synthtwin import cli
from synthtwin import parsing
from synthtwin import taxonomy

import fixtures
import health_zoo

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
PAGE_HEADING = "## The zoo-fix stand-ins page"
DECISION_HEADING = "## Decision P4-D422"
FLOOR = 11


def _page() -> str:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index(PAGE_HEADING)
    stop = text.index(DECISION_HEADING, start)
    return text[start:stop]


def _flat(text: str) -> str:
    return " ".join(text.split())


def _form(text: str) -> str:
    """A value's form as the page writes it: figures `%`, letters `@`, every other character itself."""
    return "".join("%" if mark.isdigit() else "@" if mark.isalpha() else mark for mark in text)


def _profiled(folder: pathlib.Path, name: str, text: str) -> "dict":
    path = fixtures.write(folder, name, text)
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(["profile", f"{path}", "--replace"])
    assert code == 0, sink.getvalue()[-400:]
    stem = name.rsplit(".", 1)[0]
    return json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))


def _column(document: "dict", name: str) -> "dict":
    return next(column for column in document["columns"] if column["name"] == name)


def test_the_page_stands_once_and_its_decision_follows_it() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert text.count(PAGE_HEADING) == 1
    assert text.count(DECISION_HEADING) == 1
    assert text.index(PAGE_HEADING) < text.index(DECISION_HEADING)
    page = _page()
    for section in range(11):
        assert f"### ZS.{section} " in page, section


OPERATIVE = {
    "U": "A column is UNANSWERED for this page where",
    "U-table": "also (c) where any question of the table offering `identifier` is open, on any column",
    "A1": "is not published apart: its cells are counted in the column's commonest published form or layout, "
    "and the twin writes them there. The producer and the validator absorb alike",
    "A2": "the description lists at each place the characters at least the floor's cells hold there -- at least "
    "the floor's different subjects beside a subject column (P4-D406) -- and publishes no count",
    "A3": "the pool's level SIZES (G8.3c; not published) are drawn after the class and form debts, so every "
    "published form's debt inside the number class is a sum of whole levels",
    "C1": "A HELD column's twin meets every layout and form census its held block publishes, exactly, from "
    "made-up values",
    "C3": "that question carries the kind answers in its own entry",
    "path-i": "So on path (i) the question is put whatever the column's levels, and until it is answered `no` the "
    "column is held as P4-D401 holds a column (its common ZIPs included)",
    "path-ii": "(1) at most two words; (2) no run of five figures or more, and at most six figures in the word",
    "path-iii": "Any other label column (`categorical`, or `long_tail_labels` answered `code`) answered `no` to "
    "the Safe Harbor question",
    "code-offer": "offer HX3's `code`, in HX3's words and with its declaration, between `keep` and `identifier`",
    "NP": "a held-back name is published only where its column is NOT ATTACHED to that subject",
    "GG": "the twin writes exactly those values -- never a value inside a published empty gap",
    "GG-b": "the values below it are published, without counts, only after `no` to the Safe Harbor question",
    "W1": "contract 4.6b's RULE W1 reads every named level as an OWN-FACT GROUP",
    "PS": "this page writes no date or time stand-in and names that rule wherever one is meant",
}


@pytest.mark.parametrize("rule", sorted(OPERATIVE))
def test_each_rule_keeps_its_operative_sentence(rule: str) -> None:
    assert _flat(OPERATIVE[rule]) in _flat(_page()), rule


def test_the_safe_harbor_question_is_the_owners_sentence() -> None:
    owners = (
        "Could a value of this column name a person, a place smaller than a state, a birth date, "
        "or a record, account or device number?"
    )
    page = _flat(_page())
    assert owners in page
    assert "> Could a value of '<column>' name a person, a place smaller than a state, a birth date, or a record, account or device number?" in _page()
    assert "45 CFR 164.514(b)(2)(i)" in page


def test_a3_settles_row_44_where_today_overpays_its_published_form() -> None:
    published_forms = {"%%%.%": 21, "%%%.%%": 27, "@%%": 87, "@%%.%": 414, "@%%.%%": 11}
    number_levels = {"401.9": 14, "250.00": 27, "44054006": 12}
    n_numeric = 82
    owed = n_numeric - sum(number_levels.values())
    form_debt = published_forms["%%%.%"] - sum(n for v, n in number_levels.items() if _form(v) == "%%%.%")
    assert (owed, form_debt) == (29, 7)
    today = {"250.1": 10, "251": 9, "44054005": 6, "252": 4}
    assert sum(today.values()) == owed
    written = sum(n for v, n in today.items() if _form(v) == "%%%.%")
    assert number_levels["401.9"] + written == 24
    # A3: the sizes are drawn after the debt -- here 4 and 3, as the source held them,
    # each at most f - 1 -- so the published form reads its own count again.
    sizes = [4, 3]
    assert sum(sizes) == form_debt and all(1 <= size <= FLOOR - 1 for size in sizes)
    assert number_levels["401.9"] + sum(sizes) == published_forms["%%%.%"]
    page = _flat(_page())
    assert "so the held-back numbers owe 29 cells, 7 of them in `%%%.%`" in page
    assert "`%%%.%` reads 24 against 21 and validate exits 3" in page


def _census(cells: "list[tuple[str, str]]", floor: int, in_people: bool) -> "dict[str, list[str]]":
    """Rule A2 as the page writes it: per form, the characters the floor's cells (or people) hold at each place."""
    by_form: "dict[str, list[tuple[str, str]]]" = collections.defaultdict(list)
    for value, subject in cells:
        by_form[_form(value)] += [(value, subject)]
    lists: "dict[str, list[str]]" = {}
    for form, held in by_form.items():
        if len(held) < floor:
            continue
        places = []
        for place in range(len(form)):
            rows = collections.Counter(value[place] for value, _ in held)
            people: "dict[str, set[str]]" = collections.defaultdict(set)
            for value, subject in held:
                people[value[place]] |= {subject}
            places += ["".join(sorted(
                mark for mark, n in rows.items()
                if n >= floor and (not in_people or len(people[mark]) >= floor)
            ))]
        lists[form] = places
    return lists


def _prefix(places: "list[str]") -> str:
    prefix = ""
    for listed in places:
        if len(listed) != 1:
            break
        prefix += listed
    return prefix


def test_a2_keeps_the_vocabulary_prefix_in_rows_and_counts_it_in_people() -> None:
    letters = "ABCDEFGHJKLM"
    values = [f"ICD10CM:{letters[k % 12]}{k % 10}{(k * 7) % 10}.9" for k in range(36)]
    apart = [(value, f"P{k}") for k, value in enumerate(values)]
    lists = _census(apart, FLOOR, in_people=True)
    places = lists["@@@%%@@:@%%.%"]
    assert _prefix(places) == "ICD10CM:"
    assert places[-2:] == [".", "9"]
    assert places[8] == ""  # no letter of the code on the floor's cells: the form's own alphabet
    ten = [(value, f"P{k % 10}") for k, value in enumerate(values)]
    assert _prefix(_census(ten, FLOOR, in_people=True)["@@@%%@@:@%%.%"]) == ""
    assert _prefix(_census(ten, FLOOR, in_people=False)["@@@%%@@:@%%.%"]) == "ICD10CM:"
    few = [(f"ICD10CM:Z{k}.1", f"Q{k}") for k in range(FLOOR - 1)]
    assert "@@@%%@@:@%.%" not in _census(few, FLOOR, in_people=False)
    assert "listing `ICD10CM:` at its first eight places and `.9` at its last two" in _flat(_page())


def _passes_screen(word: str) -> bool:
    """Path (ii)'s shape screen as the page writes it."""
    if len(word.split()) > 2:
        return False
    if re.search(r"\d{5}", word) or sum(mark.isdigit() for mark in word) > 6:
        return False
    if "@" in word or "://" in word or "www." in word:
        return False
    if re.search(r"\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}", word):
        return False
    if re.search(r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d", word):
        return False
    if re.search(r"\d{1,3}(?:\.\d{1,3}){3}", word):
        return False
    return True


REFUSED = (
    "Called to J. Smith RN at 14:32", "555-1234", "123-45-6789", "02139-1234", "02139",
    "a.b@c.org", "2024-01-05", "01/05/2024", "10.0.0.12", "http://x.org", "www.example",
    "14:32", "MRN 0012345", "(319) 555-0100",
)
PASSED = ("TNP", "HI", "LO", "1:40", "1:1280", "N/A", ".", "Not done", ">60", "<0.5", "QNS")


@pytest.mark.parametrize("word", REFUSED)
def test_the_shape_screen_refuses_each_shaped_class(word: str) -> None:
    assert not _passes_screen(word)


@pytest.mark.parametrize("word", PASSED)
def test_the_shape_screen_lets_the_result_words_through(word: str) -> None:
    assert _passes_screen(word)


def test_the_screens_residual_is_the_one_the_page_names() -> None:
    assert _passes_screen("Smith") and _passes_screen("J. Smith")
    assert "A lone one- or two-word name typed into a measurement column cannot be told from a result word by its shape" in _flat(_page())


def test_the_golden_region_holds_back_outlying_and_note_names_nothing(tmp_path: pathlib.Path) -> None:
    text = fixtures.every_role_table()
    document = _profiled(tmp_path, "every_role_table.csv", text)
    rows = list(csv.DictReader(io.StringIO(text)))
    region = _column(document, "region")
    assert region["role"] == "categorical"
    assert (region["suppressed_levels"], region["suppressed_rows"]) == (1, 7)
    assert collections.Counter(row["region"] for row in rows)["outlying"] == 7 and len(rows) == 240
    assert "outlying" not in json.dumps(region)
    note = _column(document, "note")
    assert note["role"] == "long_tail_labels"
    assert (note["suppressed_levels"], note["suppressed_rows"]) == (182, 217)
    for column in document["columns"]:
        assert "(withheld)" not in json.dumps(column.get("shape_forms", {}))
        assert "(withheld)" not in json.dumps(column.get("layout_forms", {}))
    assert "`region` holds back `outlying` (7 of 240)" in _flat(_page())


def test_a_lone_held_back_level_prints_its_own_row_count(tmp_path: pathlib.Path) -> None:
    draw = random.Random(7)
    lines = ["sex,unit,value"]
    for k in range(600):
        sex = "X" if k < 4 else ("F" if draw.random() < 0.5 else "M")
        unit = "U" if k == 10 else ("A" if draw.random() < 0.5 else "B")
        lines += [f"{sex},{unit},{draw.gauss(50, 10):.1f}"]
    document = _profiled(tmp_path, "lone.csv", "\n".join(lines) + "\n")
    sex = _column(document, "sex")
    unit = _column(document, "unit")
    assert (sex["suppressed_levels"], sex["suppressed_rows"]) == (1, 4)
    assert (unit["suppressed_levels"], unit["suppressed_rows"]) == (1, 1)
    assert "a lone `U` prints `suppressed_rows 1`, measured again on this base" in _flat(_page())


def test_the_code_look_reaches_code_form_tails_and_not_words() -> None:
    assert asking._looks_like_a_code(["E11.9", "C50.911", "I10", "Z79.4"])
    assert asking._looks_like_a_code(["0JH60DZ", "J1885", "99213"])
    assert not asking._looks_like_a_code(["E11.9", "chest pain"])
    assert not asking._looks_like_a_code(["Penicillin", "Sulfa"])
    assert not asking._looks_like_a_code(["E11.9;I10"])
    assert not asking._looks_like_a_code(["X" * 21 + "1"])
    assert "a figure in every cell, no space, at most 20 characters" in _flat(_page())


def test_gg_reads_the_categories_ceiling_and_days_supply_falls_inside_it() -> None:
    ceiling = taxonomy.categories_ceiling(600, taxonomy.Settings())
    days_supply = {"5": 5, "7": 25, "10": 6, "14": 14, "21": 8, "28": 11, "30": 349, "84": 8, "90": 174}
    assert sum(days_supply.values()) == 600
    assert len(days_supply) <= ceiling
    assert sorted(value for value, n in days_supply.items() if n < FLOOR) == ["10", "21", "5", "84"]
    page = _flat(_page())
    assert "(`5` 5, `7` 25, `10` 6, `14` 14, `21` 8, `28` 11, `30` 349, `84` 8, `90` 174)" in page
    assert "`taxonomy.categories_ceiling`" in page


def test_the_mark_set_today_is_the_thirteen_the_page_widens() -> None:
    assert parsing.SHAPE_MARKS == "-./_:#*()[]+,"
    assert len(parsing.SHAPE_MARKS) == 13
    for mark in "=|;^~":
        assert mark not in parsing.SHAPE_MARKS
    assert "today the thirteen `-./_:#*()[]+,`) gains `=`, `|`, `;`, `^` and `~`" in _flat(_page())


FOUR = ("CODES-1", "CODES-2", "CODES-3", "GG")
TWELVE = (
    "demographics", "diagnoses", "medication_orders", "imaging", "genomics", "perioperative", "labs",
    "mixed_results", "tumor_registry", "immunizations_providers", "surveys_pro", "dicom_metadata",
)


def test_the_twelve_kinds_are_the_ones_the_zoo_owns_to_the_four_lanes() -> None:
    owned = sorted(
        kind for kind, lines in health_zoo.OWNERS.items()
        if any(owner in FOUR for owner, _gap, _covers in lines)
    )
    assert owned == sorted(TWELVE)
    page = _flat(_page())
    assert ", ".join(f"`{kind}`" for kind in TWELVE[:-1]) + f" and `{TWELVE[-1]}`" in page


def test_rule_u_reads_the_holding_questions_p4_d401_names() -> None:
    text = _flat(PLAN.read_text(encoding="utf-8"))
    p4d401 = text[text.index("## Decision P4-D401"):text.index("## Decision P4-D402")]
    assert (
        "the person question, the two-numbers question, or the question answered by a measurement, a code "
        "or a record number (padded figures, figures all one width or grouped in threes, and a date count "
        "whose values are also one width)"
    ) in p4d401
    assert "the point-between-thousands question and the checklist of columns read as numbers" in p4d401
    page = _flat(_page())
    for named in (
        "the person question (routes one to four)", "the two-numbers question",
        "the question answered by a measurement, a code or a record number put to padded figures",
        "the point-between-thousands question, the checklist of columns read as numbers",
    ):
        assert named in page, named
