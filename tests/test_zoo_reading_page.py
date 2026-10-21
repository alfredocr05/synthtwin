"""The zoo-fix reading page holds what it computes (plan P4-D419).

WHY A FILE OF ITS OWN. The zoo-fix reading page in
`docs/plans/phase-4-columns.md` is written before the code of lanes
UN-1a, UN-1b, TR, LISTS, UN-2 and NOTES, and of CODES-3's question:
nothing in the product reads it yet. The disposition seal turns red on
any edit of a sealed passage and is re-sealed by whoever makes the edit,
so it cannot tell a correction from its undoing. This file can, for the
figures the page computes and for its reading of the product it
describes.

WHAT IS COMPUTED HERE, NOT READ. The share line as the geometric middle
of the zoo plan's two nearest points, and every re-measured share on its
side of the line; the clock grid's bound and the categories ceiling it
rests on; the missing-code question's trigger over the cases the page
measured; the list reading and the closed list of templates on the
guard cases each lane's gate holds; what the two golden fixtures hold;
and the holding questions of plan P4-D401 and the role lists the page's
rule I reads, from `synthtwin.asking` itself.

WHAT IS NOT HERE. No lane's code exists, so nothing here says a twin
meets anything. The functions below are the page's rules written once
as the test reads them, not the product's: each lane builds its own and
its gate holds the cases.
"""
import csv
import io
import math
import pathlib
import random
import re

from synthtwin import asking
from synthtwin import parsing
from synthtwin import taxonomy

import fixtures

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
PAGE_HEADING = "## The zoo-fix reading page"
DECISION_HEADING = "## Decision P4-D419"


def _page() -> str:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index(PAGE_HEADING)
    stop = text.index(DECISION_HEADING, start)
    return text[start:stop]


def _flat(text: str) -> str:
    return " ".join(text.split())


def test_the_page_stands_once_and_its_decision_follows_it() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert text.count("\n" + PAGE_HEADING) == 1
    assert text.count("\n" + DECISION_HEADING + " ") == 1
    assert text.index(PAGE_HEADING) < text.index(DECISION_HEADING)
    for section in ("ZR.0", "ZR.1", "ZR.2", "ZR.3", "ZR.4", "ZR.5", "ZR.6", "ZR.7", "ZR.8", "ZR.9"):
        assert f"\n### {section} " in _page(), section


ORDER = (
    "0:", "0b:", "0c:", "0d:", "2:", "3, 4:", "5:", "5c:", "6:", "8 asked before 7",
    "7:", "7b:", "8:", "9:", "9t:", "9l:", "9b:", "9c:", "10:",
)


def test_the_order_table_lists_every_rule_in_the_order_the_page_states() -> None:
    page = _page()
    table = page[page.index("| place | rule |"):]
    table = table[: table.index("\n\n")]
    rules = []
    for line in table.split("\n")[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rules += [cells[1]]
    assert len(rules) == len(ORDER)
    for rule, opening in zip(rules, ORDER):
        assert rule.startswith(opening), (rule, opening)


def test_the_share_line_is_the_middle_of_the_plans_nearest_points() -> None:
    """A quarter: the geometric middle of 13.8 % (notes) and 44.7 % (an ICD tail)."""
    middle = math.sqrt(0.138 * 0.447)
    assert abs(middle - 0.25) < 0.003
    page = _flat(_page())
    assert "`4 x covered >= present`" in page
    assert "a quarter of its present rows" in page
    # Every re-measured share the page states, on its side of the line.
    below = {"13.3": 0.133, "16.3 %": 0.163, "21.2 %": 0.212, "24.1 %": 0.241, "9.6 %": 0.096}
    above = {"36.5 %": 0.365, "42.5": 0.425, "46.2 %": 0.462, "72.2 %": 0.722}
    for said, share in below.items():
        assert said in page and 4 * share < 1, said
    for said, share in above.items():
        assert said in page and 4 * share >= 1, said


def test_the_clock_grid_bounds_a_key_read_as_clock_times() -> None:
    """Rule 5c's guard: at least 11 values on the grid, on the smallest table described."""
    assert 24 * 60 / 10_000 == 0.144
    assert 24 * 3600 / 1_000_000 == 0.0864
    smallest = taxonomy.categories_ceiling(100, taxonomy.Settings())
    assert smallest == 10
    assert 0.144 ** (smallest + 1) < 1e-9
    grid = re.compile(r"(?:[01]\d|2[0-3])[0-5]\d")
    off = [f"{k:04d}" for k in range(1, 601) if not grid.fullmatch(f"{k:04d}")]
    assert off[0] == "0060"
    page = _flat(_page())
    assert "0.144^11" in page and "`0060`" in page and "0.0864^11" in page


def _placeholder_shape(cell: str) -> bool:
    """Q-MISSING's shape: a minus sign and one to three figures, or nines alone of two or more."""
    if re.fullmatch(r"-\d{1,3}", cell):
        return True
    return re.fullmatch(r"9{2,}", cell) is not None


def _asked_missing(cells: "list[str]") -> "list[str]":
    """The values Q-MISSING asks about: the shape, outside the built-in sentinels, far and frequent."""
    settings = taxonomy.Settings()
    numbers = [float(cell) for cell in cells]
    asked = []
    for spelling in sorted(set(cells)):
        value = float(spelling)
        if not _placeholder_shape(spelling) or value in parsing.NUMERIC_SENTINELS:
            continue
        others = sorted(number for number in numbers if number != value)
        lower = taxonomy._quantile(others, 25, 100)
        upper = taxonomy._quantile(others, 75, 100)
        reach = settings.sentinel_outlier_iqr_multiple * (upper - lower)
        held = cells.count(spelling)
        far = value < lower - reach or value > upper + reach
        if far and held >= taxonomy._needed(settings.sentinel_minimum_share, len(cells)):
            asked += [spelling]
    return asked


def test_the_missing_code_question_asks_the_codes_and_nothing_else() -> None:
    draw = random.Random(20261021)
    survey = ["-99" if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    ages = ["999" if draw.random() < 0.03 else str(draw.randint(18, 90)) for _ in range(600)]
    inside = [draw.choice(("7", "9")) if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    minus_one = ["-1" if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    codes = [draw.choice(("195967001", "709044004")) if draw.random() < 0.08 else str(draw.randint(10_000, 99_999)) for _ in range(600)]
    flags = [draw.choice(("0", "1")) if draw.random() < 0.25 else str(draw.randint(20, 40)) for _ in range(600)]
    assert _asked_missing(survey) == ["-99"]
    assert _asked_missing(ages) == ["999"]
    assert _asked_missing(inside) == []
    assert _asked_missing(minus_one) == []
    assert _asked_missing(codes) == []
    assert _asked_missing(flags) == []
    page = _flat(_page())
    assert "a minus sign and one to three figures, or as nines alone of two figures or more" in page
    assert "the shape condition removes all five" in page


LIST_MARKS = (";", "|", "^", "~", ", ", ",")


def _a_list(cells: "list[str]") -> "str | None":
    """Rule 9l's conditions 1 to 4 and its inference, as the page writes them; the mark or None."""
    ceiling = taxonomy.categories_ceiling(len(cells), taxonomy.Settings())
    for mark in LIST_MARKS:
        if mark == "," and any(", " in cell for cell in cells):
            continue
        parts = [[part.strip() for part in cell.split(mark)] for cell in cells]
        several = [split for split in parts if len(split) >= 2]
        if len(several) < parsing.census_floor(11):
            continue
        if len({len(split) for split in parts}) < 2:
            continue
        values = {parsing.folded(part) for split in parts for part in split}
        if "" in values or len(values) > ceiling or len(values) >= len(set(cells)):
            continue
        widest = max(len(split) for split in parts)
        if mark == "," and widest < 3:
            continue
        if mark == ", " and widest < 3:
            continue
        return mark
    return None


TEMPLATES = (
    (re.compile(r"(\d+)'(\d+)\""), (None, 12)),
    (re.compile(r"(\d+)w ?(\d+)d"), (None, 7)),
    (re.compile(r"(\d+)\+(\d+)"), (None, 7)),
    (re.compile(r"PT(\d+)H(\d+)M"), (None, 60)),
    (re.compile(r"(\d+) days (\d\d):(\d\d):(\d\d)"), (None, 24, 60, 60)),
    (re.compile(r"(\d+):(\d\d)"), (None, 60)),
    (re.compile(r"(\d+)/(\d+) [A-Za-z][A-Za-z/%]*"), (None, None)),
)


def _a_template(cells: "list[str]") -> bool:
    """Rule 9t: one closed-list template in every cell, every base held; `#:##` only past 23 hours."""
    for pattern, bases in TEMPLATES:
        matched = [pattern.fullmatch(cell) for cell in cells]
        if not all(matched):
            continue
        held = all(
            base is None or int(hole) < base
            for found in matched if found is not None
            for hole, base in zip(found.groups(), bases)
        )
        if not held:
            continue
        if pattern.pattern == r"(\d+):(\d\d)":
            return any(found is not None and int(found.group(1)) > 23 for found in matched)
        return True
    return False


def test_lists_and_templates_are_disjoint_on_each_gates_guard_case() -> None:
    draw = random.Random(20261021)
    pressures = [f"{draw.randint(90, 180)}/{draw.randint(50, 110)} mmHg" for _ in range(600)]
    plain = [f"{draw.randint(90, 180)}/{draw.randint(50, 110)}" for _ in range(600)]
    picks = [",".join(str(k) for k in sorted(draw.sample(range(1, 10), draw.randint(1, 3)))) for _ in range(600)]
    problems = [";".join(draw.sample(("E11.9", "I10", "N18.3", "E78.5", "J44.9", "F32.9"), draw.randint(1, 3))) for _ in range(600)]
    complaints = [draw.choice(("chest pain, shortness of breath", "fall, hip pain", "nausea, vomiting, diarrhea", "headache", "fever, cough")) for _ in range(600)]
    weights = [f"{draw.randint(50, 110)},{draw.randint(0, 9)} kg" for _ in range(600)]
    statures = [f"{inches // 12}'{inches % 12}\"" for inches in (draw.randint(58, 78) for _ in range(600))]
    durations = [f"{minutes // 60}:{minutes % 60:02d}" for minutes in (draw.randint(5, 4300) for _ in range(600))]
    clocks = [f"{minutes // 60}:{minutes % 60:02d}" for minutes in (draw.randint(0, 1439) for _ in range(600))]
    assert _a_template(pressures) and _a_list(pressures) is None
    assert not _a_template(plain) and _a_list(plain) is None
    assert _a_list(picks) == "," and not _a_template(picks)
    assert _a_list(problems) == ";" and not _a_template(problems)
    assert _a_list(complaints) is None
    assert _a_list(weights) is None and not _a_template(weights)
    assert _a_template(statures) and not _a_template(statures + ["5'13\""])
    assert _a_template(durations) and not _a_template(clocks)


def _far_or_listed(cells: "list[str]") -> bool:
    numbers = []
    for cell in cells:
        try:
            numbers += [float(cell)]
        except ValueError:
            numbers = []
            break
    return bool(numbers and _asked_missing(cells))


def test_the_golden_fixtures_hold_none_of_the_shapes_the_new_readings_take() -> None:
    """ZR.6: so no question of the page fits a fixture column, and the fixtures' questions files stay."""
    grid = re.compile(r"(?:[01]\d|2[0-3])[0-5]\d(?:[0-5]\d(?:\.\d+)?)?")
    for text in (fixtures.every_role_table(), fixtures.every_role_and_joined_table()):
        rows = list(csv.reader(io.StringIO(text)))
        header, body = rows[0], rows[1:]
        for index, name in enumerate(header):
            cells = [row[index] for row in body if row[index].strip()]
            if not cells:
                continue
            assert not all(re.fullmatch(r"\d{4}|\d{6}(?:\.\d+)?", cell) and grid.fullmatch(cell) for cell in cells), name
            assert _a_list(cells) is None, name
            assert not any(re.fullmatch(r"-?\d+,\d+", cell) for cell in cells), name
            assert not _far_or_listed(cells), name


def test_rule_i_reads_the_holding_questions_the_product_has() -> None:
    """The page's rule I rests on these lists; a change to any of them sends a lane back to the page."""
    assert asking.HOLDING_REASONS == (
        asking.BECAUSE_REPEATS_AND_MANY,
        asking.BECAUSE_JOINED,
        asking.BECAUSE_PADDED,
        asking.BECAUSE_FIXED_WIDTH,
        asking.BECAUSE_GROUPED_FIXED_WIDTH,
    )
    assert asking._READ_AS_DATES_OR_TIMES == (taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK)
    # A unit column read as an affixed number is still put the person
    # question; a column read as joined numbers is not, which is why
    # rule I asks it all the same for a template.
    assert taxonomy.ROLE_AFFIXED not in asking._PERSON_ROLES_EXCLUDED
    assert taxonomy.ROLE_JOINED in asking._PERSON_ROLES_EXCLUDED
    page = _flat(_page())
    assert "No reading on this page drops a question that holds a column under P4-D401" in page


def test_contract_c6_1_lists_fourteen_of_its_fifteen_roles() -> None:
    """ZR.8 point 3: rule 7b's role is missing from C6-1's list; UN-1a restates it and changes this check."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("**C6-1.**")
    listed = text[start: text.index("Fourteen roles in thirteen rules", start)]
    assert "`numbers_with_labels`" not in listed
    assert "`joined_numbers`" in listed and "`free_text`" in listed
