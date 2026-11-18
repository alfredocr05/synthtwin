"""K-HZ-36: ages beside a repeating subject described as ages, bin groups counted in people, and measurements no longer asked as ages, at 20,000 and 200,000 rows (plan P4-D486).

Lane HB3-a2's parts, each through the command a person types -- `profile`
with nobody at the keyboard, the questions file answered truthfully round by
round where the leg says so, `generate` at seed 0, `validate` -- on invented
tables whose generating structure is known, counted by linear counters (each
real cell and each twin cell read once):

- THE VISIT TABLE, 1,000 people of 20 visits (20,000 rows) and 10,000 people
  of 20 (200,000 rows): one age a person, about 58 +/- 17 years from 0 to 105
  (three in a hundred children), written plain (`age`), with its unit word
  (`age_text`, `72 years`), with its word before it (`age_label`, `Age 72`),
  with a letter (`age_y`, `72 y`), with one decimal (`age_dec`), zero-padded
  (`age_pad`, answered `measurement`), and in months under a name that says
  so (`age_in_months`); beside them a 0/1 outcome whose log odds rise 0.06 a
  year of age and a reading of 90 + 0.6 a year of age (+/- 8). With the
  person column declared (`--identifier subject_id`) and, at 20,000 rows,
  without it, its questions answered. Each spelling held whole or described
  (`spellings_held`, of `spellings`), and for each one described the twin's
  mean, SD and quantiles p5 to p95 in years against the real table's, against
  the real ages as its block publishes them (the top code and the ends
  applied) and against the plain column's twin (`parity_gaps`: spellings
  whose twin lies further from its own published ages than the plain twin
  lies from its own, by more than 0.5 years in the mean or 5 per cent of the
  SD -- lane HB3-a2's repair 1, the statistics check's item 2: the plain
  twin's own one-year shift at 10,000 people is the generator's, not a
  spelling's), the slope of the outcome on age and the reading's mean by age
  band printed per spelling (route S: the command's default twin, which
  carries no relationship between columns on a table of several rows a
  person until the patient walk is switched on, lane GRb2 with CHON).
- THE CAPPED TABLE (W (1)): the same people's ages kept within 25 to 89 under
  `age`, beside the declared person column, at 20,000 and 200,000 rows:
  held (`capped_held`).
- THE BIN GROUPS (C5): 1,000 people of 20 rows, 15 aged 25 (10 inside the
  200-row low tail), 28 to 89 each 15 or 16 people's, 15 aged 90, an age and
  a one-decimal column of the same values beside the declared person column;
  and (lane HB3-a2's repair 1, skeptic 1's item 1) a reading written `NNN.N
  mg/dL` by 900 people and `N.N mmol/L` by 100, whose wrapper's `numbers`
  publish their own bin groups, every numeric block counted
  (`_every_block_below_floor`; `counters_blind`: the nested counter on blocks
  made to publish a group of 2 people in a wrapper's numbers, in the numbers
  beside labels and in a part of joined numbers, each read).
- EVERY DESCRIPTION: each number its block publishes and each bin group 1 to
  10 people hold (`published_below_floor`, the groups' people counted over
  the interior rows by rank, the tails' rows set aside), every figure past 90
  years in a key, a label or a value of the block (`ages_past_89_shown`), and
  twin cells past 90 years (`ages_past_89_written`); each leg whose
  `validate` of the twin does not exit 0 (`legs_validate_not_0`, an at-most
  key at the measured count: the plain column's twin at 10,000 people misses
  its own low tail's values, on the base as on the head).
- THE OBSERVATIONS (R beside bare ages; lane HB3-a2's repair 1, the
  statistics check's item 1): 10,000 people of 20 rows, a value column
  holding the person's age bare on one row in five (18 to 104) beside
  weights, pulses and pressures written with their units, the person
  declared, unanswered: its block's figures past 90 and its twin's bare cells
  past 90 join `ages_past_89_shown` and `ages_past_89_written`.
- THE READING RULE (R): a measurement table of the same people (a weight
  `NN.N kg`, a rate `NN bpm`, a pressure `NN mmHg`, bare ones beside them and
  an age written bare under the neutral name `level_k`), the person declared,
  unanswered: the columns set out of the reach by their units
  (`unit_columns_set_out`, of 3), age columns set out (`ages_set_out`, the
  control and a generated check over 4,000 age columns: each word, unit,
  affix and band of the vocabulary in one cell among unit cells, and every
  name that says age), the twin's weights of 90 kg or more against the
  real's; and over the zoo's whole catalogue at 20,000 rows (E0a's tables
  and E0c's wide ones, `health_zoo.catalogue()`), the columns the rule sets
  out of the reach, each named (`zoo_columns_set_out`).
- THE HELD STAND-INS (S, left by the size valve to lane HB3-b-b): the twin cells
  of a held age column (the visit table beside its zero-padded copy, whose
  open question holds the ages whole, without its person column,
  unanswered) whose number place writes a figure past 89
  (`held_stand_ins_past_89`).

    .venv/bin/python tools/measurements/kpi_ages_widened.py --kpi
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import math
import pathlib
import random
import re
import shutil
import statistics
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import health_zoo  # noqa: E402

from synthtwin import cli, parsing, profile, taxonomy  # noqa: E402

FLOOR = 11
NUMBER = re.compile(r"\d+(?:\.\d+)?")
SPELLINGS = ("age", "age_text", "age_label", "age_y", "age_dec", "age_pad", "age_in_months")
IN_MONTHS = {"age_in_months": 12.0}
# Count keys and sentences of a block: no value (the K-HZ-29 counters' reading).
_SENTENCE_KEYS = ("detection_evidence", "remarks", "name", "negative_form", "group_separator", "statistical_type",
                  "quality_state", "structural_role", "role", "n_distinct_by_occurrences", "field_widths",
                  "missing_by_class", "missing_by_source", "numeric_styles", "layout_forms", "layout_prefixes",
                  "layout_exclusions", "shape_forms", "figure_openings", "top_coded")
_VALUE_KEYS = ("percentiles", "percentiles_between", "mode", "mean", "top_coded_ends", "top_coded_band_values", "boundary",
               "values", "value")
_RUNG_NAME = re.compile(r"p\d\d")


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _base_age(draw: random.Random) -> int:
    if draw.random() < 0.03:
        return draw.randint(0, 17)
    return max(0, min(105, int(round(draw.gauss(58, 17)))))


def visit_table(people: int, seed: int, capped: bool = False) -> "tuple[list[str], list[list[str]]]":
    """The invented visit table: one age a person in every spelling, an outcome and a reading of known slopes."""
    draw = random.Random(seed)
    header = ["subject_id", "visit_date", *SPELLINGS, "outcome_flag", "reading_k"]
    rows: "list[list[str]]" = []
    for who in range(people):
        age = int(min(89, max(25, round(draw.gauss(55, 12))))) if capped else _base_age(draw)
        tenth, month = draw.randint(0, 9), draw.randint(0, 11)
        start = datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randint(0, 700))
        for visit in range(20):
            day = start + datetime.timedelta(days=90 * visit + draw.randint(0, 20))
            rows += [[f"S{100000 + who}", day.isoformat(), f"{age}", f"{age} years", f"Age {age}", f"{age} y",
                      f"{age}.{tenth}", f"{age:03d}", f"{age * 12 + month}",
                      f"{int(draw.random() < _logistic(-4.0 + 0.06 * age))}",
                      f"{round(90 + 0.6 * age + draw.gauss(0, 8), 1)}"]]
    return header, rows


def c5_table() -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(20261115)
    ages = [25] * 15 + [90] * 15 + [28 + place % 62 for place in range(970)]
    draw.shuffle(ages)
    return ["subject_id", "age", "level_dec"], [
        [f"S{10000 + who}", f"{ages[who]}", f"{ages[who]}.0"] for who in range(1000) for _visit in range(20)
    ]


def two_units_table() -> "tuple[list[str], list[list[str]]]":
    """A reading written `NNN.N mg/dL` by 900 people and `N.N mmol/L` by 100, 20 rows each, each person's values close to their own centre (C5 in a wrapper's `numbers`; lane HB3-a2's repair 1)."""
    draw = random.Random(4875)
    rows: "list[list[str]]" = []
    for who in range(1000):
        small = who >= 900
        centre = draw.gauss(5.5, 1.2) if small else draw.gauss(100.0, 22.0)
        for _row in range(20):
            value = centre + draw.gauss(0.0, 0.3 if small else 5.0)
            rows += [[f"S{10000 + who}", f"{value:.1f} mmol/L" if small else f"{value:.1f} mg/dL"]]
    return ["subject_id", "reading"], rows


def observations_table(people: int) -> "tuple[list[str], list[list[str]]]":
    """Observations a row, one value column (the statistics check's item 1): the person's age written bare on one row in five (one age a person, 18 to 104), a weight `NN kg`, a pulse `NN bpm` and a pressure `NN mmHg` on the others, 20 rows a person."""
    draw = random.Random(20261116 + people)
    rows: "list[list[str]]" = []
    for who in range(people):
        age = max(18, min(104, int(round(draw.gauss(62, 16)))))
        start = datetime.date(2019, 1, 1) + datetime.timedelta(days=draw.randint(0, 700))
        for row in range(20):
            name = ("Age", "Weight", "Pulse", "Diastolic", "Weight")[row % 5]
            written = {
                "Age": f"{age}", "Weight": f"{int(draw.gauss(80, 17))} kg",
                "Pulse": f"{int(draw.gauss(78, 12))} bpm", "Diastolic": f"{int(draw.gauss(76, 10))} mmHg",
            }[name]
            rows += [[f"S{100000 + who}", (start + datetime.timedelta(days=30 * row)).isoformat(), name, written]]
    return ["subject_id", "taken_on", "obs_name", "obs_value"], rows


def unit_table() -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(20261114)
    rows: "list[list[str]]" = []
    for who in range(1000):
        weight, rate, pressure = draw.gauss(78, 18), draw.gauss(80, 12), draw.gauss(76, 11)
        neutral = _base_age(draw)
        for _visit in range(20):
            kilos = max(35.0, weight + draw.gauss(0, 2))
            beat = int(max(35, rate + draw.gauss(0, 9)))
            low = int(max(35, min(125, pressure + draw.gauss(0, 7))))
            rows += [[f"S{10000 + who}", f"{kilos:.1f} kg", f"{beat} bpm", f"{low} mmHg", f"{kilos:.1f}", f"{beat}",
                      f"{neutral}"]]
    return ["subject_id", "weight", "rate", "pressure", "weight_bare", "rate_bare", "level_k"], rows


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _truthful(column: str) -> "list[str]":
    if column == "subject_id":
        return ["identifier"]
    if column == "age_in_months":
        return ["months", "yes", "measurement", "keep"]
    if column.startswith("age") or column == "level_k":
        return ["years", "yes", "measurement", "keep"]
    if column == "outcome_flag":
        return ["no", "code", "measurement", "keep"]
    return ["no", "measurement", "keep", "code"]


def _answer(path: pathlib.Path) -> int:
    document = json.loads(path.read_text(encoding="utf-8"))
    given = 0
    for entry in document.get("asked", []):
        if f"{entry.get('your_answer') or ''}":
            continue
        offered = [f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]
        for want in _truthful(f"{entry.get('column')}"):
            if want in offered:
                entry["your_answer"] = want
                given += 1
                break
    path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    return given


def _run(folder: pathlib.Path, source: pathlib.Path, declared: "list[str]", answered: bool) -> "dict[str, object]":
    """profile (nobody at the keyboard), the answer rounds where ``answered``, generate at seed 0, validate."""
    folder.mkdir(parents=True, exist_ok=True)
    questions = folder / f"{source.stem}-questions.json"
    exits: "list[int]" = []
    seconds: "dict[str, float]" = {}
    screen = io.StringIO()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        started = time.process_time()
        exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", *declared])]
        seconds["profile"] = round(time.process_time() - started, 2)
        for _round in range(4 if answered and exits[0] == 0 else 0):
            if not _answer(questions):
                break
            exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers",
                                f"{questions}", *declared])]
        twin_folder = folder / "twin"
        twin_folder.mkdir(exist_ok=True)
        described = folder / f"{source.stem}-profile.json"
        started = time.process_time()
        exits += [cli.main(["generate", f"{described}", "--out-dir", f"{twin_folder}", "--seed", "0", "--replace"])]
        seconds["generate"] = round(time.process_time() - started, 2)
        twin_path = twin_folder / f"{source.stem}-twin.csv"
        exits += [cli.main(["validate", f"{described}", "--twin", f"{twin_path}", "--out-dir", f"{twin_folder}",
                            "--replace"]) if twin_path.is_file() else -1]
    blocks = {f"{one['name']}": one for one in json.loads(described.read_text(encoding="utf-8"))["columns"]} if exits[0] == 0 else {}
    twin: "list[list[str]]" = []
    if twin_path.is_file():
        with open(twin_path, encoding="utf-8", newline="") as handle:
            twin = list(csv.reader(handle))
    texts = [screen.getvalue()]
    for name in sorted(folder.glob("*.txt")) + sorted(folder.glob("*.json")):
        texts += [name.read_text(encoding="utf-8")]
    return {"exits": exits, "seconds": seconds, "blocks": blocks, "twin": twin, "texts": texts}


def _years(cell: str, divisor: float) -> "float | None":
    found = NUMBER.search(cell)
    return None if found is None else float(found.group(0)) / divisor


def _figures_past(block: "dict[str, object]", divisor: float) -> int:
    """Figures past 90 years a block holds in a key, a label, a text value or a value key (K-HZ-29's widened reading)."""
    found = 0
    waiting: "list[tuple[str, object, bool]]" = [("", block, False)]
    while waiting:
        key, leaf, valued = waiting.pop()
        if key in _SENTENCE_KEYS:
            continue
        if isinstance(leaf, dict):
            for inner in leaf:
                if not _RUNG_NAME.fullmatch(f"{inner}"):
                    found += sum(1 for run in NUMBER.findall(f"{inner}") if float(run) / divisor > 90)
                waiting += [(f"{inner}", leaf[inner], valued or key in _VALUE_KEYS)]
        elif isinstance(leaf, list):
            waiting += [(key, item, valued) for item in leaf]
        elif isinstance(leaf, str):
            found += sum(1 for run in NUMBER.findall(leaf) if float(run) / divisor > 90)
        elif isinstance(leaf, (int, float)) and not isinstance(leaf, bool) and (valued or key in _VALUE_KEYS):
            found += int(leaf / divisor > 90)
    return found


def _below_floor(block: "dict[str, object]", values: "list[float | None]", people: "list[str]", groups_only: bool = False) -> int:
    """Numbers a block publishes, and its bin groups, that 1 to 10 people hold: each row's value as the block reads it; ``groups_only``, its bin groups alone (a measurement that varies within a person, whose rungs P4-D406 counts in rows)."""
    holders: "dict[float, set[str]]" = {}
    for value, person in zip(values, people):
        if value is not None:
            holders.setdefault(value, set()).add(person)
    found = 0
    for number in () if groups_only else profile._published_in(block, True).numbers:
        if 0 < len(holders.get(number, set())) < FLOOR:
            found += 1
    groups = block.get("bin_groups")
    tails = block.get("tails")
    if isinstance(groups, list) and groups and isinstance(tails, dict) and tails.get("low") and tails.get("high"):
        rungs = {**(block.get("percentiles") or {}), **(block.get("percentiles_between") or {})}  # type: ignore[dict-item]
        low, high = tails["low"], tails["high"]
        lowest, highest = rungs.get(f"p{low['percent']:02d}"), rungs.get(f"p{high['percent']:02d}")
        if isinstance(lowest, (int, float)) and isinstance(highest, (int, float)) and highest > lowest:
            ranked = sorted((value, place) for place, value in enumerate(values) if value is not None)
            interior = ranked[low["rows"]: len(ranked) - high["rows"]]
            for group in groups:
                inside = {people[place] for value, place in interior
                          if group["first"] <= parsing.histogram_bin(value, lowest, highest) <= group["last"]}
                found += int(0 < len(inside) < FLOOR)
    return found


def _every_block_below_floor(block: "dict[str, object]", read: "dict[str, list[float | None]]", people: "list[str]",
                             groups_only: bool = False) -> int:
    """`_below_floor` over EVERY numeric block a column publishes (lane HB3-a2's repair 1, skeptic 1's item 1): its own (`top`), each wrapper's `numbers` (by its suffix), the `numbers` of numbers with labels and each of its `parts` (`part0`, ...), each over the values this driver reads for that block (``read``); a block it reads no values for counts as wholly few-held, so a block it cannot read is never passed over."""
    found = _below_floor(block, read["top"], people, groups_only) if "top" in read else 0
    nested: "list[tuple[str, object]]" = [(f"{variant.get('suffix')}", variant.get("numbers"))
                                          for variant in block.get("affix_variants") or [] if isinstance(variant, dict)]  # type: ignore[attr-defined]
    nested += [("numbers", block.get("numbers"))] if isinstance(block.get("numbers"), dict) else []
    nested += [(f"part{place}", part) for place, part in enumerate(block.get("parts") or [])]  # type: ignore[arg-type]
    for name, inner in nested:
        if not isinstance(inner, dict):
            continue
        if name not in read:
            found += len(inner.get("bin_groups") or []) or 1
            continue
        found += _below_floor(inner, read[name], people, groups_only)
    return found


def _counters_blind() -> "list[str]":
    """The nested counter on blocks made to publish what it counts: the names of those it reads none of (lane HB3-a2's repair 1; the shape of K-HZ-29's `counters_blind`)."""
    blind: "list[str]" = []
    people = [f"P{who}" for who in range(30) for _row in range(20)]
    values: "list[float | None]" = [float(who) for who in range(30) for _row in range(20)]
    inner: "dict[str, object]" = {"percentiles": {"min": 0.0, "max": 29.0}, "percentiles_between": {"p01": 0.0, "p99": 29.0},
                                  "tails": {"low": {"percent": 1, "rows": 6}, "high": {"percent": 99, "rows": 6}},
                                  "bin_groups": [{"first": 0, "last": 1, "count": 34}, {"first": 2, "last": 31, "count": 554}]}
    bare = {key: inner[key] for key in inner if key != "bin_groups"}
    for name, made in (
        ("a wrapper's numbers", lambda one: {"affix_variants": [{"suffix": " u", "numbers": one}]}),
        ("the numbers beside labels", lambda one: {"numbers": one}),
        ("a part of joined numbers", lambda one: {"parts": [one]}),
    ):
        key = {"a wrapper's numbers": " u", "the numbers beside labels": "numbers"}.get(name, "part0")
        if _every_block_below_floor(made(inner), {key: values}, people, True) < 1 or _every_block_below_floor(made(bare), {key: values}, people, True):
            blind += [f"a bin group of 2 people in {name}"]
    return blind


def _as_read(cells: "list[str]", block: "dict[str, object]", divisor: float) -> "list[float | None]":
    """Each cell's number as the block reads it: in its own unit, the top code and the ends applied in years."""
    top = block.get("top_coded")
    ends = block.get("top_coded_ends")
    found: "list[float | None]" = []
    for cell in cells:
        read = NUMBER.search(cell)
        if read is None:
            found += [None]
            continue
        value = float(read.group(0))
        if isinstance(top, int) and value / divisor >= 90:
            value = float(top)
        if isinstance(ends, list) and len(ends) == 2:
            years = value / divisor
            # ...each band at the age it records where it records one
            # (`top_coded_band_values`, lane RX-1).
            band = block.get("top_coded_band_values")
            if isinstance(band, list) and len(band) == 2:
                if years <= ends[0]:
                    value = float(band[0]) * divisor
                elif years >= ends[1]:
                    value = float(band[1]) * divisor
            elif years < ends[0]:
                value = float(ends[0]) * divisor
            elif years > ends[1]:
                value = float(ends[1]) * divisor
        found += [value]
    return found


def _quantiles(values: "list[float]") -> "list[float]":
    ordered = sorted(values)
    return [round(ordered[min(len(ordered) - 1, int(share * len(ordered)))], 2) for share in (0.05, 0.25, 0.5, 0.75, 0.95)]


def _slope(pairs: "list[tuple[float, int]]") -> "float | None":
    """The logistic slope of a 0/1 outcome on a value, by Newton steps in plain Python."""
    if len({outcome for _value, outcome in pairs}) < 2:
        return None
    centre = sum(value for value, _outcome in pairs) / len(pairs)
    b0 = b1 = 0.0
    for _step in range(25):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for value, outcome in pairs:
            z = value - centre
            p = _logistic(b0 + b1 * z)
            w = p * (1 - p)
            g0, g1 = g0 + outcome - p, g1 + (outcome - p) * z
            h00, h01, h11 = h00 + w, h01 + w * z, h11 + w * z * z
        det = h00 * h11 - h01 * h01
        if det <= 0:
            return None
        b0, b1 = b0 + (h11 * g0 - h01 * g1) / det, b1 + (-h01 * g0 + h00 * g1) / det
    return round(b1, 4)


def _band_means(pairs: "list[tuple[float, float]]") -> "dict[str, float]":
    bands: "dict[int, list[float]]" = {}
    for value, reading in pairs:
        found = bands.setdefault(min(4, int(value // 20)), [])
        found += [reading]
    return {f"{band * 20}-{band * 20 + 19}": round(sum(found) / len(found), 1) for band, found in sorted(bands.items()) if len(found) >= 50}


def _summary(values: "list[float]") -> "list[float]":
    return [round(statistics.mean(values), 2), round(statistics.pstdev(values), 2), *_quantiles(values)]


def _legs(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """The visit table at 20,000 rows (person declared and not) and 200,000 (declared), the capped table and C5."""
    plain_twin: "dict[str, list[float]]" = {}
    for label, people, declared, answered in (("20k-declared", 1000, True, False), ("20k-answered", 1000, False, True),
                                              ("200k-declared", 10000, True, False)):
        header, rows = visit_table(people, 20261111 + people)
        folder = scratch / label
        folder.mkdir(parents=True)
        source = folder / "visits.csv"
        _write(source, header, rows)
        run = _run(folder, source, ["--identifier", "subject_id"] if declared else [], answered)
        twin = run["twin"]
        assert isinstance(twin, list) and isinstance(run["blocks"], dict)
        twin_header = twin[0] if twin else []
        people_of = [row[0] for row in rows]
        outcome_at, reading_at = header.index("outcome_flag"), header.index("reading_k")
        for spelling in SPELLINGS:
            divisor = IN_MONTHS.get(spelling, 1.0)
            place = header.index(spelling)
            block = run["blocks"].get(spelling, {})
            cells = [row[place] for row in rows]
            real = [found for found in (_years(cell, divisor) for cell in cells) if found is not None]
            held = block.get("role") == taxonomy.ROLE_IDENTIFIER
            value["spellings"] = int(value["spellings"]) + 1  # type: ignore[call-overload]
            value["spellings_held"] = int(value["spellings_held"]) + int(held)  # type: ignore[call-overload]
            value["ages_past_89_shown"] = int(value["ages_past_89_shown"]) + _figures_past(block, divisor)  # type: ignore[call-overload]
            if not held:
                value["published_below_floor"] = int(value["published_below_floor"]) + _below_floor(  # type: ignore[call-overload]
                    block, _as_read(cells, block, divisor), people_of)
            text = f"{label} {spelling}: {'held' if held else block.get('role')}, ends {block.get('top_coded_ends')}"
            if spelling in twin_header:
                at = twin_header.index(spelling)
                made = [_years(row[at], divisor) for row in twin[1:]]
                written = [found for found in made if found is not None]
                # ...a described column's twin cells past 90 years; a held
                # column's made-up cells read as their cells are written, its
                # real spellings past 89 alone (K-HZ-29's reading).
                old = {cell for cell in cells if (_years(cell, divisor) or 0.0) > 89.0 + 1e-9}
                value["ages_past_89_written"] = int(value["ages_past_89_written"]) + (  # type: ignore[call-overload]
                    sum(1 for row in twin[1:] if row[at] in old and (_years(row[at], divisor) or 0.0) > 90.0 + 1e-9)
                    if held else sum(1 for found in written if found > 90.0 + 1e-9))
                if written and real:
                    own = _summary(written)
                    # ...against the real ages as the block publishes them
                    # (the top code and the ends applied): a twin's distance
                    # from its own published column is what a spelling adds
                    # (lane HB3-a2's repair 1, the statistics check's item 2).
                    shown = [found / divisor for found in _as_read(cells, block, divisor) if found is not None]
                    published = _summary(shown) if shown and not held else _summary(real)
                    text += f"; twin {own} against real {_summary(real)}, as published {published[:2]}"
                    distance = (abs(own[0] - published[0]), abs(own[1] - published[1]))
                    if spelling == "age":
                        plain_twin[label] = [*own, *distance]
                    elif not held and label in plain_twin:
                        plain = plain_twin[label]
                        gap = distance[0] > plain[7] + 0.5 or distance[1] > plain[8] + 0.05 * published[1]
                        value["parity_gaps"] = int(value["parity_gaps"]) + int(gap)  # type: ignore[call-overload]
                        text += f"; plain twin {plain[:2]} off its own published {plain[7:9]}{' GAP' if gap else ''}"
                    pairs_real = [(found, int(row[outcome_at])) for found, row in
                                  zip((_years(cell, divisor) for cell in cells), rows) if found is not None]
                    pairs_twin = [(found, int(row[twin_header.index('outcome_flag')])) for found, row in zip(made, twin[1:])
                                  if found is not None and row[twin_header.index('outcome_flag')] in ("0", "1")]
                    text += f"; slope real {_slope(pairs_real)} twin {_slope(pairs_twin)} (route S)"
                    readings_twin = [(found, float(row[twin_header.index('reading_k')])) for found, row in zip(made, twin[1:])
                                     if found is not None and NUMBER.fullmatch(row[twin_header.index('reading_k')] or "x")]
                    readings_real = [(found, float(row[reading_at])) for found, row in
                                     zip((_years(cell, divisor) for cell in cells), rows) if found is not None]
                    text += f"; reading by band real {_band_means(readings_real)} twin {_band_means(readings_twin)}"
            lines += [text]
            print(text, flush=True)
        lines += [f"{label} seconds {run['seconds']} exits {run['exits']}"]
        value["legs_validate_not_0"] = int(value["legs_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload, index]
        shutil.rmtree(folder, ignore_errors=True)
    for label, people in (("20k", 1000), ("200k", 10000)):
        header, rows = visit_table(people, 20261112 + people, capped=True)
        folder = scratch / f"capped-{label}"
        folder.mkdir(parents=True)
        source = folder / "capped.csv"
        _write(source, header[:3], [row[:3] for row in rows])
        run = _run(folder, source, ["--identifier", "subject_id"], False)
        block = run["blocks"].get("age", {})  # type: ignore[union-attr]
        held = block.get("role") == taxonomy.ROLE_IDENTIFIER
        value["capped_held"] = int(value["capped_held"]) + int(held)  # type: ignore[call-overload]
        if not held:
            value["published_below_floor"] = int(value["published_below_floor"]) + _below_floor(  # type: ignore[call-overload]
                block, _as_read([row[2] for row in rows], block, 1.0), [row[0] for row in rows])
        twin = run["twin"]
        made = [float(row[2]) for row in twin[1:] if NUMBER.fullmatch(row[2])] if twin else []  # type: ignore[index]
        real = [float(row[2]) for row in rows]
        lines += [f"capped {label}: {'held' if held else block.get('role')}, ends {block.get('top_coded_ends')}, "
                  f"twin {_summary(made) if made else None} against real {_summary(real)}, exits {run['exits']}"]
        value["legs_validate_not_0"] = int(value["legs_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload, index]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)
    header, rows = c5_table()
    folder = scratch / "c5"
    folder.mkdir(parents=True)
    source = folder / "c5.csv"
    _write(source, header, rows)
    run = _run(folder, source, ["--identifier", "subject_id"], False)
    for name, place in (("age", 1), ("level_dec", 2)):
        block = run["blocks"].get(name, {})  # type: ignore[union-attr]
        below = _below_floor(block, _as_read([row[place] for row in rows], block, 1.0), [row[0] for row in rows])
        value["published_below_floor"] = int(value["published_below_floor"]) + below  # type: ignore[call-overload]
        value["c5_groups_below_floor"] = int(value["c5_groups_below_floor"]) + below  # type: ignore[call-overload]
        lines += [f"C5 {name}: {block.get('role')}, groups {[(g['first'], g['last'], g['count']) for g in block.get('bin_groups') or []][:3]}, below the floor {below}"]
        print(lines[-1], flush=True)
    value["legs_validate_not_0"] = int(value["legs_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload, index]
    shutil.rmtree(folder, ignore_errors=True)
    _two_units(scratch, value, lines)


def _two_units(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """C5 in a wrapper's `numbers` (lane HB3-a2's repair 1, skeptic 1's item 1): the two-unit reading through the command, the person declared, every block's groups and published values counted in people."""
    header, rows = two_units_table()
    folder = scratch / "two-units"
    folder.mkdir(parents=True)
    source = folder / "two-units.csv"
    _write(source, header, rows)
    run = _run(folder, source, ["--identifier", "subject_id"], False)
    block = run["blocks"].get("reading", {})  # type: ignore[union-attr]
    read: "dict[str, list[float | None]]" = {
        "top": [float(row[1][:-6]) if row[1].endswith(" mg/dL") else None for row in rows],
        " mmol/L": [float(row[1][:-7]) if row[1].endswith(" mmol/L") else None for row in rows],
    }
    held = block.get("role") == taxonomy.ROLE_IDENTIFIER
    # ...its groups counted in people; its rungs, a measurement that varies
    # within a person, P4-D406 counts in rows.
    below = 0 if held else _every_block_below_floor(block, read, [row[0] for row in rows], True)
    value["c5_groups_below_floor"] = int(value["c5_groups_below_floor"]) + below  # type: ignore[call-overload]
    value["legs_validate_not_0"] = int(value["legs_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload, index]
    groups = {"top": len(block.get("bin_groups") or [])}
    groups.update({f"{variant.get('suffix')}": len(variant["numbers"].get("bin_groups") or [])
                   for variant in block.get("affix_variants") or []})
    lines += [f"C5 two units: {'held' if held else block.get('role')}, groups {groups}, below the floor {below}, exits {run['exits']}"]
    print(lines[-1], flush=True)
    shutil.rmtree(folder, ignore_errors=True)


def _observations(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """R beside bare ages (the statistics check's item 1): the observations table at 10,000 people of 20 rows through the command, the person declared, unanswered: every figure past 90 its value column's block shows, and its twin's bare cells past 90 -- the ages, the only cells written without a unit."""
    header, rows = observations_table(10000)
    folder = scratch / "observations"
    folder.mkdir(parents=True)
    source = folder / "observations.csv"
    _write(source, header, rows)
    run = _run(folder, source, ["--identifier", "subject_id"], False)
    block = run["blocks"].get("obs_value", {})  # type: ignore[union-attr]
    twin = run["twin"]
    assert isinstance(twin, list)
    shown = _figures_past(block, 1.0)
    at = twin[0].index("obs_value") if twin else -1
    # ...a described column's bare twin cells past 90; a held column's made-up
    # cells read as their cells are written, its real ages past 89 alone.
    old = {row[3] for row in rows if row[2] == "Age" and int(row[3]) > 89}
    held = block.get("role") == taxonomy.ROLE_IDENTIFIER
    written = sum(1 for row in twin[1:] if (row[at] in old if held else (NUMBER.fullmatch(row[at].strip()) and float(row[at]) > 90.0))) if twin else 0
    value["ages_past_89_shown"] = int(value["ages_past_89_shown"]) + shown  # type: ignore[call-overload]
    value["ages_past_89_written"] = int(value["ages_past_89_written"]) + written  # type: ignore[call-overload]
    value["legs_validate_not_0"] = int(value["legs_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload, index]
    real = sum(1 for row in rows if row[2] == "Age" and int(row[3]) > 89)
    lines += [f"R observations 200k: {block.get('role')}, top code {block.get('top_coded')}, figures past 90 shown {shown}, "
              f"bare twin cells past 90 {written} (real ages past 89: {real} cells), seconds {run['seconds']}, exits {run['exits']}"]
    print(lines[-1], flush=True)
    shutil.rmtree(folder, ignore_errors=True)


def _units(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """R: the measurement table through the command, the generated age columns, the zoo's catalogue."""
    header, rows = unit_table()
    folder = scratch / "units"
    folder.mkdir(parents=True)
    source = folder / "units.csv"
    _write(source, header, rows)
    run = _run(folder, source, ["--identifier", "subject_id"], False)
    blocks = run["blocks"]
    twin = run["twin"]
    assert isinstance(blocks, dict) and isinstance(twin, list)
    for name in ("weight", "rate", "pressure"):
        out = "top_coded" not in blocks.get(name, {"top_coded": 90})
        value["unit_columns_set_out"] = int(value["unit_columns_set_out"]) + int(out)  # type: ignore[call-overload]
        at = header.index(name)
        real = [_years(row[at], 1.0) or 0.0 for row in rows]
        made = [_years(row[twin[0].index(name)], 1.0) or 0.0 for row in twin[1:]] if twin else []
        lines += [f"R {name}: {'set out' if out else 'reached'}; values of 90 or more real {sum(1 for x in real if x >= 90)} "
                  f"twin {sum(1 for x in made if x >= 90)}; twin {_summary(made) if made else None} against real {_summary(real)}"]
        print(lines[-1], flush=True)
    value["ages_set_out"] = int(value["ages_set_out"]) + int("top_coded" not in blocks.get("level_k", {}))  # type: ignore[call-overload]
    shutil.rmtree(folder, ignore_errors=True)
    draw = random.Random(4865)
    sayings = (
        [f"{word} 95" for word in taxonomy.AGE_VOCABULARY.before]
        + [f"95 {unit}" for unit, _letter in taxonomy.AGE_VOCABULARY.units if unit]
        + [f"95{affix}" for affix in taxonomy.AGE_VOCABULARY.affixes]
        + ["95y", ">89", "90+", "≥90", "<18"]
    )
    generated = 0
    read_before = 0
    for unit in taxonomy.NO_AGE_UNITS:
        for saying in sayings:
            for how in (str.lower, str.upper, str.title):
                cells = [f"{draw.randint(40, 125)} {unit}" for _cell in range(400)]
                cells[draw.randrange(len(cells))] = how(saying)
                generated += 1
                # ...set out by the rule: in the reach where nothing but the
                # rule is asked (``said``), out of it where the rule is.
                if taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, said=True) != taxonomy.SAFE_HARBOR_AGES:
                    continue
                read_before += 1
                value["ages_set_out"] = int(value["ages_set_out"]) + int(  # type: ignore[call-overload]
                    taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) != taxonomy.SAFE_HARBOR_AGES)
    lines += [f"R generated age columns among unit cells: {generated}, {read_before} of them in the reach without the rule"]
    moved: "list[str]" = []
    # ...over the whole catalogue, E0c's wide tables too (the statistics
    # check's item 5: seven of the eleven columns the reach reads are there).
    for table in health_zoo.runnable_tables(health_zoo.catalogue()):
        header, rows = table.build(health_zoo.KPI_ROWS, health_zoo.seed_of(table))
        for place, name in enumerate(header):
            cells = [row[place] if place < len(row) else "" for row in rows]
            # ...each column read with a decimal comma where most of its cells
            # write one between figures, as the describe reads it.
            comma = 2 * sum(1 for cell in cells if re.fullmatch(r"\s*-?\d+,\d+\D*", cell)) > len(cells)
            if taxonomy.safe_harbor_reach(cells, comma, frozenset(), FLOOR, said=True) != taxonomy.SAFE_HARBOR_AGES:
                continue
            if taxonomy.safe_harbor_reach(cells, comma, frozenset(), FLOOR, said=taxonomy.named_as_an_age(name)) == "":
                moved += [f"{table.name}.{name}"]
    value["zoo_columns_set_out"] = len(moved)
    lines += [f"R zoo columns set out of the reach: {moved}"]
    print(lines[-1], flush=True)


def _stand_ins(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """S: a held age column's twin cells whose number place writes a figure past 89 (the visit table beside its zero-padded copy, whose open question holds the ages whole, no person column, unanswered)."""
    header, rows = visit_table(1000, 20261111 + 1000)
    folder = scratch / "held"
    folder.mkdir(parents=True)
    source = folder / "held.csv"
    keep = [0, 1, 2, 3, 4, header.index("age_pad")]
    _write(source, [header[at] for at in keep], [[row[at] for at in keep] for row in rows])
    run = _run(folder, source, [], False)
    twin = run["twin"]
    assert isinstance(twin, list) and isinstance(run["blocks"], dict)
    past = 0
    for name in ("age", "age_text", "age_label"):
        role = run["blocks"].get(name, {}).get("role")
        if role != taxonomy.ROLE_IDENTIFIER or not twin:
            lines += [f"S {name}: {role}, not held"]
            continue
        at = twin[0].index(name)
        found = sum(1 for row in twin[1:] if any(90 < int(run_) < 1000 for run_ in re.findall(r"\d+", row[at])))
        past += found
        lines += [f"S {name}: held; {found} twin cells with a figure from 91 to 999; first cells {[row[at] for row in twin[1:6]]}"]
    value["held_stand_ins_past_89"] = past
    lines += [f"S held age columns' twin cells with a figure from 91 to 999: {past} (lane HB3-b-b, by the size valve)"]
    print(lines[-1], flush=True)
    shutil.rmtree(folder, ignore_errors=True)


value: "dict[str, object]" = {
    "spellings": 0, "spellings_held": 0, "parity_gaps": 0, "capped_held": 0, "c5_groups_below_floor": 0,
    "published_below_floor": 0, "ages_past_89_shown": 0, "ages_past_89_written": 0, "unit_columns_set_out": 0,
    "ages_set_out": 0, "zoo_columns_set_out": 0, "held_stand_ins_past_89": 0, "legs_validate_not_0": 0,
    "counters_blind": 0,
}
lines: "list[str]" = []
# `--only two-units,observations` runs the named legs alone and emits nothing
# (a reviewer's check of one leg on another tree; the KPI is the whole run).
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv[:-1] else []
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    blind = _counters_blind()
    value["counters_blind"] = len(blind)
    lines += [f"counters blind: {blind}"]
    if ONLY:
        for leg in ONLY:
            {"two-units": _two_units, "observations": _observations, "units": _units, "stand-ins": _stand_ins}[leg](
                scratch, value, lines)
        print(json.dumps(value, sort_keys=True), flush=True)
    else:
        _legs(scratch, value, lines)
        _observations(scratch, value, lines)
        _units(scratch, value, lines)
        _stand_ins(scratch, value, lines)
if not ONLY:
    ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_ages_widened-items.txt"
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    ITEMS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    kpi_rules.emit("K-HZ-36", value, f"{len(lines)} legs at 20,000 and 200,000 rows (1,000 and 10,000 people of 20 visits)")
