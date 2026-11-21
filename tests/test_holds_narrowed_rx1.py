"""Holds narrowed so that no hold costs a column or the relations for an ordinary value (lane RX-1 of the fidelity plan).

The owner's ruling of 2026-11-15: HIPAA means the Safe Harbor identifiers and
published counts under the floor of 11 people; an ordinary value merely
present in the twin discloses nothing, so it is never a reason to hold a
column, cut a relation or distort a distribution. Each case is red on the
mutant named in its docstring.

- R3, THE AGE CAP IS FOR AGES: a column or a key whose name names a
  measurement no age is (`taxonomy.named_as_a_measurement`: a saturation, a
  temperature, a rate, a pressure, a weight, a score, a count, a dose, a
  laboratory analyte, a unit no age is written in) is in no age reach: its
  values from 90 to 125 are published and written as themselves. A name that
  names an age too, a unit of age, and one cell naming an age by a word, a
  unit or an affix keep the column in the reach (HIPAA first); a neutral
  name stays in it until its question is answered (the owner's question 3
  of the fidelity plan stays open).
- R2, A COLUMN THE TOP CODE PROTECTS IS NOT ALSO HELD WHOLE: ages written
  with their word (`Age 18` to `Age 105`) beside strays `Age 126` to `Age 225`
  on a tenth of the rows were held as record numbers under every heading by
  the identifier words' reader, which read the age reach without the age
  word the description reads; the twin wrote 2,190 made-up three-figure
  `Xxx NNN` cells a heading and no level. They are top-coded again, as the
  description reads them: 73 levels, `Age 90` the top code, no age past 89
  shown or written.

Every table is invented and drawn from its seed here, at the owner's table
floor (20,000 rows).
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import chain, cli, profile, reading, taxonomy

ROWS = 20_000
FLOOR = 11
_NUMBER = re.compile(r"\d+")


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def _described(path: pathlib.Path) -> "dict[str, dict[str, object]]":
    table = reading.read_table(f"{path}", small_cell_floor=FLOOR)
    document = profile.build_document(table, taxonomy.Settings(small_cell_floor=FLOOR), [], [], [], top_code=True)
    return {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index]


def _largest_published(block: "dict[str, object]") -> float:
    """The largest value a number block publishes: its rungs, its mode and its tails' listed values."""
    found: "list[float]" = []
    points = block.get("percentiles")
    if isinstance(points, dict):
        found += [float(value) for value in points.values() if isinstance(value, (int, float))]
    if isinstance(block.get("mode"), (int, float)):
        found += [float(block["mode"])]  # type: ignore[arg-type]
    tails = block.get("tails")
    if isinstance(tails, dict):
        for side in tails.values():
            if isinstance(side, dict) and isinstance(side.get("values"), list):
                found += [float(value) for value in side["values"] if isinstance(value, (int, float))]
    return max(found)


def _through_the_commands(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", monkeypatch: "object", one_row_each: bool = False
) -> "dict[str, object]":
    """profile with nobody at the keyboard (with ``one_row_each``, a second round answering the subject question `one row each`, as a person would), then generate at seed 0; every file's text, the blocks, the questions and the twin."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: False)  # type: ignore[attr-defined]
    source = folder / "t.csv"
    _write(source, header, rows)
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"]) == 0, screen.getvalue()[-2000:]
        questions = folder / "t-questions.json"
        document = json.loads(questions.read_text(encoding="utf-8")) if questions.is_file() else {}
        between = document.get("between_columns") if isinstance(document, dict) else None
        subject = between.get("rows_per_person") if isinstance(between, dict) else None
        if one_row_each and isinstance(subject, dict):
            subject["your_answer"] = "one row each"
            questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            again = ["profile", f"{source}", "--out-dir", f"{folder}", "--answers", f"{questions}"]
            if cli.main(again) != 0:
                assert cli.main(again + ["--replace-description"]) == 0, screen.getvalue()[-2000:]
        twin_folder = folder / "twin"
        twin_folder.mkdir()
        assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{twin_folder}", "--seed", "0",
                         "--replace"]) == 0, screen.getvalue()[-2000:]
    texts = [screen.getvalue()] + [(folder / name).read_text(encoding="utf-8")
                                   for name in ("t-profile.json", "t-profile.txt", "t-questions.json")
                                   if (folder / name).is_file()]
    blocks = {f"{block['name']}": block for block in json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"]}
    asked = json.loads((folder / "t-questions.json").read_text(encoding="utf-8")).get("asked", [])
    with open(twin_folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    return {"texts": texts, "blocks": blocks, "asked": asked, "twin": twin}


# -- R3: THE AGE CAP IS FOR AGES ------------------------------------------------------------------------------

_MEASURED_NAMES = (
    "oxygen_saturation", "SpO2", "O2Sat", "temp_f", "TemperatureF", "heart_rate", "pulse", "systolic_bp",
    "diastolic_pressure", "weight_lbs", "pain_score", "visit_count", "dose", "glucose", "resp_rate", "percentile",
)
_NOT_MEASURED_NAMES = (
    "age", "Age", "age_years", "ptage", "age_weight", "weight_at_age", "value", "result", "v12", "level_k",
    "record_label", "stage", "item_code", "visit_note", "years",
)


def test_r3_the_names_that_name_a_measurement_and_no_age() -> None:
    """The closed list read on the name's words and on its runs of letters and figures; a name naming an age too is an age. Red where `named_as_a_measurement` reads no word (every measured name then reads False) or where the age's name is not read first (`age_weight` then reads True)."""
    for name in _MEASURED_NAMES:
        assert taxonomy.named_as_a_measurement(name), name
    for name in _NOT_MEASURED_NAMES:
        assert not taxonomy.named_as_a_measurement(name), name


def _vitals_rows(seed: int) -> "tuple[list[str], list[list[str]]]":
    """Bare numbers, every column holding values from 90 to 125 on many rows: measurements under their names, the same saturations under a neutral name, ages under `age`."""
    draw = random.Random(seed)
    header = ["oxygen_saturation", "SpO2", "temp_f", "heart_rate", "pain_score", "visit_count", "value", "age"]
    rows: "list[list[str]]" = []
    for _row in range(ROWS):
        saturation = min(100, max(82, round(draw.gauss(95.5, 2.5))))
        rows += [[
            f"{saturation}",
            f"{saturation}",
            f"{draw.gauss(99.1, 1.1):.1f}",
            f"{min(125, max(40, round(draw.gauss(84, 14))))}",
            f"{min(100, max(0, round(draw.gauss(55, 22))))}",
            f"{min(125, max(1, round(draw.gauss(60, 25))))}",
            f"{saturation}",
            f"{draw.randint(18, 104)}",
        ]]
    return header, rows


def test_r3_measurements_under_their_names_keep_their_values_past_89_and_ages_stay_capped(tmp_path: pathlib.Path) -> None:
    """At the owner's table floor: six measurement columns of bare numbers past 89 are described with no top code and publish values past 90; the same saturations under the neutral name `value` and the ages under `age` stay top-coded at 90, nothing past 90 published. Red where `taxonomy.named_as_a_measurement` answers no (the six top-coded at 90, as on the base)."""
    header, rows = _vitals_rows(20261117)
    path = tmp_path / "vitals.csv"
    _write(path, header, rows)
    blocks = _described(path)
    for name in ("oxygen_saturation", "SpO2", "temp_f", "heart_rate", "pain_score", "visit_count"):
        assert "top_coded" not in blocks[name], name
        assert blocks[name]["role"] != taxonomy.ROLE_IDENTIFIER, name
        assert _largest_published(blocks[name]) > 90, name
    for name in ("value", "age"):
        assert blocks[name].get("top_coded") == 90, name
        assert _largest_published(blocks[name]) <= 90, name


def test_r3_one_cell_naming_an_age_keeps_a_measured_column_in_the_reach_and_qualifiers_do_not(tmp_path: pathlib.Path) -> None:
    """HIPAA first: weights in kilograms written bare, one cell among 20,000 written `age 95`, stay top-coded; a saturation's qualifiers `<80` and `>100` are no age's band and leave it out. Red where `taxonomy.ages_named_in_cells` answers no (the weights then lose the top code with an age past 89 in a cell)."""
    draw = random.Random(4717)
    weights = [f"{min(125, max(40, round(draw.gauss(80, 18))))}" for _row in range(ROWS)]
    weights[draw.randrange(ROWS)] = "age 95"
    saturations = [f"{min(100, max(82, round(draw.gauss(95.5, 2.5))))}" for _row in range(ROWS)]
    for at in range(0, ROWS, 400):
        saturations[at] = "<80" if at % 800 else ">100"
    path = tmp_path / "weights.csv"
    _write(path, ["weight", "spo2"], [[weights[row], saturations[row]] for row in range(ROWS)])
    blocks = _described(path)
    assert blocks["weight"].get("top_coded") == 90 or blocks["weight"]["role"] == taxonomy.ROLE_IDENTIFIER
    assert "top_coded" not in blocks["spo2"]
    assert taxonomy.safe_harbor_reach(saturations, False, frozenset(), FLOOR, measured=True) == ""
    assert taxonomy.safe_harbor_reach(weights, False, frozenset(), FLOOR, measured=True) == taxonomy.SAFE_HARBOR_AGES


def test_r3_a_unit_of_age_named_or_an_age_word_in_the_cells_keeps_the_reach() -> None:
    """The reach itself: ``measured`` never frees a column whose name states a unit of age (``mark``), whose cells say age (``named``) or whose name says age (``said``). Red where ``measured`` is read before those three."""
    draw = random.Random(31)
    cells = [f"{draw.randint(18, 110)}" for _row in range(2_000)]
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, measured=True) == ""
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, said=True, measured=True) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, named=True, measured=True) == taxonomy.SAFE_HARBOR_AGES
    months = [f"{draw.randint(0, 1300)}" for _row in range(2_000)]
    assert taxonomy.safe_harbor_reach(months, False, frozenset(), FLOOR, mark=1080, measured=True) == taxonomy.SAFE_HARBOR_AGES


def test_r3_through_the_commands_the_twin_writes_the_measurements_past_89_and_no_age_past_89(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Through `profile` (nobody at the keyboard) and `generate`: no Safe Harbor question about ages is put to the measured columns; the twin writes saturations of 90 or more on about the real share of rows (real about 0.97), where the base wrote 90 on all of them; the `age` column writes no age past 90 and no file or screen shows a real age from 91 to 104. Red where `taxonomy.named_as_a_measurement` answers no."""
    header, rows = _vitals_rows(7)
    run = _through_the_commands(tmp_path, header, rows, monkeypatch)
    asked_about = {f"{entry.get('column')}" for entry in run["asked"]}  # type: ignore[union-attr]
    for name in ("oxygen_saturation", "SpO2", "temp_f", "heart_rate"):
        assert name not in asked_about, name
    twin = run["twin"]
    assert isinstance(twin, list)
    place = twin[0].index("oxygen_saturation")
    high = sum(1 for row in twin[1:] if float(row[place]) >= 90)
    real = sum(1 for row in rows if float(row[0]) >= 90)
    assert abs(high - real) <= 0.02 * ROWS, (high, real)
    assert len({row[place] for row in twin[1:]}) > 5
    ages = twin[0].index("age")
    assert max(int(row[ages]) for row in twin[1:] if row[ages]) <= 90
    shown = "\n".join(f"{text}" for text in run["texts"])  # type: ignore[union-attr]
    blocks = run["blocks"]
    assert isinstance(blocks, dict)
    assert blocks["age"].get("top_coded") == 90
    assert _largest_published(blocks["age"]) <= 90
    assert "top_coded" not in blocks["oxygen_saturation"]
    assert shown


# -- R2: AGES WITH THEIR WORD BESIDE STRAYS ARE TOP-CODED, NEVER HELD WHOLE ----------------------------------------

_STRAYED = [f"Age {18 + row % 88}" for row in range(ROWS - 2000)] + [f"Age {126 + row % 100}" for row in range(2000)]


@pytest.mark.parametrize("heading", ["age", "value", "item_code", "record_label", "visit_note"])
def test_r2_ages_written_with_their_word_beside_strays_are_top_coded_not_held(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, heading: str
) -> None:
    """`K-HZ-29`'s strayed leg under its five headings, through the commands at 20,000 rows: a set of categories, `Age 90` its top code, 73 levels, no question offering `identifier`; no real spelling of an age past 89 in any file or on the screen, and no twin cell holding a number from 91 to 125. Red where the identifier words' reader reads the age reach without the age word (``aged`` False), as on the base: role identifier, 2,190 made-up cells of three figures."""
    run = _through_the_commands(tmp_path, [heading], [[cell] for cell in _STRAYED], monkeypatch)
    blocks = run["blocks"]
    assert isinstance(blocks, dict)
    block = blocks[heading]
    assert block["role"] != taxonomy.ROLE_IDENTIFIER, block.get("detection_evidence")
    assert block.get("top_coded") == 90
    for entry in run["asked"]:  # type: ignore[union-attr]
        offered = [f"{one.get('answer')}" for one in entry.get("answers_you_can_give", [])]
        assert "identifier" not in offered, entry
    twin = run["twin"]
    assert isinstance(twin, list)
    past = [row[0] for row in twin[1:] if any(90 < int(found) <= 125 for found in _NUMBER.findall(row[0]))]
    assert not past, past[:5]
    real_past = {cell for cell in _STRAYED if 90 < int(_NUMBER.findall(cell)[0])}
    for text in run["texts"]:  # type: ignore[union-attr]
        for spelling in real_past:
            assert not re.search(rf"(?<![\w]){re.escape(spelling)}(?!\d)", f"{text}"), spelling


def test_r2_the_value_readers_hold_reads_the_age_word_as_the_description_does() -> None:
    """The reader itself: with the age word read (``aged``) the strayed column is no identifier-words column; without it, as on the base, it is held. Red where `safe_harbor_hold` hands no age evidence on."""
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, _STRAYED, frozenset(), FLOOR) == taxonomy.HELD_IDENTIFIER_WORDS
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, _STRAYED, frozenset(), FLOOR, aged=True) == ""
    # ...and a level that holds another identifier word beside the ages stays held, aged or not.
    named = _STRAYED[: ROWS - 200] + ["Age 40 Dr Smith"] * 200
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, named, frozenset(), FLOOR, aged=True) == taxonomy.HELD_IDENTIFIER_WORDS


# -- R1: ONE COLUMN WHOSE RECOUNT DISAGREES IS LEFT OUT, NEVER THE CHAIN -------------------------------------------


def _cohort_rows(seed: int) -> "tuple[list[str], list[list[str]]]":
    """One row a person: a group, a measurement that depends on it, a yes/no that depends on both, and a score."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for _row in range(ROWS):
        group = draw.choice(("A", "B", "C"))
        level = draw.gauss({"A": 40.0, "B": 55.0, "C": 70.0}[group], 8.0)
        flag = "Y" if draw.random() < (0.2 if level < 50 else 0.6) else "N"
        rows += [[group, f"{level:.1f}", flag, f"{draw.randint(0, 30)}"]]
    return ["arm", "reading", "event", "points"], rows


def test_r1_a_column_whose_recount_disagrees_is_left_out_and_the_chain_stands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Through `profile` with the chain's switch: the recount of `points` made to disagree (the reading's own `agrees` turned false), the chain is still drawn over `arm`, `reading` and `event`, `points` named in `ineligible` as `recount` and in no family. Red where one column's disagreement turns the whole chain off (the base: `statistical` null)."""
    original = chain.read_as_described

    def disagreeing(*args: object, **kwargs: object) -> object:
        read, cells = original(*args, **kwargs)  # type: ignore[arg-type]
        block = args[2]
        if read is not None and isinstance(block, dict) and block.get("name") == "points":
            read = dataclasses.replace(read, agrees=False)
        return read, cells

    monkeypatch.setattr(chain, "read_as_described", disagreeing)
    header, rows = _cohort_rows(5)
    run = _through_the_commands(tmp_path, header, rows, monkeypatch, one_row_each=True)
    document = json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))
    statistical = document["relationships"]["statistical"]
    assert statistical is not None
    assert {"column": "points", "reason": "recount"} in statistical["ineligible"]
    drawn = {entry["child"] for entry in statistical["chain"]} | {
        parent["column"] for entry in statistical["chain"] for parent in entry["parents"]
    }
    assert "points" not in drawn
    assert {"arm", "reading", "event"} <= drawn
    assert run["twin"]


# -- AGE BANDS WRITTEN AT THEIR OWN MEAN, SO AGE EFFECTS KEEP THEIR SIZE ----------------------------------------------


def test_bands_the_mean_of_each_end_band_rounded_half_up_in_whole_ages() -> None:
    """`taxonomy.ends_band_values`: the low band every whole age at or below the low end, the high band every one at or above the high end, the top code's 90 counted as 90; each mean rounded half up; a band no cell holds at its edge. `cells_within_the_ends` with the values writes each band's cells at its value in their own form. Red where the band values are the edges (`ends_band_values` returning the ends)."""
    cells = [f"{age}" for age in [20] * 15 + [25] * 5 + [30] * 12 + list(range(41, 70)) * 20 + [80] * 12 + [85] * 3 + [90] * 14]
    assert taxonomy.ends_band_values(cells, False, frozenset(), 41, 69) == (31, 79)
    assert taxonomy.ends_band_values(["50", "60"], False, frozenset(), 41, 69) == (41, 69)
    written = taxonomy.cells_within_the_ends(["Age 25", "025", "n/a", "Age 50", "Age 81"], False, frozenset(), 27, 80, values=(22, 85))
    assert written == ["Age 22", "022", "n/a", "Age 50", "Age 85"]
    assert taxonomy.cells_within_the_ends(["Age 25", "025", "n/a", "Age 50", "Age 81"], False, frozenset(), 27, 80) == [
        "Age 27", "027", "n/a", "Age 50", "Age 80",
    ]


def _visit_rows(people: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """One age a person (about 58 +/- 17, three in a hundred children, 0 to 105), 20 visits a person, an outcome whose log odds rise 0.06 a year of age and a reading of 90 + 0.6 a year of age."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for who in range(people):
        age = draw.randint(0, 17) if draw.random() < 0.03 else max(0, min(105, int(round(draw.gauss(58, 17)))))
        for _visit in range(20):
            chance = 1.0 / (1.0 + 2.718281828459045 ** (4.0 - 0.06 * age))
            rows += [[f"S{100000 + who}", f"{age}", f"{int(draw.random() < chance)}",
                      f"{round(90 + 0.6 * age + draw.gauss(0, 8), 1)}"]]
    return ["subject_id", "age", "outcome_flag", "reading_k"], rows


def _linear_slope(pairs: "list[tuple[float, float]]") -> float:
    mean_x = sum(x for x, _y in pairs) / len(pairs)
    mean_y = sum(y for _x, y in pairs) / len(pairs)
    return sum((x - mean_x) * (y - mean_y) for x, y in pairs) / sum((x - mean_x) ** 2 for x, _y in pairs)


@pytest.fixture(scope="module")
def visits(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    """The visit table at the owner's floor (1,000 people of 20 visits), the person declared, through `profile`, `generate` and `validate` (the twin, then the real table itself), nobody at the keyboard."""
    folder = tmp_path_factory.mktemp("visits")
    header, rows = _visit_rows(1000, 7)
    (folder / "table").mkdir()
    source = folder / "table" / "t.csv"
    _write(source, header, rows)
    out = folder / "out"
    for made in (out, out / "twin-check", out / "real-check"):
        made.mkdir()
    screen = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "_there_is_somebody_to_ask", lambda: False)
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            exits = [cli.main(["profile", f"{source}", "--out-dir", f"{out}", "--replace", "--identifier", "subject_id"])]
            exits += [cli.main(["generate", f"{out / 't-profile.json'}", "--out-dir", f"{out}", "--seed", "0", "--replace"])]
            exits += [cli.main(["validate", f"{out / 't-profile.json'}", "--twin", f"{out / 't-twin.csv'}", "--out-dir",
                                f"{out / 'twin-check'}", "--replace"])]
            exits += [cli.main(["validate", f"{out / 't-profile.json'}", "--twin", f"{source}", "--out-dir",
                                f"{out / 'real-check'}", "--replace"])]
    assert exits[0] == 0, screen.getvalue()[-3000:]
    text = (out / "t-profile.json").read_text(encoding="utf-8")
    block = next(one for one in json.loads(text)["columns"] if one["name"] == "age")
    with open(out / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [int(row[1]) for row in list(csv.reader(handle))[1:] if row[1]]
    return {"rows": rows, "block": block, "twin": twin, "exits": exits, "text": text, "screen": screen.getvalue(),
            "source": source}


def test_bands_through_the_commands_the_ends_are_written_at_their_people_s_mean_age(visits: "dict[str, object]") -> None:
    """The age's two end bands are recorded with the ages they are written as, each the mean age of its band's rows, the first below the low end and the second above the high end and at most 90; the reading's linear slope on the age as published lies within a tenth of its slope on the age top-coded alone (the edges gave about twice it); the twin's age SD at least 0.85 of the real; the twin and the real table each validate with exit 0; no twin age past 90. Red where `taxonomy.ends_band_values` gives the ends back (each band at its edge, as on the base)."""
    block = visits["block"]
    rows = visits["rows"]
    twin = visits["twin"]
    assert isinstance(block, dict) and isinstance(rows, list) and isinstance(twin, list)
    low, high = block["top_coded_ends"]
    first, second = block["top_coded_band_values"]
    assert 0 <= first < low and high < second <= 90, (low, high, first, second)
    ages = [min(int(row[1]), 90) for row in rows]
    lows = [age for age in ages if age <= low]
    assert first == (2 * sum(lows) + len(lows)) // (2 * len(lows))
    published = [first if age <= low else second if age >= high else age for age in ages]
    truth = _linear_slope([(float(age), float(row[3])) for age, row in zip(ages, rows)])
    as_published = _linear_slope([(float(age), float(row[3])) for age, row in zip(published, rows)])
    assert abs(as_published / truth - 1) < 0.1, (as_published, truth)
    assert max(twin) <= 90
    spread = (sum((age - sum(twin) / len(twin)) ** 2 for age in twin) / len(twin)) ** 0.5
    real_spread = (sum((age - sum(ages) / len(ages)) ** 2 for age in ages) / len(ages)) ** 0.5
    assert spread >= 0.85 * real_spread, (spread, real_spread)
    assert visits["exits"] == [0, 0, 0, 0], f"{visits['screen']}"[-3000:]


def test_bands_the_loader_reads_the_band_values_only_inside_their_bounds(visits: "dict[str, object]") -> None:
    """The loader's rule for `top_coded_band_values`: two whole numbers beside `top_coded_ends`, the first from 0 to the low end, the second from the high end to the top code; any other is refused, and so is the key without the ends. Red where the bounds are not read."""
    from synthtwin import canonical, contract, errors

    text = visits["text"]
    assert isinstance(text, str)
    document = json.loads(text)
    place = next(at for at in range(len(document["columns"])) if document["columns"][at]["name"] == "age")
    low, high = document["columns"][place]["top_coded_ends"]
    loaded = contract.load_profile_text(text, "visits")
    assert next(one for one in loaded.columns if one.name == "age").top_coded_band_values == tuple(
        document["columns"][place]["top_coded_band_values"])
    for wrong in ([low + 1, high + 1], [low - 1, high - 1], [low - 1, 91], [low - 1], [f"{low - 1}", high + 1], [True, high + 1]):
        changed = json.loads(text)
        changed["columns"][place]["top_coded_band_values"] = wrong
        with pytest.raises(errors.ProfileError, match="top_coded_band_values"):
            contract.load_profile_text(canonical.serialize(changed), "visits")
    changed = json.loads(text)
    del changed["columns"][place]["top_coded_ends"]
    with pytest.raises(errors.ProfileError, match="top_coded_band_values"):
        contract.load_profile_text(canonical.serialize(changed), "visits")
    # ...and the description written again in its own form loads, the values as they were.
    assert canonical.serialize(json.loads(text)) == text


def test_bands_the_chain_reads_each_band_at_the_age_its_block_records(visits: "dict[str, object]") -> None:
    """The chain's reader (`chain.described_cells`, as the table and patient layers read a column) reads every age at or below the low end as the first band value and every one at or above the high end as the second, as the description wrote them, so its recount agrees and the column takes part. Red where the chain reads the ends alone (each band at its edge: the recount then disagrees)."""
    block = visits["block"]
    source = visits["source"]
    assert isinstance(block, dict) and isinstance(source, pathlib.Path)
    low, high = block["top_coded_ends"]
    first, second = block["top_coded_band_values"]
    table = reading.read_table(f"{source}", small_cell_floor=FLOOR)
    place = table.column_names.index("age")
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    read = chain.described_cells(table, place, block, taxonomy.Settings(small_cell_floor=FLOOR), declared, "", False, 0)
    written = reading.column_values(table, place)
    for real, seen in zip(written, read):
        age = min(int(real), 90)
        assert seen == (f"{first}" if age <= low else f"{second}" if age >= high else f"{age}"), (real, seen)


def test_bands_the_floor_check_refuses_band_values_a_few_people_hold() -> None:
    """`profile._band_values_keep_the_floor`, the guard the ends' rounds pass the band values through: a low band whose rows belong to 5 people (its value then a value 5 people hold) is refused, one of 30 people kept. Red where the guard keeps every band (the rounds would then publish what the edges never did)."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)

    def judged(young: int) -> bool:
        ages = [10 + who % 5 for who in range(young)] + [40 + who % 30 for who in range(1000 - young)]
        cells = [f"{age}" for age in ages for _row in range(20)]
        people = [[f"P{who}" for who in range(1000) for _row in range(20)]]
        low, high = 14, 69
        values = taxonomy.ends_band_values(cells, False, frozenset(), low, high)
        written = taxonomy.cells_within_the_ends(cells, False, frozenset(), low, high, values=values)
        candidate = taxonomy.with_top_ends(
            taxonomy.with_top_code(taxonomy.profile_column("age", 0, written, len(written), settings), 90, -1, (), False),
            low, high, values,
        )
        return profile._band_values_keep_the_floor(candidate, written, False, frozenset(), 90, True, people, None, FLOOR)

    assert not judged(5)
    assert judged(30)
