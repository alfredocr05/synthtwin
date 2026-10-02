"""K-S3-56: a column of dates that cannot settle its own reading is asked, and the answer repairs it.

LANE R1 OF STAGE 3B, PLAN P4-D381. Two questions the values cannot
settle, put through the questions file and answered there, over the
columns of `tests/date_question_shapes.py` at their own sizes, a floor
of eleven and seed 0, through the real producer, generator and checker:

* `day_or_month_shapes` / `codes_shapes`: how many columns of each kind
  were measured -- dates no value of which says whether the day or the
  month comes first, and dates or times beside a few repeated codes;
* `asked`: how many of them the questions file asks about, with the
  answer that repairs the column among those it offers;
* `repaired`: how many come back, answered, read as dates or times with
  every twin cell outside the codes parsed by the person's own
  `strptime` format, the codes written back as often as the table wrote
  them, the twin checked with nothing MISSED, and nothing asked again;
* `twin_cells_unread`: answered twin cells outside the codes that format
  refuses, and `missed`: answered twins validation MISSES;
* `clean_shapes` / `clean_asked`: the thirty-seven spellings the reach
  audit of 2026-10-01 found read with no gap, and how many of them raise
  either question -- except `mdy_ambiguous`, whose every day is 12 or
  less and which is the day-first column's cells with the fields
  swapped, so the day-or-month question is right to reach it:
  `control_asked` counts it;
* `left_alone` / `left_alone_asked`: the shapes either question must
  leave alone -- a code on five rows, a third of the column, six codes,
  two dates, no dates -- and how many are asked.

Before lane R1 (668f276): neither question existed. Seven of the eight
columns with codes were read as labels or numbers, their twins parsing 0
to 59 in 100 cells under the person's format, and the eighth as dates,
its twenty codes written as made-up text (99.5 in 100); the six of the
day-or-month kind were read month first, the five written day first
parsing 41 to 74 in 100. Nothing was asked about dates, and three of the
eight were asked whether they were blood pressures.

    .venv/bin/python tools/measurements/kpi_date_questions.py --kpi
"""

import contextlib
import csv
import io
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import date_question_shapes as shapes  # noqa: E402
import fixtures  # noqa: E402
import kpi_rules  # noqa: E402

from synthtwin import asking  # noqa: E402
from synthtwin.cli import main as cli  # noqa: E402


def _quiet(argv: "list[str]") -> int:
    held = io.StringIO()
    with contextlib.redirect_stdout(held), contextlib.redirect_stderr(held):
        return cli(argv)


def _questions(folder: pathlib.Path) -> "dict[str, object]":
    found = json.loads((folder / "real-questions.json").read_text(encoding="utf-8"))
    assert isinstance(found, dict)
    return found


def asked_entry(questions: "dict[str, object]", answer: str) -> "dict[str, object] | None":
    """The entry of the questions file that offers ``answer``, or None."""
    sections = questions["asked"]
    about = questions["about_your_file"]
    assert isinstance(sections, list) and isinstance(about, list)
    for entry in about + sections:
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if answer in offered:
            return dict(entry)
    return None


def raises_either(questions: "dict[str, object]") -> "tuple[bool, bool]":
    """Whether the file asks the day-or-month question, and the codes question."""
    about = questions["about_your_file"]
    asked = questions["asked"]
    assert isinstance(about, list) and isinstance(asked, list)
    day_or_month = any(entry["column"] == asking.DAY_FIRST_SUBJECT for entry in about)
    codes = any(
        asking.ANSWER_NO_DATE in [choice["answer"] for choice in entry["answers_you_can_give"]]
        for entry in asked
    )
    return day_or_month, codes


def described(folder: pathlib.Path, shape: "shapes.Shape", *options: str) -> int:
    """Describe one shape's column in ``folder``; return the exit code."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, built = fixtures.rows_at_the_floor("seen_at", shapes.cells(shape))
    table.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="")
    return _quiet(["profile", str(table), "--out-dir", str(folder), "--replace", *options])


def answered(folder: pathlib.Path, shape: "shapes.Shape") -> "tuple[bool, int, bool, bool]":
    """Ask, answer, describe again, twin and check one shape.

    Returns whether it was asked, the twin cells outside the codes the
    person's format refuses, whether validation missed, and whether the
    answered column came back whole.
    """
    if described(folder, shape) != 0:
        return False, 0, False, False
    questions = _questions(folder)
    entry = asked_entry(questions, shape.answer)
    if entry is None:
        return False, 0, False, False
    for section in ("asked", "about_your_file"):
        listed = questions[section]
        assert isinstance(listed, list)
        for one in listed:
            if one["column"] == entry["column"]:
                one["your_answer"] = shape.answer
    answers = folder / "answers.json"
    answers.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    if described(folder, shape, "--answers", str(answers)) != 0:
        return True, 0, False, False
    block = json.loads((folder / "real-profile.json").read_text(encoding="utf-8"))["columns"][0]
    if _quiet(["generate", str(folder / "real-profile.json"), "--seed", "0", "--out-dir", str(folder), "--replace"]) != 0:
        return True, 0, False, False
    missed = _quiet(["validate", str(folder / "real-profile.json"), "--out-dir", str(folder), "--replace"]) != 0
    rows = list(csv.reader(io.StringIO((folder / "real-twin.csv").read_text(encoding="utf-8"))))[1:]
    twin = [row[0] for row in rows if row]
    unread = sum(1 for cell in twin if cell and cell not in shape.codes and not shapes.parses(cell, shape.fmt))
    real = shapes.cells(shape)
    codes_back = all(
        sum(1 for cell in twin if cell == code) == sum(1 for cell in real if cell == code)
        for code in shape.codes
    )
    again = raises_either(_questions(folder))
    whole = (
        block["role"] in ("datetime", "time_of_day")
        and unread == 0
        and not missed
        and codes_back
        and not again[0]
        and not again[1]
    )
    return True, unread, missed, whole


def measure(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    """Every shape once; the totals and what failed."""
    totals = {
        "day_or_month_shapes": len(shapes.DAY_OR_MONTH),
        "codes_shapes": len(shapes.CODES),
        "asked": 0,
        "repaired": 0,
        "twin_cells_unread": 0,
        "missed": 0,
        "clean_shapes": len(shapes.CLEAN),
        "clean_asked": 0,
        "control_asked": 0,
        "left_alone": len(shapes.NOT_ASKED),
        "left_alone_asked": 0,
    }
    notes: "list[str]" = []
    for shape in shapes.DAY_OR_MONTH + shapes.CODES:
        was_asked, unread, missed, whole = answered(home / shape.name, shape)
        totals["asked"] += 1 if was_asked else 0
        totals["repaired"] += 1 if whole else 0
        totals["twin_cells_unread"] += unread
        totals["missed"] += 1 if missed else 0
        if not was_asked:
            notes += [f"{shape.name}: not asked"]
        elif not whole:
            notes += [f"{shape.name}: answered and not repaired ({unread} unread, missed {missed})"]
    for shape in shapes.CLEAN + shapes.NOT_ASKED:
        folder = home / f"plain-{shape.name}"
        if described(folder, shape) != 0:
            notes += [f"{shape.name}: not described"]
            continue
        day_or_month, codes = raises_either(_questions(folder))
        if shape in shapes.NOT_ASKED:
            if day_or_month or codes:
                totals["left_alone_asked"] += 1
                notes += [f"{shape.name}: asked"]
            continue
        if shape.name in shapes.CLEAN_AMBIGUOUS and day_or_month and not codes:
            totals["control_asked"] += 1
            continue
        if day_or_month or codes:
            totals["clean_asked"] += 1
            notes += [f"{shape.name}: asked"]
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = measure(pathlib.Path(folder))
    kpi_rules.emit(
        "K-S3-56", totals,
        "; ".join(notes) if notes else "every column asked, every answer repaired, every clean spelling left alone",
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
