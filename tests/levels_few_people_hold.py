"""Levels few people hold: an invented form and K-HZ-19's reading of it (lane PL, plan P4-D453).

On a table of several rows a person, a level one to ten people hold on eleven
rows or more used to cost the whole code or flag column (P4-D406). This form
holds the shapes that decided it, each under a generic name, built at run time
from a seed:

- codes with a rare level, answered `code` by the person (`rare_code`,
  `rare_far_code`, `rare_nought_code`, `rare_word_code`, `rare_dotted_code`, whose
  stand-ins wear the form of its levels);
- a code that stays with a person, a few whole numbers read as a count and put
  the Safe Harbor question (`code_per_person`);
- flags (`flag_yes_no`, `flag_words`, `flag_digits`), one rare value each;
- columns too few people fill (`thin_digit`, `thin_word`), the second of words,
  which its twin keeps a column of words;
- a code with no rare level beside them (`common_code`);
- identifier-shaped columns many people share (`plan_number`,
  `account_number`, `full_name`, `street_address`, `person_dob`), never turned
  into levels whatever their sharing.

`measure` is K-HZ-19's reading of one run, every count linear in the cells:
the real values of a column are held in a set, each twin cell read once.
Shared by the gate (`tests/test_levels_few_people_hold.py`) and K-HZ-19's
driver (`tools/measurements/kpi_levels_few_people_hold.py`).
"""

from __future__ import annotations

import json
import pathlib
import random

import health_zoo
from health_zoo import Table, csv_bytes

ROWS_A_PERSON = 4
FAR_LEVEL = "4417"
WORD_LEVEL = "QXR7"
# Each column the rule reaches, its levels few people hold and whether it is a
# flag, whose blank share is read too.
CODES = (
    "rare_code", "rare_far_code", "rare_nought_code", "rare_word_code", "rare_dotted_code", "code_per_person", "common_code",
)
FLAGS = ("flag_yes_no", "flag_words", "flag_digits")
THIN = ("thin_digit", "thin_word")
IDENTIFYING = ("plan_number", "account_number", "full_name", "street_address", "person_dob")
SEED = 20261101


def _people(n: int) -> "list[str]":
    people = max(n // ROWS_A_PERSON, 1)
    return [f"{1_000_000 + (row * 7_919) % people:07d}" for row in range(n)]


def person_held(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """The form: `n` rows of about ROWS_A_PERSON a person."""
    draw = random.Random(seed)
    people = _people(n)
    everyone = sorted(set(people))

    def few(size: int) -> "set[str]":
        return set(draw.sample(everyone, min(size, len(everyone))))

    def zipf(levels: "list[str]") -> str:
        return draw.choices(levels, [1 / (place + 1) for place in range(len(levels))])[0]

    five = list("12345")
    noughts = [f"0{k}" for k in range(1, 6)]
    words = ["ALPHA", "BRAVO", "DELTA", "GAMMA"]
    per_person = {person: str(draw.choices(range(1, 31), [1 / k for k in range(1, 31)])[0]) for person in everyone}
    per_person.update({person: "100" for person in everyone[:3]})
    per_person.update({person: "101" for person in everyone[3:9]})
    # Twelve to a value: each many people share, as a plan or a surname is.
    plan = {person: f"HPX{100_000_000 + draw.randrange(max(len(everyone) // 12, 1)):09d}" for person in everyone}
    account = {person: f"ACC{10_000_000 + draw.randrange(max(len(everyone) // 12, 1)):08d}" for person in everyone}
    surname = {person: f"Surname{draw.randrange(max(len(everyone) // 12, 1))} Given" for person in everyone}
    street = {person: f"{1 + draw.randrange(max(len(everyone) // 12, 1))} Oak Street" for person in everyone}
    born = {person: f"19{draw.randrange(40, 99)}-{1 + draw.randrange(12):02d}-{1 + draw.randrange(28):02d}" for person in everyone}
    rare, far, nought, word, dotted = few(5), few(6), few(5), few(4), few(7)
    registers = [f"{letter}{10 + place}.{place}" for place, letter in enumerate("BCDEFGHJ")]
    flag, alert, digit = few(8), few(5), few(8)
    thin_a, thin_b = few(5), few(7)
    header = ["record_key", "patient_key", *CODES[:5], "code_per_person", *FLAGS, *THIN, "common_code", *IDENTIFYING]
    rows: "list[list[str]]" = []
    for row, person in enumerate(people):
        rows += [[
            str(810_000 + row), person,
            "6" if person in rare else zipf(five),
            FAR_LEVEL if person in far else zipf(five),
            "09" if person in nought else zipf(noughts),
            WORD_LEVEL if person in word else zipf(words),
            "Q99.1" if person in dotted else zipf(registers),
            per_person[person],
            "Y" if person in flag else "" if draw.random() < 0.1 else "N",
            "Yes" if person in alert else "No",
            "1" if person in digit else "0",
            "1" if person in thin_a else "",
            "Y" if person in thin_b else "",
            zipf(five),
            plan[person], account[person], surname[person], street[person], born[person],
        ]]
    return header, rows


def table() -> Table:
    header, _rows = person_held(3, 0)
    knows = {"record_key": "identifier", "patient_key": "identifier"}
    for name in CODES:
        knows[name] = "code"
    for name in IDENTIFYING:
        knows[name] = "identifier"
    return Table(
        "levels_few_people_hold", ".csv", person_held,
        lambda head, rows: csv_bytes(head, rows),
        {"levels_few_people_hold": tuple(header)},
        knows,
        health_zoo._csv_reader(),
        (),
        person="patient_key",
    )


def _blocks(folder: pathlib.Path, stem: str) -> "dict[str, dict]":
    described = json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))
    return {f"{block['name']}": block for block in described["columns"]}


def _few_held(header: "list[str]", rows: "list[list[str]]") -> "dict[str, dict[str, tuple[int, int]]]":
    """Per column, each level with its people and rows, where one to ten people hold it."""
    person = header.index("patient_key")
    found: "dict[str, dict[str, tuple[int, int]]]" = {}
    for place, name in enumerate(header):
        holders: "dict[str, set[str]]" = {}
        counts: "dict[str, int]" = {}
        for row in rows:
            cell = row[place]
            if cell:
                holders.setdefault(cell, set()).add(row[person])
                counts[cell] = counts.get(cell, 0) + 1
        found[name] = {cell: (len(holders[cell]), counts[cell]) for cell in holders if len(holders[cell]) <= 10}
    return found


def _all_words(folder: pathlib.Path) -> "set[str]":
    """Every word of every file a run leaves but the source and the twin, each read once."""
    words: "set[str]" = set()
    for path in sorted(folder.iterdir()):
        if path.suffix in (".json", ".txt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            word = ""
            for character in text:
                if character.isalnum():
                    word += character
                elif word:
                    words.add(word)
                    word = ""
    return words


def measure(n: int, seed: int, folder: pathlib.Path) -> "dict[str, object]":
    """K-HZ-19's counts on one run of the form at `n` rows, its files in `folder`."""
    import pandas

    form = table()
    result = health_zoo.run_table(form, folder, n, seed, small_tables_refused=n >= health_zoo.KPI_ROWS)
    stem = form.name
    header, rows = person_held(n, seed)
    few = _few_held(header, rows)
    blocks = _blocks(folder, stem)
    real = pandas.read_csv(folder / f"{stem}.csv", dtype=str, keep_default_na=False)
    twin = pandas.read_csv(folder / f"{stem}-twin.csv", dtype=str, keep_default_na=False)
    real_typed = pandas.read_csv(folder / f"{stem}.csv", low_memory=False)
    twin_typed = pandas.read_csv(folder / f"{stem}-twin.csv", low_memory=False)
    found: "dict[str, object]" = {
        "levels_shown": 0, "counts_named": 0, "kept_filter_faults": 0, "flag_blank_share_faults": 0,
        "dtype_mismatches": 0, "stand_ins_equal_a_real_value": 0, "thin_words_read_as_numbers": 0,
        "identifying_levels_published": 0, "validate_exit": result["steps"].get("validate", {}).get("exit"),
        "kept_share_gap_max": 0.0, "isin_gap_max": 0.0, "blank_share_gap_max": 0.0, "pool_share_gap_max": 0.0,
    }
    means: "dict[str, list[float]]" = {}
    held: "list[str]" = []
    stand_in_cells = 0
    words = _all_words(folder)
    for token in (FAR_LEVEL, WORD_LEVEL):
        if token in words:
            found["levels_shown"] = int(found["levels_shown"]) + 1  # type: ignore[call-overload]
    for name in [*CODES, *FLAGS, *THIN]:
        block = blocks[name]
        levels = block.get("levels", [])
        published = {f"{entry['label']}" for entry in levels}
        spelled = {spelling for entry in levels for spelling in entry["variants"]}
        rare = few[name]
        for level in rare:
            if level.casefold() in {label.casefold() for label in published} or level in spelled:
                found["levels_shown"] = int(found["levels_shown"]) + 1  # type: ignore[call-overload]
        if f"{block['role']}" == "identifier":
            held += [f"{name}: read as record numbers, {block['detection_evidence'][:60]}"]
        real_values = set(real[name].tolist()) - {""}
        for cell in twin[name].tolist():
            if cell and cell not in spelled:
                stand_in_cells += 1
                if cell in real_values:
                    found["stand_ins_equal_a_real_value"] = int(found["stand_ins_equal_a_real_value"]) + 1  # type: ignore[call-overload]
        for spelling in spelled:
            gap = abs(float((real[name] == spelling).mean()) - float((twin[name] == spelling).mean()))
            found["kept_share_gap_max"] = max(float(found["kept_share_gap_max"]), round(gap, 4))  # type: ignore[arg-type]
            if gap > health_zoo.SHARE_TOLERANCE:
                found["kept_filter_faults"] = int(found["kept_filter_faults"]) + 1  # type: ignore[call-overload]
        if published and spelled:
            real_in = float(real[name].isin(sorted(spelled)).mean())
            twin_in = float(twin[name].isin(sorted(spelled)).mean())
            found["isin_gap_max"] = max(float(found["isin_gap_max"]), round(abs(real_in - twin_in), 4))  # type: ignore[arg-type]
            if abs(real_in - twin_in) > health_zoo.SHARE_TOLERANCE:
                found["kept_filter_faults"] = int(found["kept_filter_faults"]) + 1  # type: ignore[call-overload]
            # The pool's own share: the rows of no published spelling, blanks aside.
            real_pool = float(((~real[name].isin(sorted(spelled))) & (real[name] != "")).mean())
            twin_pool = float(((~twin[name].isin(sorted(spelled))) & (twin[name] != "")).mean())
            found["pool_share_gap_max"] = max(float(found["pool_share_gap_max"]), round(abs(real_pool - twin_pool), 4))  # type: ignore[arg-type]
        blank_gap = abs(float((real[name] == "").mean()) - float((twin[name] == "").mean()))
        if name not in THIN:
            found["blank_share_gap_max"] = max(float(found["blank_share_gap_max"]), round(blank_gap, 4))  # type: ignore[arg-type]
        if name in FLAGS and blank_gap > health_zoo.SHARE_TOLERANCE:
            found["flag_blank_share_faults"] = int(found["flag_blank_share_faults"]) + 1  # type: ignore[call-overload]
        if "pool_in_people" in block and f"{real_typed[name].dtype}" in ("int64", "float64"):
            # THE PRICE OF A NUMBER POOLED (the orchestrator's LANE PL RULINGS 2
            # (2)): the stand-in's value less the held one's, times the pool's
            # share, moves the mean; recorded apart, real and twin.
            means[name] = [round(float(real_typed[name].mean()), 4), round(float(twin_typed[name].mean()), 4)]
        real_type, twin_type = f"{real_typed[name].dtype}", f"{twin_typed[name].dtype}"
        if real_type != twin_type:
            if name in THIN and twin_type == "float64":
                found["thin_words_read_as_numbers"] = int(found["thin_words_read_as_numbers"]) + 1  # type: ignore[call-overload]
            else:
                found["dtype_mismatches"] = int(found["dtype_mismatches"]) + 1  # type: ignore[call-overload]
    # A COLUMN OF WORDS TOO FEW PEOPLE FILL STAYS TEXT (the orchestrator's LANE
    # PL RULINGS 1 (1)): `.str` runs on the twin, whose filled people are the
    # floor's number whatever the real holds (the twin's own people).
    try:
        twin_typed["thin_word"].str.len()
        runs = f"{real_typed['thin_word'].dtype}" == f"{twin_typed['thin_word'].dtype}"
    except AttributeError:
        runs = False
    found["thin_word_str_runs"] = int(runs)
    filled = twin["thin_word"] != ""
    found["thin_word_twin_cells"] = int(filled.sum())
    found["thin_word_twin_people"] = int(twin.loc[filled, "patient_key"].nunique())
    found["pooled_means"] = means
    for name in THIN:
        block = blocks[name]
        if block.get("n_present") != 0 or block.get("suppressed_rows", 0) != 0:
            found["counts_named"] = int(found["counts_named"]) + 1  # type: ignore[call-overload]
    for name in IDENTIFYING:
        if blocks[name].get("levels"):
            found["identifying_levels_published"] = int(found["identifying_levels_published"]) + 1  # type: ignore[call-overload]
    found["columns_still_held"] = held
    found["stand_in_cells"] = stand_in_cells
    found["validate_misses"] = len(result["misses"])
    # HIPAA FIRST: a real value of a column that names a person, in a file or in
    # the twin. A birth date stays under the date rules, not this lane's (P4-D417,
    # P4-D433): the start of a coarse bucket its description prints can equal a real
    # date, and a made-up date a real one by chance (the orchestrator's LANE ID-ROOM
    # RULINGS 1 (3), LANE HB RULINGS 2 (1)), each recorded apart and judged by K-HZ-07.
    entries = (result.get("leaks") or {}).values()
    found["leaks"] = sum(
        int(entry.get("description", 0)) + int(entry.get("twin", 0))
        for entry in entries
        if entry.get("column") != "person_dob"
    )
    found["birth_date_points_at_a_grain"] = max(
        (int(entry.get("description", 0)) for entry in entries if entry.get("column") == "person_dob"), default=0
    )
    found["birth_dates_equal_by_chance"] = max(
        (int(entry.get("twin", 0)) for entry in entries if entry.get("column") == "person_dob"), default=0
    )
    found["steps"] = {step: result["steps"][step]["exit"] for step in result["steps"]}
    found["rows_a_rare_level_holds"] = max((pair[1] for pair in few["rare_code"].values()), default=0)
    return found


# -- the legs beside the form (lane PL's repair 1) ------------------------------

# Columns whose values are identifiers by their shape, under names that say
# nothing (skeptic 1's item 1): given names, plan numbers, short street
# addresses, account numbers; each with a value three to five people hold.
NEUTRAL = {
    "first": ["Anna", "Ben", "Cara", "Dov", "Eli", "Fay", "Gus", "Hal"],
    "grp": [f"GRP-{1000 + 37 * k}" for k in range(8)],
    "line1": [f"{10 + k} Elm Street" for k in range(8)],
    "col_d": [f"AC{2000 + 41 * k}" for k in range(8)],
}
NEUTRAL_RARE = {"first": "Zebulon", "grp": "GRP-7731", "line1": "7 Birch Lane", "col_d": "AC9917"}


def _command(arguments: "list[str]", refused: bool) -> "tuple[int, str]":
    import contextlib
    import io

    from synthtwin import cli

    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(arguments, small_tables_refused=refused)
    return code, sink.getvalue()


def _words_of(folder: pathlib.Path, screen: str) -> str:
    text = screen
    for path in sorted(folder.iterdir()):
        if path.suffix in (".json", ".txt") and "twin" not in path.name:
            text += path.read_text(encoding="utf-8", errors="replace")
    return text


def neutral_identifiers(n: int, folder: pathlib.Path) -> "dict[str, int]":
    """Identifier-shaped columns under neutral names, profiled through the command and left unanswered.

    `spellings_published`: their real values in a description, a summary, a
    questions file or on the screen (target 0); `not_asked`: such a column
    held with no question put (target 0).
    """
    draw = random.Random(SEED)
    folder.mkdir(parents=True, exist_ok=True)
    people = _people(n)
    everyone = sorted(set(people))
    rare = {name: set(draw.sample(everyone, 3 + place % 3)) for place, name in enumerate(NEUTRAL)}
    chosen = {name: {person: draw.choice(NEUTRAL[name]) for person in everyone} for name in NEUTRAL}
    lines = [",".join(["patient_key", *NEUTRAL])]
    for person in people:
        lines += [",".join([person] + [NEUTRAL_RARE[name] if person in rare[name] else chosen[name][person] for name in NEUTRAL])]
    table = folder / "neutral.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    _code, screen = _command(["profile", f"{table}", "--replace", "--identifier", "patient_key"], n >= health_zoo.KPI_ROWS)
    text = _words_of(folder, screen)
    shown = sum(1 for name in NEUTRAL for value in [*NEUTRAL[name], NEUTRAL_RARE[name]] if value in text)
    asked: "set[str]" = set()
    questions = folder / "neutral-questions.json"
    if questions.exists():
        for entry in json.loads(questions.read_text(encoding="utf-8")).get("asked", []):
            if isinstance(entry, dict):
                asked.add(f"{entry.get('column', '')}")
    return {"spellings_published": shown, "not_asked": sum(1 for name in NEUTRAL if name not in asked)}


def rows_boundary(n: int, folder: pathlib.Path) -> "dict[str, int]":
    """One row a person: columns 10 and 11 rows fill, and a declared record number 5 rows fill.

    Profiled through the command at ``n`` rows. `faults`: the 10 not counted
    absent, the 11 not described with its count, the declared record number
    not counted absent (target 0); `counts_printed`: its 5 printed in any
    file or on the screen beside its name (target 0).
    """
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["key_col,rows_ten,rows_eleven,ref_col,full_col"]
    for row in range(n):
        lines += [f"{3_000_000 + row},{'A' if row < 10 else ''},{'B' if row < 11 else ''},{f'R{400_000 + row}' if row < 5 else ''},{'pqrs'[row % 4]}"]
    table = folder / "rows.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    _code, screen = _command(
        ["profile", f"{table}", "--replace", "--identifier", "key_col", "--identifier", "ref_col"], n >= health_zoo.KPI_ROWS
    )
    blocks = _blocks(folder, "rows")
    faults = 0
    faults += int(blocks["rows_ten"].get("present_count_withheld") is not True)
    faults += int(blocks["rows_eleven"].get("n_present") != 11)
    faults += int(blocks["ref_col"].get("present_count_withheld") is not True)
    said = json.dumps(blocks["ref_col"]) + "".join(line for line in screen.split("\n") if "ref_col" in line)
    printed = int('"n_present": 5' in said or " 5 " in said)
    return {"faults": faults, "counts_printed": printed}


def indicator_model(folder: pathlib.Path) -> "dict[str, float]":
    """A logistic model of the form's pooled 0/1 indicator, fitted on the twin (RULINGS 2 (2)).

    `refused` 1 where statsmodels cannot fit it (a value outside 0 and 1);
    `mean_gap` the twin's mean less the real's.
    """
    import pandas

    real = pandas.read_csv(folder / "levels_few_people_hold.csv", low_memory=False)
    twin = pandas.read_csv(folder / "levels_few_people_hold-twin.csv", low_memory=False)
    found = {"refused": 0.0, "mean_gap": round(abs(float(twin["flag_digits"].mean()) - float(real["flag_digits"].mean())), 4)}
    try:
        import statsmodels.api as sm

        sm.GLM(twin["flag_digits"], [1.0] * len(twin), family=sm.families.Binomial()).fit()
    except ImportError:
        found["refused"] = -1.0
    except Exception:  # noqa: BLE001 -- a model the twin cannot carry is the result
        found["refused"] = 1.0
    return found
