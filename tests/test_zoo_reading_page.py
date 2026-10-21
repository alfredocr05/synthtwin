"""The zoo-fix reading page holds what it computes (plan P4-D419).

WHY A FILE OF ITS OWN. The zoo-fix reading page in
`docs/plans/phase-4-columns.md` is written before the code of lanes
UN-1a, UN-1b, TR, LISTS, UN-2 and NOTES, and of CODES-3's question:
nothing in the product reads it yet. The disposition seal turns red on
any edit of a sealed passage and is re-sealed by whoever makes the edit,
so it cannot tell a correction from its undoing. This file can, for the
figures the page computes, for its reading of the product it describes,
and for the one sentence of each rule that carries the rule.

WHAT IS COMPUTED HERE, NOT READ. The share line as the geometric middle
of the zoo plan's two nearest points, and every re-measured share on its
side of the line, notes and label tails overlapping; the clock grid's
bound, and the identity question today's reader already puts to every
compact clock and every padded key the grid cannot tell from one; the
missing-code question's trigger over the cases the page measured; the
UID question's trigger over the golden fixtures; the list reading and
the closed list of templates on the guard cases each lane's gate holds;
what the two golden fixtures hold, the golden `note` out of NOTES'
reach among them; which of the eight questions hold; the classifier
docstring's own list of rules; and the holding questions of plan P4-D401
and the role lists the page's rule I reads, from `synthtwin.asking`
itself.

WHAT IS NOT HERE. No lane's code exists, so nothing here says a twin
meets anything. The functions below are the page's rules written once
as the test reads them, not the product's: each lane builds its own and
its gate holds the cases.
"""
import collections
import csv
import inspect
import io
import math
import pathlib
import random
import re

import pytest

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


# THE ONE SENTENCE OF EACH RULE THAT CARRIES IT. A rule's figures are
# computed below where they can be; what no figure computes -- that a
# reading is taken only on an answer, that a floor binds, that a list is
# closed -- is its sentence, and a page that loses or bends one of these
# sentences has changed the rule. Each is pinned verbatim, once.
OPERATIVE = {
    "rule 0c yields to rule 7": "yields to rule 7 where every whole-cell level clears the floor",
    "rule 5c is taken only on an answer": (
        "taken ONLY on the answer `clock-figures` or the declaration `--clock-figures`, never inferred"
    ),
    "rule 5c keeps the hold": (
        "so Q-CLOCK is THAT question with `clock-figures` added and its hold stands until it is answered"
    ),
    "rule A keeps the hold": "rule A reads it only on that question's answer `dates`",
    "rule I reads the exemption narrowly": (
        "P4-D401's own exemption for a column read as dates or times covers only the columns"
        " today's reader already reads as dates or times"
    ),
    "rule 7 (i) stands aside only below the floor": (
        "a SUFFIX wrapper (an empty prefix, or a symbol prefix such as `<`) reads the column and"
        " a level is below the floor (`taxonomy._a_level_is_below_the_floor`)"
    ),
    "rule P's list veto": (
        "with the LIST VETO: any present cell holding two or more of one separator (`,` `;` `|`)"
        " means the column is not read as decimals"
    ),
    "rule 9t's list is closed": "A template not on the list is reached only by declaration (rule 0c)",
    "rule 9l's condition 3": (
        "(3) the different values, trimmed and folded, are at most the categories ceiling AND"
        " fewer than the column's different cells (combinations outnumber values)"
    ),
    "rule 9b's line judges only what NOTES reaches": "The line judges only a column NOTES' trigger reaches",
    "rule 9b's line lifted by the answer": (
        "The answer \"no\" (the column holds labels, not notes) lifts the line as the declaration"
        " `--code` does"
    ),
    "the ICD points justify the code condition": "THE ICD POINTS JUSTIFY THE CODE CONDITION, NOT THE QUARTER",
    "the size-free alternative is struck": "is REFUTED and struck",
    "LV1 binds every count to the floor": (
        "LV1, each count above is 0 or at least the floor, `suppressed_value_cells` excepted (ruling 2)"
    ),
    "Q-ID reaches only free text": "only a column today's reader leaves `free_text` (no rule from 2 to 9c claims it)",
    "Q-UNIT asks about the data": (
        "every value is a number written beside the same word or mark, as the made-up `72 kg` is;"
        " is it an amount in that unit, a code, or labels to keep as written?"
    ),
    "military clocks counted in cells": "265 of whose 600 cells carry a leading zero",
    "the kinds the lanes can turn": "these lanes raise `K-HZ-01` from 14 to at most 18 of 40 by themselves",
    "an exact list counts as read": (
        "a column whose every level clears the floor counts as read wherever rule 7 keeps its exact list"
    ),
    "every KPI column is marked": "**zoo** (a column of `tests/health_zoo.py` at 98c0fce6), **E0c**",
    "UN-2's stale OWNERS line": "UN-2's line on `us_unit_vitals` is STALE",
    "the two lists UN-1a restates": "These are the two lists the first lane that edits the order (UN-1a) restates whole",
}


@pytest.mark.parametrize("rule", sorted(OPERATIVE))
def test_each_rule_keeps_its_operative_sentence(rule: str) -> None:
    assert _flat(_page()).count(OPERATIVE[rule]) == 1, rule


def _questions() -> "dict[str, list[str]]":
    """ZR.2's table of questions, a row a question, its cells in order."""
    page = _page()
    table = page[page.index("| id | lane |"):]
    table = table[: table.index("\n\n")]
    rows: "dict[str, list[str]]" = {}
    for line in table.split("\n")[2:]:
        cells = [cell.strip() for cell in line.replace("\\|", "\x00").strip("|").split("|")]
        rows[cells[0]] = [cell.replace("\x00", "|") for cell in cells]
    return rows


def test_the_questions_that_hold_are_the_identity_ones() -> None:
    """Q-ID and Q-CLOCK on whole figures hold (rule I); the other six hold nothing."""
    rows = _questions()
    assert sorted(rows) == sorted((
        "Q-ID", "Q-COMMA-3", "Q-COMMA-DD", "Q-COMMA-PICKS", "Q-UNIT", "Q-MISSING", "Q-LIST", "Q-CLOCK",
    ))
    holds = {question: cells[4] for question, cells in rows.items()}
    assert holds["Q-ID"].startswith("yes (P4-D401, one more holding shape")
    assert holds["Q-CLOCK"].startswith("yes on whole figures: today's reader always puts the padded question")
    assert "its hold stands until answered" in holds["Q-CLOCK"]
    for question in ("Q-COMMA-3", "Q-COMMA-DD", "Q-COMMA-PICKS", "Q-UNIT", "Q-MISSING", "Q-LIST"):
        assert holds[question].startswith("no"), question


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
    # The spaced label tails the skeptics measured under the line, and
    # notes' span: they overlap, so no share tells the two apart and the
    # line waits on the answer.
    labels = {
        "14.0 and 15.0 % at 100 rows": (0.140, 0.150),
        "7.5 to 20.5 % at 200": (0.075, 0.205),
        "22.5 % at 600": (0.225,),
        "(14.0 to 22.2 %": (0.140, 0.222),
    }
    for said, shares in labels.items():
        assert said in page and all(4 * share < 1 for share in shares), said
    notes = (0.133, 0.241)
    lowest = min(share for shares in labels.values() for share in shares)
    highest = max(share for shares in labels.values() for share in shares)
    assert "notes' 13.3 to 24.1 %" in page
    assert lowest < notes[1] and highest > notes[0]
    # The size-free alternative the build named: spaced label tails hold
    # more different values than half their cells, so it moves them too.
    assert "0.51 to 0.71 different values a present cell" in page and 0.51 > 0.5


def _on_the_grid(cell: str) -> bool:
    """Rule 5c's conditions 1 and 2 on one cell."""
    found = re.fullmatch(r"(\d\d)(\d\d)(?:(\d\d)(?:\.\d+)?)?", cell)
    if found is None:
        return False
    hours, minutes, seconds = found.groups()
    return int(hours) < 24 and int(minutes) < 60 and (seconds is None or int(seconds) < 60)


KEYS_ON_THE_GRID = {
    "300 rows of 0001 to 0040": range(1, 41),
    "500 rows of 0001 to 0059": range(1, 60),
    "500 rows of 0100 to 0159": range(100, 160),
    "100 rows of 0001 to 0020": range(1, 21),
    "300 rows of 0101 to 0140": range(101, 141),
    "6 sites by 40 patients": [site * 100 + patient for site in range(1, 7) for patient in range(1, 41)],
    "4 sites by 30 patients": [site * 100 + patient for site in range(1, 5) for patient in range(1, 31)],
}


def test_q_clock_is_the_identity_question_the_reader_already_puts() -> None:
    """Rule 5c never lifts a hold: every key the grid cannot tell from a clock is held today.

    Keys numbered in order stay on the clock's grid, so the grid is no
    guard; what guards them is the padded question, which every whole
    compact clock and every such key is already put. With a fraction no
    identity question is put, and nothing is held today.
    """
    for name, keys in KEYS_ON_THE_GRID.items():
        cells = [f"{key:04d}" for key in keys]
        assert all(_on_the_grid(cell) for cell in cells), name
        assert asking.why_worth_asking(cells) == asking.BECAUSE_PADDED, name
    draw = random.Random(20261021)
    no_zero = [f"{draw.randint(10, 19)}{draw.randrange(60):02d}" for _ in range(600)]
    quarter = [f"{draw.randrange(24):02d}{draw.choice((0, 15, 30, 45)):02d}" for _ in range(600)]
    fraction = [
        f"{draw.randint(7, 19):02d}{draw.randrange(60):02d}{draw.randrange(60):02d}.{draw.randrange(10 ** 6):06d}"
        for _ in range(600)
    ]
    for cells in (no_zero, quarter, fraction):
        assert all(_on_the_grid(cell) for cell in cells)
    assert asking.why_worth_asking(no_zero) == asking.BECAUSE_FIXED_WIDTH
    assert asking.why_worth_asking(quarter) == asking.BECAUSE_PADDED
    assert asking.why_worth_asking(fraction) is None
    assert asking.BECAUSE_PADDED in asking.HOLDING_REASONS
    assert asking.BECAUSE_FIXED_WIDTH in asking.HOLDING_REASONS
    # The grid's bound, now a fidelity figure: four-figure codes declared
    # clock times by mistake read only if every value is on the grid.
    assert 24 * 60 / 10_000 == 0.144
    assert 24 * 3600 / 1_000_000 == 0.0864
    assert 0.144 ** 11 < 1e-9
    page = _flat(_page())
    assert "0.144^11" in page and "0.0864^11" in page
    assert "stays on the grid to `0059`, one from `0100` to `0159`" in page
    assert "TR's gate and `K-S3-64` gain the seven key shapes above" in page and len(KEYS_ON_THE_GRID) == 7


def _placeholder_shape(cell: str) -> bool:
    """Q-MISSING's shape: a minus sign and one to three figures, or one figure 7, 8 or 9 repeated."""
    if re.fullmatch(r"-\d{1,3}", cell):
        return True
    return re.fullmatch(r"7{2,}|8{2,}|9{2,}", cell) is not None


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
    refused = ["77" if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    not_known = ["888" if draw.random() < 0.03 else str(draw.randint(18, 90)) for _ in range(600)]
    inside = [draw.choice(("7", "9")) if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    minus_one = ["-1" if draw.random() < 0.07 else str(draw.randint(1, 5)) for _ in range(600)]
    codes = [draw.choice(("195967001", "709044004")) if draw.random() < 0.08 else str(draw.randint(10_000, 99_999)) for _ in range(600)]
    flags = [draw.choice(("0", "1")) if draw.random() < 0.25 else str(draw.randint(20, 40)) for _ in range(600)]
    weights = [str(draw.randint(50, 110)) for _ in range(600)]
    assert _asked_missing(survey) == ["-99"]
    assert _asked_missing(ages) == ["999"]
    assert _asked_missing(refused) == ["77"]
    assert _asked_missing(not_known) == ["888"]
    assert _asked_missing(inside) == []
    assert _asked_missing(minus_one) == []
    assert _asked_missing(codes) == []
    assert _asked_missing(flags) == []
    # `77`, `88` and `99` written as real weights stand inside the fence.
    assert {"77", "88", "99"} <= set(weights) and _asked_missing(weights) == []
    # The fence's other alarms on the zoo at 600 and 20,000 rows: the
    # widened shape reaches none of them.
    for alarm in ("195967001", "235595009", "427089005", "709044004", "860975", "866924", "1049621", "0", "1", "2", "6"):
        assert not _placeholder_shape(alarm), alarm
    page = _flat(_page())
    assert (
        "a minus sign and one to three figures, or as one figure repeated, two figures or more,"
        " all 7, all 8 or all 9" in page
    )
    assert "the shape condition removes all five" in page
    assert "none such a run" in page


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


def test_lists_and_templates_are_disjoint_on_each_lanes_guard_case() -> None:
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


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    return {name: [row[index] for row in body] for index, name in enumerate(header)}


def test_the_golden_fixtures_hold_none_of_the_shapes_the_new_readings_take() -> None:
    """ZR.6: so no question of the page fits a fixture column, and the fixtures' questions files stay."""
    for text in (fixtures.every_role_table(), fixtures.every_role_and_joined_table()):
        for name, column in _columns(text).items():
            cells = [cell for cell in column if cell.strip()]
            if not cells:
                continue
            assert not all(_on_the_grid(cell) for cell in cells), name
            assert _a_list(cells) is None, name
            assert not any(re.fullmatch(r"-?\d+,\d+", cell) for cell in cells), name
            assert not _far_or_listed(cells), name
            assert not _uid_asked(cells), name


UID = re.compile(r"[012](?:\.(?:0|[1-9]\d*)){2,}")


def _uid_asked(cells: "list[str]") -> bool:
    """Q-ID's shape: every present cell the UID grammar with two points or more, every value different."""
    return bool(cells) and all(UID.fullmatch(cell) for cell in cells) and len(set(cells)) == len(cells)


def test_q_id_asks_a_uid_column_and_neither_golden_measurement() -> None:
    """Skeptic 1's item 4: all-different figures and marks are measurements as often as identifiers."""
    draw = random.Random(20261021)
    uids = [
        f"1.2.840.113619.2.55.3.{draw.randint(100000000, 999999999)}.{draw.randint(100, 999)}.{1600000000 + index}"
        for index in range(600)
    ]
    assert _uid_asked(uids)
    assert not _uid_asked(uids[:-1] + [uids[0]])
    assert not _uid_asked([uid.replace(".", "-") for uid in uids])
    columns = _columns(fixtures.every_role_and_joined_table())
    for name, least in (("pressure", 240), ("amount", 238)):
        cells = [cell for cell in columns[name] if cell.strip()]
        # Figures and marks alone, nearly every value different: the
        # build's trigger reached both.
        assert all(re.fullmatch(r"[0-9./-]+", cell) for cell in cells), name
        assert len(set(cells)) >= least, name
        assert not _uid_asked(cells), name
    page = _flat(_page())
    assert "matches the DICOM UID grammar `[012](\\.(0\\|[1-9]\\d*))+` with at least two points" in page
    assert "so Q-ID asks neither" in page


def test_the_golden_note_is_out_of_notes_reach() -> None:
    """ZR.6: `note`'s published levels are one word each, so the share line never judges it."""
    for text in (fixtures.every_role_table(), fixtures.every_role_and_joined_table()):
        cells = [cell for cell in _columns(text)["note"] if cell.strip()]
        counts = collections.Counter(cells)
        published = sorted(level for level, rows in counts.items() if rows >= 11)
        assert published == ["clinic", "referral"]
        assert (counts["clinic"], counts["referral"]) == (12, 11)
        for level in published:
            assert len(level.split()) < 3 and "\n" not in level, level
        covered = sum(counts[level] for level in published)
        assert (covered, len(cells)) == (23, 240) and 4 * covered < len(cells)
        assert sum(1 for cell in cells if " " in cell) == 217
    page = _flat(_page())
    assert "`clinic` on 12 rows and `referral` on 11, are one word each" in page


def test_the_order_docstring_lists_no_rule_0c() -> None:
    """ZR.1: the docstring's list runs 0, 0b, 1 to 7, 7b, 8, 9, 9b, 9c, 10; 0c is a comment in the body."""
    doc = taxonomy._decide.__doc__ or ""
    order = doc[doc.index("THE ORDER, and there is only one"): doc.index("RULES 8 AND 9 SIT WHERE")]
    listed = re.findall(r"^\s*(\d+[bc]?)\. ", order, flags=re.MULTILINE)
    assert listed == ["0", "0b", "1", "2", "3", "4", "5", "6", "7", "7b", "8", "9", "9b", "9c", "10"]
    assert "# RULE 0c" in inspect.getsource(taxonomy._decide)


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
    # The answer rule A's month-year reading is offered as already exists.
    assert asking.ANSWER_DATES == "dates"
    page = _flat(_page())
    assert "No reading on this page drops a question that holds a column under P4-D401" in page


def test_contract_c6_1_lists_fourteen_of_its_fifteen_roles() -> None:
    """ZR.8 point 3: rule 7b's role is missing from C6-1's list; UN-1a restates it and changes this check."""
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("**C6-1.**")
    listed = text[start: text.index("Fourteen roles in thirteen rules", start)]
    assert "`numbers_with_labels`" not in listed
    assert "`joined_numbers`" in listed and "`free_text`" in listed
