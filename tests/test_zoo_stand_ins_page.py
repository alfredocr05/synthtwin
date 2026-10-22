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
rows and gone when the same cells are counted in ten people; A2's three
stages of stand-ins on the zoo's own tumour registry, 0 of 81 cells out of
the TNM grammar where every place falling to the alphabet put 7 out, and
on a form under the floor whose vocabulary marks stage (3) keeps; A2's
forced case, refused; path (ii)'s shape screen over a shape of each class
it can refuse, item by item against the page's own list, and over the
result words it must let through, with its named residual; path (iii)'s
hold of a label column with a figure in every present cell, and the ZIP
column half written ZIP+4 that this base describes with no question; the
golden fixture's `region` holding back `outlying`, its `note` naming
nothing and its few-valued numbers outside GG's class, so no golden
moves; a lone held-back level printing its own row count (the owner's B);
the code-look test the page's `code` offer reads; the categories ceiling
GG's class reads at 600 rows and `days_supply` inside the class; the mark
set today; the twelve zoo kinds whose `OWNERS` lines name the four lanes,
each in the page's table of the kinds the lanes turn; and the holding
questions of plan P4-D401 that rule U reads, from that decision's own
sentences.

WHAT IS NOT HERE. No lane's code exists, so nothing here says a twin
meets anything. The functions below are the page's rules written once as
the test reads them, not the product's: each lane builds its own and its
gate holds the cases.
"""
import collections
import contextlib
import csv
import io
import itertools
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
    "U-reach": "**And for every NAME (ZS.3), every RARE VALUE (ZS.4) and every positional census beyond a form's "
    "constant marks (A2)**, also (c)",
    "A1": "is not published apart: its cells are counted in the column's commonest published form or layout, "
    "and the twin writes them there. The producer and the validator absorb alike",
    "A1-people": "that fewer than the floor's cells wear -- fewer than the floor's different subjects beside a "
    "subject column -- is not published apart",
    "A2": "the description lists at each place the characters at least the floor's cells hold there -- at least "
    "the floor's different subjects beside a subject column (P4-D406) -- and publishes no count",
    "A2-after-no": "and it does so only once the column's Safe Harbor question is answered `no` and rule U clears (ZS.1)",
    "A2-unanswered": "Unanswered, it lists at each place only the character every cell of the form holds there, "
    "published levels included",
    "A2-forced": "neither does a form with a place whose list is empty while its held-back cells H exceed (a-1)(f-1)",
    "A2-stages": "(1) each place's list, a place with an empty list taking the characters the form's published levels "
    "wear there; (2) each place's list together with the characters the form's published levels wear there; (3) the "
    "places widened to the form's alphabet one at a time from the last",
    "A2-label": "A2 fills the LABEL class only: a held-back level G8.3a owes the number class is written by A3 alone.",
    "A2-codes": "A zoo `codes` check (every twin value one the real writes) is met only by names (CODES-2) or by A2 "
    "reproducing every held-back level (TNM, GCS), never by a made-up stand-in.",
    "A2-floor": "An unlisted character's count lies in 0 to f-1, a bound that contains 0 -- nothing published forces "
    "any one character to appear",
    "A3": "the pool's level SIZES (G8.3c; not published) are drawn after the class and form debts, so every "
    "published form's debt inside the number class is a sum of whole levels",
    "A3-widths": "each number stand-in is written at its form's integer and fraction widths (`%%%.%`: three and one), "
    "inside the published range, off every published level",
    "C1": "A HELD column's twin meets every layout and form census its held block publishes, exactly, from "
    "made-up values",
    "C2": "each placeholder is written in its own spelling and each constant figure after the point as the source's",
    "C3": "that question carries the kind answers in its own entry",
    "CODES-3-root": "the figures-and-points root every cell shares is kept",
    "CODES-3-scope": "`parsing.is_a_literal_prefix` no longer asks for a letter only on a column whose every cell has "
    "the UID shape (a first arc of `0`, `1` or `2` and two points or more)",
    "yes-no-root": "A column held by the Safe Harbor question's `yes` keeps ruling 1's prefix only where it holds a "
    "letter, as today: no figure root is kept on it",
    "path-i": "So on path (i) the question is put whatever the column's levels, and until it is answered `no` the "
    "column is held as P4-D401 holds a column (its common ZIPs included)",
    "path-ii": "(1) at most two words; (2) no run of five figures or more, and at most six figures in the word",
    "path-iii": "Any other label column (`categorical`, or `long_tail_labels` answered `code`) answered `no` to "
    "the Safe Harbor question",
    "path-iii-every": "The question is put to EVERY label column (`categorical` or `long_tail_labels`, whatever its "
    "levels, answered `code` or not), in the first round, in ONE entry of the questions file",
    "path-iii-hold": "Unanswered, a label column every present cell of which holds a figure -- a ZIP, a ZIP+4, a "
    "postcode, a record, account or device number, a code -- is held as path (i) holds a column (P4-D401's held "
    "block), whatever its levels",
    "acted-on": "it is acted on only once rule U (c) clears",
    "blank": "on path (i) and on a label column with a figure in every present cell, the column held (above)",
    "yes": "no value of this column is published, and the twin writes made-up values in its layouts",
    "no": "never the rows that hold them; where only one value is named, how many rows hold it can be read",
    "code-offer": "offer HX3's `code`, in HX3's words and with its declaration, between `keep` and `identifier`",
    "NP": "a held-back name is published only where its column is NOT ATTACHED to that subject",
    "NP-attached": "A name in an ATTACHED column (an ancestry or a birth city beside each patient's rows) is a value "
    "one to ten subjects hold whatever its rows and is not published",
    "GG": "the twin writes exactly those values -- never a value inside a published empty gap",
    "GG-class": "whose values are NOT every whole number from the least to the greatest each held by at least the "
    "floor's rows",
    "GG-no": "**GG acts only after `no` to the Safe Harbor question**",
    "GG-b": "`few_values` lists every value, the rare ones included, without counts, and the twin writes exactly "
    "those values",
    "GG-unanswered": "**Unanswered**, a column of the class keeps today's description and twin byte for byte",
    "GG-yes": "**`yes`** holds the column's ladder, mode and tail values (P4-D401's held block)",
    "GG-NP": "Beside a subject column, rule NP applies to the rare values as to names.",
    "GG-W1": "Every value the block prints -- in `few_values`, the ladder, the mode or a tail -- that the floored "
    "histogram does not count at f or more is an own-fact group for RULE W1",
    "W1": "contract 4.6b's RULE W1 reads every named level as an OWN-FACT GROUP",
    "W1-pooled": ", and the pooled total printed below f as one too",
    "validate-names": "where every held-back level is named, no cell outside the published and named levels",
    "vectors-4": "`pooled_level_sizes` (`-4`) moves on purpose under B",
    "vectors-27": "the clock cases (`clock_stand_ins_past_route_one`, `-27`) must not move",
    "goldens": "So the profile golden (`tests/test_profile_document.py`, `GOLDEN_SHA256`) and the digests of "
    "`tests/test_twin_golden.py` (`GOLDEN_DESCRIPTION_SHA256`, `GOLDEN_REPORT_SHA256`, `GOLDEN_TWIN_SHA256`) do not move",
    "tests-move": "the 20 lines in 13 test files that count the questions asked (`len(asked)`) and the 18 test files "
    "that declare `--code`",
    "words-limit": "A column of WORDS of a Safe Harbor class -- a city, a name -- whose Safe Harbor question is "
    "unanswered publishes its common levels as today",
    "loinc": "`labs`' `codes loinc` (today under CODES-1's `loinc` line) moves likewise",
    "unowned": "So `diagnoses`' checks `levels icd10_dotted`, `levels icd10_plain`, `codes icd10_dotted` and "
    "`codes icd10_plain` have no owner that can turn them",
    "hx3": "Lane HX3 (P4-D420, READY, not on this base; CODES-2 stacks on it)",
    "i2b2-people": "counted in `patient_num`'s people, 13 levels on 90 cells are held back and three forms publish a "
    "census (adding the procedure codes' prefix and `NDC:00`); either way 0 stand-in cells fall outside the six vocabularies",
    "icd10-111": "`diagnoses.icd10_dotted` 3 forms and 111 `ICD-10-CM with the dot` cells",
    "see-note": "`mixed_results.result_value` 6 (moot once CODES-2 names `SEE NOTE`)",
    "gg-kpi-no": "values off the real list on the few-valued cases, stamped with `no` answered",
    "PS": "this page writes no date or time stand-in and names that rule wherever one is meant",
}


@pytest.mark.parametrize("rule", sorted(OPERATIVE))
def test_each_rule_keeps_its_operative_sentence(rule: str) -> None:
    assert _flat(OPERATIVE[rule]) in _flat(_page()), rule


def _stand_ins(cells: "list[str]", census_of: "dict[str, list[str]]", widen: bool) -> "list[str]":
    """Rule A2's stand-ins, one a held-back level, commonest first.

    widen=True is the page as repaired: (1) each place's list, an empty list taking the characters the
    form's published levels wear there; (2) each list with those characters; (3) the places widened to
    the form's alphabet one at a time from the last. widen=False is the page as first written: the lists,
    an empty list taking the alphabet, then the alphabet at every place.
    """
    tally = collections.Counter(cells)
    published = {value for value, n in tally.items() if n >= FLOOR}
    held = sorted((value for value in tally if value not in published), key=lambda value: (-tally[value], value))

    def alphabet(form: str, place: int) -> "list[str]":
        return list("0123456789") if form[place] == "%" else (
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if form[place] == "@" else [form[place]])

    used = set(published)
    iterators: "dict[tuple[str, str], object]" = {}
    written = []
    for value in held:
        form = _form(value)
        lists = census_of.get(form) or ["" for _ in form]
        worn = ["".join(sorted({level[place] for level in published if _form(level) == form})) for place in range(len(form))]
        if widen:
            first = [list(lists[place] or worn[place]) or alphabet(form, place) for place in range(len(form))]
            second = [sorted(set(first[place]) | set(worn[place])) for place in range(len(form))]
            stages = [("1", first), ("2", second)] + [
                (f"3-{k}", second[:k] + [alphabet(form, place) for place in range(k, len(form))])
                for k in range(len(form) - 1, -1, -1)
            ]
        else:
            stages = [("1", [list(lists[place]) or alphabet(form, place) for place in range(len(form))]),
                      ("a", [alphabet(form, place) for place in range(len(form))])]
        found = ""
        for name, choices in stages:
            walk = iterators.setdefault((form, name), itertools.product(*choices))
            for combination in walk:  # type: ignore[attr-defined]
                if "".join(combination) not in used:
                    found = "".join(combination)
                    break
            if found:
                break
        used |= {found}
        written += [found] * tally[value]
    return written


def test_a2_stages_keep_the_tumour_registrys_grammar_where_the_alphabet_broke_it(tmp_path: pathlib.Path) -> None:
    place = [table.name for table in health_zoo.TABLES].index("tumor_registry")
    source = health_zoo.write_table(health_zoo.TABLES[place], tmp_path, 600, 20261016 + place)
    rows = list(csv.DictReader(io.StringIO(source.read_text(encoding="utf-8-sig"))))
    cells = [row["tnm"] for row in rows if row["tnm"]]
    tally = collections.Counter(cells)
    held = [(value, "") for value in cells if tally[value] < FLOOR]
    assert (len({value for value, _ in held}), len(held)) == (11, 81)
    census = {form: places for form, places in _census(held, FLOOR, in_people=False).items()}
    assert census == {"@%@%@%": ["T", "234", "N", "0123", "M", "1"]}
    grammar = re.compile(r"T[0-4]N[0-3]M[01]")
    real_held = {value for value, _ in held}
    first = _stand_ins(cells, census, widen=False)
    repaired = _stand_ins(cells, census, widen=True)
    assert (sum(not grammar.fullmatch(cell) for cell in first), len(set(first) & real_held)) == (7, 9)
    assert (sum(not grammar.fullmatch(cell) for cell in repaired), len(set(repaired) & real_held)) == (0, 11)
    page = _flat(_page())
    assert "0 of 81 cells outside `T[0-4]N[0-3]M[01]` and 11 of 11 stand-ins real levels" in page
    assert "7 of 81 cells outside and 9 of 11 real" in page


def test_a2_stage_three_keeps_the_vocabulary_marks_of_a_form_under_the_floor() -> None:
    cells = ["DEM|LANG:F"] * 30 + ["DEM|LANG:M"] * 30 + ["DEM|LANG:U"] * 5 + ["DEM|LANG:X"] * 3
    assert _stand_ins(cells, {}, widen=True)[-8:] == ["DEM|LANG:A"] * 5 + ["DEM|LANG:B"] * 3
    assert _stand_ins(cells, {}, widen=False)[-8:] == ["AAA|AAAA:A"] * 5 + ["AAA|AAAA:B"] * 3
    assert "the demographic form `@@@|@@@:@` is written with its published `DEM|` prefix and a drawn last letter" in _flat(_page())


def test_a2_refuses_the_forced_case_where_an_empty_place_bounds_every_character() -> None:
    """95 held-back cells of one figure place, each digit on at most 10: every digit is forced into 5..10."""
    held, alphabet_size, floor = 95, 10, FLOOR
    spread = [10, 10, 10, 10, 10, 10, 10, 10, 10, 5]
    assert sum(spread) == held and max(spread) <= floor - 1
    least = held - (alphabet_size - 1) * (floor - 1)
    assert least == 5 and least >= 1
    for spread_case in ([10] * 9 + [5], [5] + [10] * 9):
        for count in spread_case:
            assert least <= count <= floor - 1
    assert held > (alphabet_size - 1) * (floor - 1)
    assert 90 == (alphabet_size - 1) * (floor - 1)  # at H = 90 one digit may hold none: no bound inside 1..f-1
    assert "`K-S6-08` gains H = 95 on figures, a = 10: every digit forced into 5..10" in _flat(_page())


def _held_while_unanswered(cells: "list[str]") -> bool:
    """Path (iii)'s hold: a label column every present cell of which holds a figure."""
    present = [cell for cell in cells if cell.strip()]
    return bool(present) and all(any(mark.isdigit() for mark in cell) for cell in present)


def test_path_iii_holds_figure_columns_and_leaves_words_as_the_stated_limit() -> None:
    assert _held_while_unanswered(["02139", "02139-1234", "10027"])
    assert _held_while_unanswered(["K1A 0B1", "M5V 2T6"])  # letters too: the figures-and-marks reading misses it
    assert _held_while_unanswered(["E11.9", "I10", "T2N0M1"])
    assert not _held_while_unanswered(["Boston", "São Paulo", "Hà Nội"])
    assert not _held_while_unanswered(["DEM|LANG:F", "ICD10CM:E11.9"])
    page = _flat(_page())
    assert "measured, the zoo's `patients.birth_city`, 7 cities on 600 of 600 rows" in page
    assert "holding only columns of figures and marks alone leaves the postcode column's 5 of 40 printed" in page


def test_a_zip_column_half_written_zip_plus_four_is_asked_nothing_on_this_base(tmp_path: pathlib.Path) -> None:
    """The first review's case: today no question reaches it and real five-figure ZIPs print with their counts."""
    draw = random.Random(11)
    zips = [f"0{2100 + 7 * k:04d}" for k in range(70)]
    weights = [1.0 / (k + 1) ** 1.1 for k in range(70)]
    lines = ["pid,zip"]
    for k in range(600):
        code = draw.choices(zips, weights)[0]
        lines += [f"P{k:06d},{code}-{draw.randint(1000, 9999)}" if k % 2 else f"P{k:06d},{code}"]
    document = _profiled(tmp_path, "zipmix.csv", "\n".join(lines) + "\n")
    zip_column = _column(document, "zip")
    assert zip_column["role"] in ("categorical", "long_tail_labels")
    printed = [level["label"] for level in zip_column.get("levels") or []]
    assert printed and all(re.fullmatch(r"\d{5}", label) for label in printed)
    asked = json.loads((tmp_path / "zipmix-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "zip"]
    assert _held_while_unanswered([line.split(",")[1] for line in lines[1:]])
    assert "0 of 363 and 0 of 40 real values printed" in _flat(_page())


def _consecutive_and_floored(values: "list[str]") -> bool:
    """Outside GG's class: every whole number from the least to the greatest, each on the floor's rows."""
    tally = collections.Counter(values)
    numbers = sorted({float(value) for value in tally})
    if any(number != int(number) for number in numbers):
        return False
    whole = [int(number) for number in numbers]
    return whole == list(range(whole[0], whole[-1] + 1)) and min(tally.values()) >= FLOOR


@pytest.mark.parametrize("fixture", ["every_role_table", "every_role_and_joined_table"])
def test_the_golden_fixtures_few_valued_numbers_stand_outside_ggs_class(fixture: str, tmp_path: pathlib.Path) -> None:
    text = getattr(fixtures, fixture)()
    document = _profiled(tmp_path, f"{fixture}.csv", text)
    rows = list(csv.DictReader(io.StringIO(text)))
    ceiling = taxonomy.categories_ceiling(len(rows), taxonomy.Settings())
    few = [
        column["name"] for column in document["columns"]
        if column["role"] in ("count", "continuous") and (column.get("n_distinct") or 0) <= ceiling
    ]
    assert few == ["visits"]
    visits = [row["visits"] for row in rows if row["visits"]]
    assert sorted({int(value) for value in visits}) == list(range(10))
    assert _consecutive_and_floored(visits)
    assert "`visits` (a `count` column of the ten values 0 to 9, each on 15 to 28 rows) is outside GG's class" in _flat(_page())
    assert min(collections.Counter(visits).values()) >= 15 and max(collections.Counter(visits).values()) <= 28


def test_days_supply_is_inside_ggs_class() -> None:
    days_supply = {"5": 5, "7": 25, "10": 6, "14": 14, "21": 8, "28": 11, "30": 349, "84": 8, "90": 174}
    cells = [value for value, n in days_supply.items() for _ in range(n)]
    assert not _consecutive_and_floored(cells)
    assert _consecutive_and_floored([str(k % 4) for k in range(600)])


def test_the_kinds_table_holds_the_twelve_kinds_once_each() -> None:
    page = _page()
    table = page[page.index("**The kinds each lane turns, at 600 rows**"):page.index("### ZS.9")]
    named = re.findall(r"^\| ([^|]+) \|", table, flags=re.MULTILINE)
    kinds = [kind.strip("` ") for cell in named for kind in cell.split(",") if kind.strip("` ") not in ("kind", "---")]
    assert sorted(kinds) == sorted(TWELVE)
    assert "Best case 22 of 40 kinds; 18 without rule NP." in _flat(page)


def test_pcornet_dx_held_back_cells_are_the_label_level_and_seven_number_levels() -> None:
    number_levels = {"272.4": 4, "585.3": 3, "486": 8, "311": 4, "38341003": 5, "233604007": 4, "431855005": 1}
    assert (len(number_levels), sum(number_levels.values())) == (7, 29)
    assert 10 + sum(number_levels.values()) == 39
    assert len({_form(value) for value in number_levels} | {_form("R07.9")}) == 5
    assert "holds back 39 cells in five shapes" in _flat(_page())


def test_the_safe_harbor_question_is_the_owners_sentence() -> None:
    owners = (
        "Could a value of this column name a person, a place smaller than a state, a birth date, "
        "or a record, account or device number?"
    )
    page = _flat(_page())
    assert owners in page
    assert "> Could a value of '<column>' name a person, a place smaller than a state, a birth date, or a record, account or device number?" in _page()
    assert "45 CFR 164.514(b)(2)(i)" in page


SAFE_HARBOR_CLASSES = (
    "a person is a patient or a patient's relative, employer or household member, by name, initials or any mark",
    "a place smaller than a state is a street address, city, county, precinct, or a ZIP code, or its first three "
    "figures where that area holds 20,000 people or fewer",
    "a birth date includes any date of a person other than its year, and an age over 89 years, or any date that "
    "shows one",
    "the numbers include medical record, health-plan, account, certificate or licence, vehicle, device and serial "
    "numbers, telephone, fax and social security numbers, e-mail, web and internet addresses, and any other number "
    "or code given to one person",
)


@pytest.mark.parametrize("covered", SAFE_HARBOR_CLASSES)
def test_the_safe_harbor_explanation_names_each_class_the_page_relies_on(covered: str) -> None:
    """The question's `what_synthtwin_saw` covers 45 CFR 164.514(b)(2)(i)'s (B), (C) and (R) as GG and path (iii) read them."""
    assert _flat(covered) in _flat(_page())


def test_the_page_cites_no_method_section_this_base_lacks() -> None:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index(PAGE_HEADING)
    assert "G7.13" not in text[start:]
    assert "(the G1 floor, contract NF128 and NF129, plan P4-D417)" in _flat(text[start:])


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


SCREEN = {
    "(1) at most two words": lambda word: len(word.split()) > 2,
    "(2) no run of five figures or more, and at most six figures in the word": lambda word: bool(
        re.search(r"\d{5}", word)) or sum(mark.isdigit() for mark in word) > 6,
    "(3) no `@`, no `://`, no `www.`": lambda word: "@" in word or "://" in word or "www." in word,
    "(4) no date shape": lambda word: bool(re.search(r"\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}", word)),
    "and no clock shape (a two-figure hour 00 to 23, a colon and minutes 00 to 59, with or without seconds or a "
    "marker; a titer, `1:` and figures, is not one)": lambda word: bool(re.search(r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d", word)),
    "(5) no dotted quad": lambda word: bool(re.search(r"\d{1,3}(?:\.\d{1,3}){3}", word)),
    "(6) no letter in a word that holds three figures or more": lambda word: any(
        any(mark.isalpha() for mark in part) and sum(mark.isdigit() for mark in part) >= 3 for part in [word]),
    "(7) no single letter followed by a point": lambda word: bool(re.search(r"(?<![A-Za-z])[A-Za-z]\.", word)),
}
"""Path (ii)'s shape screen, one refusal a clause of the page's own list, the clause as the page writes it."""


def _passes_screen(word: str, without: str = "") -> bool:
    """Path (ii)'s shape screen as the page writes it; `without` leaves one clause out."""
    return not any(refuses(word) for clause, refuses in SCREEN.items() if clause != without)


REFUSED = (
    "Called to J. Smith RN at 14:32", "555-1234", "123-45-6789", "02139-1234", "02139",
    "a.b@c.org", "2024-01-05", "01/05/2024", "10.0.0.12", "http://x.org", "www.example",
    "14:32", "REC 0012345", "(319) 555-0100", "REC 4521", "E1234", "K1A 0B1", "J.S.", "J. Smith",
)
PASSED = ("TNP", "HI", "LO", "1:40", "1:1280", "N/A", ".", "Not done", ">60", "<0.5", "QNS")


@pytest.mark.parametrize("word", REFUSED)
def test_the_shape_screen_refuses_each_shaped_class(word: str) -> None:
    assert not _passes_screen(word)


@pytest.mark.parametrize("word", PASSED)
def test_the_shape_screen_lets_the_result_words_through(word: str) -> None:
    assert _passes_screen(word)


def test_every_clause_of_the_screen_stands_on_the_page() -> None:
    page = _flat(_page())
    for clause in SCREEN:
        assert _flat(clause) in page, clause


# Each clause of the screen, a word only that clause refuses: the page's list is the screen. Clause (5)
# is the one no word reaches alone: a dotted quad of six figures or fewer always holds a date shape.
ONLY_THIS_CLAUSE = {
    "(1) at most two words": "seen by nurse",
    "(2) no run of five figures or more, and at most six figures in the word": "02139",
    "(3) no `@`, no `://`, no `www.`": "a@b",
    "(4) no date shape": "1/2/24",
    "and no clock shape (a two-figure hour 00 to 23, a colon and minutes 00 to 59, with or without seconds or a "
    "marker; a titer, `1:` and figures, is not one)": "14:32",
    "(6) no letter in a word that holds three figures or more": "REC 4521",
    "(7) no single letter followed by a point": "J.S.",
}


@pytest.mark.parametrize("clause", sorted(ONLY_THIS_CLAUSE))
def test_each_clause_of_the_screen_is_the_pages_and_refuses_its_own_class(clause: str) -> None:
    word = ONLY_THIS_CLAUSE[clause]
    assert _flat(clause) in _flat(_page()), clause
    assert not _passes_screen(word)
    assert _passes_screen(word, without=clause), (clause, word)


def test_the_screens_residual_is_the_one_the_page_names() -> None:
    assert _passes_screen("Smith") and _passes_screen("John Smith") and _passes_screen("JS")
    assert not _passes_screen("pH 7.35") and not _passes_screen("10E3/uL")
    page = _flat(_page())
    assert ("A lone one- or two-word name typed into a measurement column (`Smith`, `John Smith`, initials without "
            "points such as `JS`) cannot be told from a result word by its shape") in page
    assert "a result word such as `pH 7.35` or `10E3/uL` is refused too" in page


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
    lines = ["gender,unit,value"]
    for k in range(600):
        gender = "X" if k < 4 else ("F" if draw.random() < 0.5 else "M")
        unit = "U" if k == 10 else ("A" if draw.random() < 0.5 else "B")
        lines += [f"{gender},{unit},{draw.gauss(50, 10):.1f}"]
    document = _profiled(tmp_path, "lone.csv", "\n".join(lines) + "\n")
    gender = _column(document, "gender")
    unit = _column(document, "unit")
    assert (gender["suppressed_levels"], gender["suppressed_rows"]) == (1, 4)
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
