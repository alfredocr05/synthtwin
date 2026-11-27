"""K-HZ-37: values typed by a key, at 20,000 rows and 1,000 people (lane KV, plan P4-D487).

THE SIX INVENTED LONG FORMS of `tests/key_value_tables.py` (a vital-signs
export with word keys and with six-figure number keys, a question-and-answer
export, a lab export with a unit column, the zoo's own `values_typed_by_key`
kind, and a question-and-answer export whose answers include Safe Harbor
identifiers), each run end to end through the commands a person types (the
shipped table floor on): profile, the answers round by round, generate seed
0, validate. FOUR MODES (a run of U or Y whose value column is not keyed, its key
column held, is described and read but not generated: its value column is
held whole, as on the base, and its twin is the held writer's, lane
HB3-b's; see `run`): U nothing
answered; N answered as the holder would
(the person column `identifier`, the key `code` where its keys are codes, a
question offering `keep` and `identifier` on another column `keep`, the key
column's Safe Harbor question `no`, the value column's truthfully -- `yes`
where a key holds dates or identifiers -- and Q-KEYED `keyed`); Y as N with
the key column's question `yes`; M as N with the value column's `no` (a
careless or mistaken `no`). REPAIR 1'S RUNS (the orchestrator's LANE KV
RULINGS 3 and 4): a pool of ONE rare key held by four people on twelve rows,
every one a town (form sp, N and M); the identifier form with its question
keys written as codes and a key of family names alone (form qpc, the four
modes); rare keys whose cue word or name a character that prints nothing
breaks (form hf, N); the vital-signs form with the person column answered and
nothing else (P) and with every question answered but the person column's
(O, a question offering `identifier` open); the lab form with the value
column declared a measurement (D). REPAIR 2'S RUNS (the orchestrator's
LANE KV RULINGS 6): the coded identifier form with the value column's
careless `no` CORRECTED to `yes` in the answers file after its question
about values that read as dates was answered `no` (C), and with its Safe
Harbor question answered `no` and that question about dates `yes` (E):
ANY YES HOLDS. And the zoo's three key-value kinds through the zoo's own
`run_table`.

HIPAA FIRST, every count at most 0: real rare keys named in U, P, O or Y (a
whole string in a JSON file or a word of a text file the run wrote); a rare
key's name a screen reads (`profile.keyed_names_pass`'s screens, each alone,
each read as written and with what prints nothing set aside, a sentence
among them) among the names published; the name or the town of the pool of
one rare key of four people, published or written in any mode; a key block under a rare key; a published level of a key
block that 1 to 10 people hold (a top-coded block's top level held by the
people of every value from its mark, or, pooled below the mark, the level
it joined held by them too; a block published at a grain, whose levels
name buckets, counted apart); a twin cell equal to a value only rare keys
hold; on the identifier form, an identifier value (ZIP codes, cities,
contacts' names, telephones, dates of birth, record numbers) published or
written under U, N, P, O, D, C or E, and an age past 89 in any mode (read as K-HZ-20's
driver reads ages: a published value outside the count-like facts, or a
twin cell, past the mark of 90, the top category itself allowed); after the careless `no`
never more cities, names or ages past 89 than the column-wide reading
published (25, 30 and 6 on the planning's form; this form's own counts are
read on the base by step 0). FIDELITY: twin key cells off the real key list
after `no` (where the screens refused every name, P4-D487's limit (e),
recorded apart); per common key (`_key_bars`), a numeric key's twin cells
inside its own real 1st to 99th percentile at 0.95 of the real share, the
Kolmogorov-Smirnov distance at most twice the real table's own half-split
value, the twin's mean and standard deviation each within twice the mean
gap between the halves' over twenty random half-splits of its people, a
category key's total variation distance at most twice its half-split value
-- each counted over the keys whose block is described -- the number keys a
block holds or top-codes counted apart (owner KV-b), and every published
key's twin count exact. THE CONTROL, READ PER KEY AND PER BAR (the
statistics check's item 1): the same bars on the twin with its values drawn
apart from the key (its value column shuffled over its rows); a key whose
bar the control passes is VOID for that bar, counted apart, never as
passing, and a run's control passes the bars where it passes every bar of a
key on half its keys or more, which must be in no run. The bars' own case
(`self_check`): a constant inside the real range fails them. THE PRICE: CPU
seconds of each step, the questions Q-KEYED put. THE VALIDATOR: the runs
whose validate misses an obligation on the product's own twin (exit 3),
which must be none (the scoped verify of repair 1: a key block counted
absent was missed). A run that did not complete
stops the driver (`RunNotComplete`) and reads as no measurement.

    .venv/bin/python tools/measurements/kpi_key_value.py --kpi
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import key_value_tables  # noqa: E402
import kpi_rules  # noqa: E402

from synthtwin import asking, cli, parsing, profile, taxonomy  # noqa: E402

kpi_rules.guard_this_tree()

MODES = ("U", "N", "Y", "M")
ROUNDS_AT_MOST = 5
FLOOR = 11
csv.field_size_limit(10 ** 8)


class RunNotComplete(Exception):
    """A step of a run exited otherwise than 0 or 3, or wrote no file it owes."""


def _cpu() -> float:
    times = __import__("os").times()
    return times.user + times.system


def _step(arguments: "list[str]") -> "tuple[int, float]":
    sink = io.StringIO()
    started = _cpu()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(arguments, small_tables_refused=True)
    if code not in (0, 3):
        raise RunNotComplete(f"{arguments[0]} exited {code}: {sink.getvalue()[-400:]}")
    return int(code), _cpu() - started


def _entries(document: "dict") -> "list[dict]":
    found: "list[dict]" = []
    for section in ("about_your_file", "asked"):
        for entry in document.get(section) or []:
            if isinstance(entry, dict) and "answers_you_can_give" in entry:
                found += [entry]
    for entry in (document.get("checklist") or {}).get("columns") or []:
        if isinstance(entry, dict) and "answers_you_can_give" in entry:
            found += [entry]
    return found


def _answer(form: key_value_tables.Form, mode: str, entry: "dict") -> str:
    offered = [f"{choice['answer']}" for choice in entry["answers_you_can_give"]]
    column = f"{entry.get('column', '')}"
    harbor = sorted(answer for answer in offered if answer not in ("years", "months", "weeks", "days")) == ["no", "yes"]
    # MODE P: the person column answered and nothing else; MODE O: every
    # question answered as in N but the person column's, left open (a
    # question offering `identifier` open on the table: rule U (c)).
    if mode == "P":
        return "identifier" if column == form.person and "identifier" in offered else ""
    if mode == "O" and column == form.person:
        return ""
    if "keyed" in offered:
        return "keyed" if column == form.value else "keep"
    if column == form.person and "identifier" in offered:
        return "identifier"
    if column == form.key and harbor:
        return "yes" if mode == "Y" else "no"
    if column == form.value and harbor:
        # MODE E: the value column's Safe Harbor question `no`, its question
        # about values that read as dates `yes`; MODE C answers as M, and
        # `run` corrects the Safe Harbor `no` to `yes` afterwards.
        if mode == "E":
            return "yes" if asking.SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}" else "no"
        return "no" if mode in ("M", "C") else ("yes" if form.value_holds_dates else "no")
    if column == form.key and form.key_is_code and "code" in offered:
        return "code"
    if harbor and column == form.time:
        return "yes"
    if harbor:
        return "no"
    if "identifier" in offered and "keep" in offered and column:
        return "keep"
    return ""


def _corrected(form: key_value_tables.Form, questions: pathlib.Path, source: pathlib.Path) -> float:
    """MODE C: the value column's Safe Harbor `no` corrected to `yes` in the answers file, its question about values that read as dates left `no`, and the profile run again; the CPU seconds of that run."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    corrected = 0
    for section in ("answered_before", "asked"):
        for entry in document.get(section) or []:
            if not isinstance(entry, dict) or entry.get("column") != form.value or entry.get("your_answer") != "no":
                continue
            offered = sorted(f"{choice['answer']}" for choice in entry.get("answers_you_can_give") or [])
            harbor = [answer for answer in offered if answer not in ("years", "months", "weeks", "days")] == ["no", "yes"]
            if harbor and asking.SAFE_HARBOR_DATES_SEEN not in f"{entry.get('what_synthtwin_saw', '')}":
                entry["your_answer"] = "yes"
                corrected = corrected + 1
    if corrected != 1:
        raise RunNotComplete(f"{form.name} C: {corrected} Safe Harbor answers corrected, not one")
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    _code, spent = _step(["profile", f"{source}", "--replace", "--answers", f"{questions}"])
    return spent


def _round_key(entry: "dict", mode: str) -> "tuple[str, tuple[str, ...], bool]":
    """What makes a question the same question in a later round: its column and the answers it offers -- and, in modes C and E, whether it is the question about values that read as dates, which offers the Safe Harbor question's `no` and `yes` and follows it a round later (the other modes leave it open after the value column's `no`, as they did when they were stamped)."""
    offered = tuple(sorted(f"{choice['answer']}" for choice in entry["answers_you_can_give"]))
    dates = mode in ("C", "E") and asking.SAFE_HARBOR_DATES_SEEN in f"{entry.get('what_synthtwin_saw', '')}"
    return (f"{entry.get('column')}", offered, dates)


def run(folder: pathlib.Path, form: key_value_tables.Form, mode: str) -> "dict[str, object]":
    """One form in one mode through the commands; the files it wrote and the CPU seconds of each step."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / f"{form.name}.csv"
    source.write_text(key_value_tables.csv_text(form), encoding="utf-8", newline="\n")
    seconds: "dict[str, float]" = {}
    # MODE D: as N, the value column declared a measurement on every call.
    declared = ["--measurement", form.value] if mode == "D" else []
    _code, seconds["profile"] = _step(["profile", f"{source}", "--replace", *declared])
    questions = folder / f"{form.name}-questions.json"
    keyed_put = 0
    put: "set[tuple[str, tuple[str, ...], bool]]" = set()
    if mode != "U":
        rounds = 0.0
        for _round in range(ROUNDS_AT_MOST):
            document = json.loads(questions.read_text(encoding="utf-8"))
            entries = _entries(document)
            fresh = [entry for entry in entries if _round_key(entry, mode) not in put and not entry.get("your_answer")]
            if _round and not fresh:
                break
            for entry in entries:
                key = _round_key(entry, mode)
                if key not in put and "keyed" in key[1]:
                    keyed_put = keyed_put + 1
                put.add(key)
                if not entry.get("your_answer"):
                    entry["your_answer"] = _answer(form, mode, entry)
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            _code, spent = _step(["profile", f"{source}", "--replace", "--answers", f"{questions}", *declared])
            rounds = rounds + spent
        if mode == "C":
            rounds = rounds + _corrected(form, questions, source)
        seconds["answers"] = rounds
    described = folder / f"{form.name}-profile.json"
    if not described.is_file():
        raise RunNotComplete(f"{form.name} {mode}: no description")
    # A RUN OF U OR Y WHOSE VALUE COLUMN IS NOT KEYED (its key column held,
    # so no pair is described) is described and read, not generated: its
    # value column is held whole, as on the base, and its twin is the held
    # writer's, which runs past 900 s on a question-and-answer table (lane
    # HB3-b's, RULINGS 1 K13). Its description is the base's save, where
    # the first reading found the pair, the value column's question and
    # hold: unanswered it is put its Safe Harbor question rather than the
    # person question, held as its pool in people would be, its dated
    # cells read as blanks (the vital-signs form and the zoo's kind);
    # the run's own record says no twin was made (`twin_made`).
    value_block = _block(json.loads(described.read_text(encoding="utf-8")), form.value)
    if mode in ("U", "Y", "P", "O") and "by_key" not in value_block:
        return {"folder": folder, "seconds": seconds, "validate": None, "keyed_put": keyed_put, "twin": False}
    _code, seconds["generate"] = _step(["generate", f"{described}", "--replace", "--seed", "0"])
    validated, seconds["validate"] = _step(["validate", f"{described}", "--replace"])
    twin = folder / f"{form.name}-twin.csv"
    if not twin.is_file():
        raise RunNotComplete(f"{form.name} {mode}: no twin")
    return {"folder": folder, "seconds": seconds, "validate": validated, "keyed_put": keyed_put, "twin": True}


def _read(path: pathlib.Path) -> "tuple[list[str], list[list[str]]]":
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def _strings(node: object, found: "set[str]") -> "set[str]":
    if isinstance(node, str):
        found.add(node)
    elif isinstance(node, bool):
        pass
    elif isinstance(node, int):
        found.add(f"{node}")
    elif isinstance(node, dict):
        for key in node:
            found.add(f"{key}")
            _strings(node[key], found)
    elif isinstance(node, list):
        for item in node:
            _strings(item, found)
    return found


def _published(folder: pathlib.Path) -> "tuple[set[str], set[str]]":
    """Every string of every JSON file a run wrote (the description, the questions file), and every token of its text files."""
    strings: "set[str]" = set()
    words: "set[str]" = set()
    for path in sorted(folder.iterdir()):
        if path.suffix == ".json":
            try:
                _strings(json.loads(path.read_text(encoding="utf-8")), strings)
            except ValueError:
                continue
        elif path.suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="replace")
            words |= set(re.findall(r"[^\s,;:()'\"`\[\]{}]+", text))
            words |= set(re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", text))
            words |= set(re.findall(r"\(\d{3}\) \d{3}-\d{4}", text))
    return strings, words


def _block(document: "dict", name: str) -> "dict":
    for block in document["columns"]:
        if block["name"] == name:
            return block
    raise KeyError(name)


def _screened(name: str, numbers: bool, role: str, code: bool) -> bool:
    """Whether a screen of the name's road refuses a rare key's name on its own (`profile.keyed_names_pass`'s screens, each alone).

    Every road: lane CZ-E's identifier words and lane CZ-F's persons'
    names. Then lane CODES-2's road the key column takes: path (i) alone
    for a column of bare numbers (``numbers``); path (iii) for categories
    not answered `code`; path (i) and path (iii)'s net, a run of five
    figures a code's and one of six refused (`counting_figures`), for a
    declared code or a long tail.
    """
    named = taxonomy.HELD_BACK_NAMED_ANSWERED
    # ...each read as written and with what prints nothing set aside (the
    # double reading of LANE CODES-2 RULINGS 8 (2)), and a sentence of three
    # words or more refused (LANE KV RULINGS 2 (2)).
    for written in {name, taxonomy._without_what_prints_nothing(name)}:
        if taxonomy.identifier_words_form(written) or taxonomy.a_persons_name(written):
            return True
        if profile._reads_as_a_sentence(written):
            return True
    if numbers:
        return not taxonomy._names_under(named, (name,), False, True, True)
    if role == taxonomy.ROLE_CATEGORICAL and not code:
        return not taxonomy._names_under(named, (name,), False, True, False)
    return not taxonomy._names_under(named, (name,), False, True, True) or (
        taxonomy._holds_a_letter(name) and not taxonomy.passes_the_word_screen(name, False, False)
    )


def _number(text: str) -> "float | None":
    try:
        value = float(text)
    except ValueError:
        return None
    return value if value == value and abs(value) != float("inf") else None


def _ks(first: "list[float]", second: "list[float]") -> float:
    first, second = sorted(first), sorted(second)
    at_first = at_second = 0
    gap = 0.0
    while at_first < len(first) and at_second < len(second):
        point = min(first[at_first], second[at_second])
        while at_first < len(first) and first[at_first] <= point:
            at_first = at_first + 1
        while at_second < len(second) and second[at_second] <= point:
            at_second = at_second + 1
        gap = max(gap, abs(at_first / len(first) - at_second / len(second)))
    return gap


def _tvd(first: "list[str]", second: "list[str]") -> float:
    if not first or not second:
        return 1.0
    share: "dict[str, float]" = {}
    for value in first:
        share[value] = share.get(value, 0.0) + 1.0 / len(first)
    for value in second:
        share[value] = share.get(value, 0.0) - 1.0 / len(second)
    return 0.5 * sum(abs(gap) for gap in share.values())


def _by_key(header: "list[str]", rows: "list[list[str]]", form: key_value_tables.Form) -> "dict[str, list[tuple[str, str]]]":
    k, v, p = header.index(form.key), header.index(form.value), header.index(form.person)
    found: "dict[str, list[tuple[str, str]]]" = {}
    for row in rows:
        found.setdefault(row[k], []).append((row[p], row[v]))
    return found


_SPLITS = 20


def _mean(values: "list[float]") -> float:
    return sum(values) / len(values)


def _sd(values: "list[float]") -> float:
    middle = _mean(values)
    return (sum((value - middle) ** 2 for value in values) / len(values)) ** 0.5


def _key_bars(real: "list[tuple[str, str]]", made: "list[str]", numeric: bool) -> "dict[str, bool]":
    """Whether a key's twin cells pass each bar (THE STATISTICS CHECK'S ITEM 1, LANE KV RULINGS 4 (1)).

    A numeric key: RANGE, its twin cells inside the real 1st to 99th
    percentile at 0.95 of the real share; KS, the Kolmogorov-Smirnov distance
    at most twice the real table's own half-split value (its people split by
    the parity of their names' letters); MEAN, the twin mean within twice the
    mean gap between the two halves' means over twenty random half-splits of
    its people; SPREAD, the twin's standard deviation within twice the mean
    gap between the halves' deviations over the same splits. A category key:
    TVD, the total variation distance at most twice its half-split value.
    """
    values = [value for _person, value in real]
    if not numeric:
        halves_words: "tuple[list[str], list[str]]" = ([], [])
        for person, value in real:
            halves_words[sum(map(ord, person)) % 2].append(value)
        return {"tvd": _tvd(values, made) <= 2 * _tvd(halves_words[0], halves_words[1])}
    held = [number for number in (_number(value) for value in values) if number is not None]
    made_numbers = [number for number in (_number(cell) for cell in made) if number is not None]
    if not held or not made_numbers:
        return {"range": False, "ks": False, "mean": False, "spread": False}
    ordered = sorted(held)
    low, high = ordered[len(ordered) // 100], ordered[len(ordered) - 1 - len(ordered) // 100]
    real_share = sum(1 for value in held if low <= value <= high) / len(values)
    made_share = sum(1 for value in made_numbers if low <= value <= high) / max(1, len(made))
    halves: "tuple[list[float], list[float]]" = ([], [])
    for person, value in real:
        number = _number(value)
        if number is not None:
            halves[sum(map(ord, person)) % 2].append(number)
    split = _ks(halves[0], halves[1]) if halves[0] and halves[1] else 1.0
    people = sorted({person for person, _value in real})
    draw = random.Random(len(people) * 7919 + len(real))
    gaps_mean: "list[float]" = []
    gaps_spread: "list[float]" = []
    for _turn in range(_SPLITS):
        half = set(draw.sample(people, len(people) // 2))
        first = [number for person, number in ((person, _number(value)) for person, value in real) if number is not None and person in half]
        second = [number for person, number in ((person, _number(value)) for person, value in real) if number is not None and person not in half]
        if first and second:
            gaps_mean += [abs(_mean(first) - _mean(second))]
            gaps_spread += [abs(_sd(first) - _sd(second))]
    mean_bar = 2 * _mean(gaps_mean) if gaps_mean else float("inf")
    spread_bar = 2 * _mean(gaps_spread) if gaps_spread else float("inf")
    return {
        "range": made_share >= 0.95 * real_share,
        "ks": _ks(held, made_numbers) <= 2 * split,
        "mean": abs(_mean(made_numbers) - _mean(held)) <= mean_bar,
        "spread": abs(_sd(made_numbers) - _sd(held)) <= spread_bar,
    }


def _bars(form: key_value_tables.Form, real: "dict[str, list[tuple[str, str]]]", twin: "dict[str, list[tuple[str, str]]]",
          control: "dict[str, list[tuple[str, str]]]", described: "set[str]", common: "set[str]") -> "dict[str, object]":
    """Per common key whose block is described: each bar on the twin and on the CONTROL, each key failing counted, and each key whose bar the control passes counted VOID for that bar, never as passing (the statistics check's item 1 (a))."""
    counts: "dict[str, object]" = {"numeric": 0, "category": 0}
    for bar in ("range", "ks", "mean", "spread", "tvd"):
        counts[f"{bar}_failing"] = 0
        counts[f"{bar}_void"] = 0
    control_whole = 0
    shares: "list[float]" = []
    distances: "list[float]" = []
    variations: "list[float]" = []
    for key in sorted(common & described):
        real_pairs = real.get(key, [])
        real_values = [value for _person, value in real_pairs]
        made = [value for _person, value in twin.get(key, [])]
        held = [value for value in (_number(value) for value in real_values) if value is not None]
        numeric = bool(real_values) and 10 * len(held) >= 9 * len(real_values)
        counts["numeric" if numeric else "category"] = int(counts["numeric" if numeric else "category"]) + 1  # type: ignore[call-overload]
        passes = _key_bars(real_pairs, made, numeric)
        controlled = _key_bars(real_pairs, [value for _person, value in control.get(key, [])], numeric)
        for bar, passed in passes.items():
            if not passed:
                counts[f"{bar}_failing"] = int(counts[f"{bar}_failing"]) + 1  # type: ignore[call-overload]
            if controlled[bar]:
                counts[f"{bar}_void"] = int(counts[f"{bar}_void"]) + 1  # type: ignore[call-overload]
        if all(controlled.values()):
            control_whole = control_whole + 1
        if numeric:
            ordered = sorted(held)
            low, high = ordered[len(ordered) // 100], ordered[len(ordered) - 1 - len(ordered) // 100]
            made_numbers = [value for value in (_number(cell) for cell in made) if value is not None]
            shares += [sum(1 for value in made_numbers if low <= value <= high) / max(1, len(made))]
            distances += [_ks(held, made_numbers) if made_numbers else 1.0]
        else:
            variations += [_tvd(real_values, made)]
    keys = int(counts["numeric"]) + int(counts["category"])  # type: ignore[call-overload]
    # ...THE CONTROL PASSES THE BARS where it passes every bar of a key on
    # half the keys or more: read on every bar, never on the range alone.
    counts["control_passes"] = bool(keys) and 2 * control_whole >= keys
    for name, listed in (("median_inside", shares), ("median_ks", distances), ("median_tvd", variations)):
        ordered = sorted(listed)
        counts[name] = round(ordered[len(ordered) // 2], 3) if ordered else None
    return counts


def self_check() -> None:
    """THE BARS' OWN CASE (the statistics check's item 1 (c)): a key block written as a constant inside the real range fails a bar.

    A key of eleven people on one row each, the even half of them below 100
    and the odd half above 150, and every twin cell 90: inside the real 1st
    to 99th percentile, and within twice a half-split Kolmogorov-Smirnov
    distance of 1.0 -- the first stamp's range, KS and TVD bars passed it,
    as they passed eight described keys of the zoo's kind more than one
    standard deviation off. The mean or the spread bar must fail it, or the
    driver stops.
    """
    real = [(f"P{place}", f"{(86 + 3 * place) if sum(map(ord, f'P{place}')) % 2 == 0 else (150 + 2 * place)}") for place in range(11)]
    passes = _key_bars(real, ["90"] * 11, True)
    if not (passes["range"] and passes["ks"]) or (passes["mean"] and passes["spread"]):
        raise SystemExit(f"K-HZ-37's bars fail their own case (a constant inside the real range): {passes}")


AGES_PAST_89 = "age_in_years_over_89"


def _ages_past_89(
    document: "dict", form: key_value_tables.Form, header: "list[str]", rows: "list[list[str]]", real: "set[str]"
) -> "tuple[int, int, int]":
    """Ages past 89 published and written, read as lane SH3's driver reads them for K-HZ-20 (`age_address_shapes`).

    A whole number anywhere in a file is no age: a count of 93 rows, or the
    top category itself, which the Safe Harbor rule allows (every age from
    90 read as 90), was read as one by the first draft. So: in each key
    block whose key the product names an age (`taxonomy.age_mark_named`),
    every published value outside the count-like facts (`_published`, the
    walker K-HZ-20 uses) read in years over the mark -- past 90 where the
    block is top-coded, from 90 where not -- one each distinct; in the value
    column's own block and the pooled block, a published value equal to a
    real age past 89. Written: on the rows of an age key whose block is
    described, a twin cell over the mark; where its block is held, a twin
    cell equal to a real age past 89, its other made-up values over the mark
    returned apart (LANE I4m RULINGS 21 (1)); on every other row, a twin
    cell equal to a real age past 89. Every count is linear in the cells.
    """
    import age_address_shapes as shapes

    value_block = _block(document, form.value)
    k = header.index(form.key)
    v = header.index(form.value)
    published: "set[tuple[float, str]]" = set()
    aged: "dict[str, tuple[bool, bool]]" = {}
    others = [{name: value_block[name] for name in value_block if name != "by_key"}]
    if "by_key" in value_block:
        if "pool" in value_block["by_key"]:
            others += [value_block["by_key"]["pool"]]
        for entry in value_block["by_key"]["key_blocks"]:
            label = f"{entry['key']}"
            if not taxonomy.age_mark_named(label) and label not in {key.casefold() for key in form.age_keys}:
                continue
            block = entry["block"]
            top = "top_coded" in block
            aged[label] = (top, block["role"] == "identifier")
            for _path, value, _unit in shapes._published(block):
                read = shapes.in_its_unit(f"{value}", shapes.YEARS)
                if read is not None and shapes.over_the_mark(read[0], read[1], top):
                    published.add(read)
    for block in others:
        for _path, value, _unit in shapes._published(block):
            if f"{value}".strip() in real:
                published.add((float(f"{value}".strip()), shapes.YEARS))
    written = 0
    made_up = 0
    for row in rows:
        label = row[k].strip().casefold()
        if label in aged and not aged[label][1]:
            read = shapes.in_its_unit(row[v], shapes.YEARS)
            written += 1 if read is not None and shapes.over_the_mark(read[0], read[1], aged[label][0]) else 0
        elif row[v] in real:
            written += 1
        elif label in aged:
            read = shapes.in_its_unit(row[v], shapes.YEARS)
            made_up += 1 if read is not None and shapes.over_the_mark(read[0], read[1], False) else 0
    return len(published), written, made_up


def measure(form: key_value_tables.Form, mode: str, done: "dict[str, object]") -> "dict[str, object]":
    folder = done["folder"]
    assert isinstance(folder, pathlib.Path)
    census = key_value_tables.census(form)
    rare = key_value_tables.rare_keys(form)
    common = {key for key in census if key not in rare}
    rare_only = key_value_tables.rare_only_values(form)
    strings, words = _published(folder)
    document = json.loads((folder / f"{form.name}-profile.json").read_text(encoding="utf-8"))
    key_block = _block(document, form.key)
    value_block = _block(document, form.value)
    names = key_block.get("held_back_names") or []
    numbers = all(parsing.classify_number(f"{name}") == parsing.NUMBER for name in names)
    code = form.key_is_code and mode != "U"
    found: "dict[str, object]" = {
        "rare_keys_named": len([key for key in rare if key in strings or key in words]),
        "names_a_screen_reads": len([
            name for name in names if _screened(f"{name}", numbers, f"{key_block['role']}", code)
        ]),
        "names_published": len(names),
        "keyed": "by_key" in value_block,
    }
    blocks = {}
    if "by_key" in value_block:
        for entry in value_block["by_key"]["key_blocks"]:
            blocks[f"{entry['key']}"] = entry["block"]
    written_of = {}
    for level in key_block.get("levels") or []:
        best = max(level.get("variants") or {f"{level['label']}": 1}, key=lambda spelling: (level["variants"] or {}).get(spelling, 0) if level.get("variants") else 0)
        written_of[f"{level['label']}"] = best
    found["key_blocks_of_rare_keys"] = len([label for label in blocks if not any(
        key.strip().casefold() == label for key in common)])
    header, rows = list(form.header), [list(row) for row in form.rows]
    real = _by_key(header, rows, form)
    few = 0
    grained = 0
    for label, block in blocks.items():
        # ...a block published at a grain names buckets, never a value of the
        # table (contract NF128: `2023-01-01` at the rung `year` is 2023),
        # each counted in people by the product and checked by V14: its
        # levels are not read against the cells here, and it is counted apart.
        if "time_grain" in block:
            grained = grained + 1
            continue
        spelled = [key for key in census if key.strip().casefold() == label]
        holders: "dict[str, set[str]]" = {}
        # ...a top-coded block's top level stands for every value from its
        # mark (the age top-code, P4-D487's limit (c)): its holders are the
        # people holding any of them.
        mark = block.get("top_coded")
        top = f"{mark}" if isinstance(mark, int) and not isinstance(mark, bool) else None
        for key in spelled:
            for person, value in real.get(key, []):
                holders.setdefault(value.strip().casefold(), set()).add(person)
                number = _number(value.strip())
                if top is not None and number is not None and number >= float(top):
                    holders.setdefault(f"top {top}", set()).add(person)
        # ...and a top category fewer than the floor's people hold is pooled
        # below the mark (P4-D454, `taxonomy.top_category_pooled`): its cells
        # are written as the largest value below the mark the block holds,
        # whose level then stands for its own holders and every holder from
        # the mark (`85` written on eleven rows of eleven people, one of
        # whom wrote 85, on the zoo's kind: the first reading counted one).
        below: "tuple[float, str] | None" = None
        if top is not None:
            for key in spelled:
                for _person, value in real.get(key, []):
                    number = _number(value.strip())
                    if number is not None and number < float(top) and (below is None or number > below[0]):
                        below = (number, value.strip().casefold())
        published = {f"{level['label']}" for level in block.get("levels") or []}
        for level in block.get("levels") or []:
            name = f"{level['label']}"
            if top is not None and name == top:
                held_by = holders.get(f"top {top}", set())
            elif top is not None and top not in published and below is not None and name == below[1]:
                held_by = holders.get(name, set()) | holders.get(f"top {top}", set())
            else:
                held_by = holders.get(name, set())
            if 1 <= len(held_by) <= FLOOR - 1:
                few = few + 1
    found["level_counts_of_1_to_10_people"] = few
    found["key_blocks_at_a_grain"] = grained
    # ...and, recorded apart, the key blocks whose absent cells are 1 to 10
    # rows (a column's `n_missing` is published as every column's is).
    found["key_blocks_with_1_to_10_absent_cells"] = len([
        block for block in blocks.values() if 1 <= int(block.get("n_missing") or 0) <= FLOOR - 1
    ])
    found["twin_made"] = bool(done["twin"])
    twin_header, twin_rows = _read(folder / f"{form.name}-twin.csv") if done["twin"] else (list(form.header), [])
    twin = _by_key(twin_header, twin_rows, form)
    k = twin_header.index(form.key)
    v = twin_header.index(form.value)
    found["twin_cells_equal_a_rare_only_value"] = sum(1 for row in twin_rows if row[v] in rare_only)
    found["key_cells_off_the_list"] = sum(1 for row in twin_rows if row[k] and row[k] not in census)
    held = {label for label, block in blocks.items() if block["role"] == "identifier"}
    described = {key for key in common if key.strip().casefold() in blocks and key.strip().casefold() not in held}
    found["key_blocks"] = len(blocks)
    found["key_blocks_held"] = len(held)
    # ...THE NUMBER KEYS A BLOCK HOLDS OR TOP-CODES, named apart (the
    # statistics check's item 2 (a), owner KV-b): a held key's twin cells
    # are made up, a top-coded key's every value from 90 written as 90.
    numeric_common = set()
    for key in common:
        values = [value for _person, value in real.get(key, [])]
        if values and 10 * len([value for value in values if _number(value) is not None]) >= 9 * len(values):
            numeric_common.add(key.strip().casefold())
    found["numeric_keys_held"] = sorted(label for label in held if label in numeric_common)
    found["numeric_keys_top_coded"] = sorted(
        label for label, block in blocks.items() if label in numeric_common and label not in held and "top_coded" in block
    )
    shuffled_values = [row[v] for row in twin_rows]
    random.Random(7).shuffle(shuffled_values)
    control_rows = [row[:v] + [value] + row[v + 1:] for row, value in zip(twin_rows, shuffled_values)]
    bars = _bars(form, real, twin, _by_key(twin_header, control_rows, form), described, common)
    found.update({f"bars_{key}": value for key, value in bars.items()})
    found["control_passes"] = bars["control_passes"]
    exact = 0
    twin_counts: "dict[str, int]" = {}
    for row in twin_rows:
        twin_counts[row[k]] = twin_counts.get(row[k], 0) + 1
    for level in key_block.get("levels") or []:
        spelled_total = sum(count for key, count in twin_counts.items() if key.strip().casefold() == level["label"])
        if spelled_total != level["count"]:
            exact = exact + 1
    found["published_key_counts_not_exact"] = exact
    if form.identifiers:
        exposed: "dict[str, int]" = {}
        for kind, values in form.identifiers:
            if kind == AGES_PAST_89:
                published, written, made_up = _ages_past_89(document, form, twin_header, twin_rows, set(values))
                exposed[kind] = published
                exposed[f"{kind} twin"] = written
                found["made_up_ages_past_the_mark"] = made_up
                continue
            shown = len([value for value in values if value in strings or value in words])
            cells = sum(1 for row in twin_rows if row[v] in values)
            exposed[kind] = shown
            exposed[f"{kind} twin"] = cells
        found["identifiers"] = exposed
    found["seconds"] = {key: round(value, 1) for key, value in done["seconds"].items()}  # type: ignore[union-attr]
    found["keyed_put"] = done["keyed_put"]
    found["validate_exit"] = done["validate"]
    return found


def zoo_kinds(folder: pathlib.Path) -> "dict[str, str]":
    """The zoo's three key-value kinds through the zoo's own run_table at 20,000 rows: each kind's failing checks and owners."""
    import dates_in_disguise
    import health_zoo

    tables = [dates_in_disguise.table_named(name) for name in ("answers_long", "flow_values", "results_dated")]
    results = health_zoo.run_zoo(folder, 20000, tables=tables)
    measured = health_zoo.zoo_measures(results)
    said: "dict[str, str]" = {}
    for kind, verdict in measured["kinds"].items():
        said[kind] = "passes" if verdict["passed"] else (
            f"{verdict['failing_step']}: {len(verdict['failures'])} failing; {', '.join(verdict['owners']) or 'NO OWNER'}"
        )
    return said


def runs() -> "list[tuple[key_value_tables.Form, str]]":
    """Each form and mode the driver runs: the six forms in the four modes; then repair 1's (LANE KV RULINGS 3 and 4): the pool of one rare key (sp) in N and M, the coded identifier form (qpc) in the four modes, the hidden names (hf) in N, the vital-signs form in P and O, and the lab form in D; then repair 2's (LANE KV RULINGS 6): the coded identifier form in C and E."""
    forms = key_value_tables.all_forms()
    found = [(form, mode) for form in forms for mode in MODES]
    fs = [form for form in forms if form.name == "fs"][0]
    lab = [form for form in forms if form.name == "lab"][0]
    found += [(key_value_tables.small_pool(fs), mode) for mode in ("N", "M")]
    found += [(key_value_tables.coded_identifiers(), mode) for mode in MODES]
    found += [(key_value_tables.hidden_names(fs), "N"), (fs, "P"), (fs, "O"), (lab, "D")]
    found += [(key_value_tables.coded_identifiers(), mode) for mode in ("C", "E")]
    return found


def main() -> None:
    self_check()
    value: "dict[str, object]" = {}
    said: "list[str]" = []
    totals = {
        "rare_keys_named_unanswered_20000_rows": 0, "rare_keys_named_after_yes_20000_rows": 0,
        "names_a_screen_reads_named_20000_rows": 0, "key_blocks_of_rare_keys_20000_rows": 0,
        "level_counts_of_1_to_10_people_20000_rows": 0, "twin_cells_equal_a_rare_only_value_20000_rows": 0,
        "identifier_values_published_or_written_unanswered_or_truthful_20000_rows": 0,
        "ages_past_89_published_or_written_20000_rows": 0, "key_cells_off_the_list_after_no_20000_rows": 0,
        "key_cells_off_the_list_names_refused_20000_rows": 0,
        "names_or_values_of_a_pool_of_one_key_or_few_people_20000_rows": 0,
        "numeric_keys_failing_range_20000_rows": 0, "numeric_keys_failing_ks_20000_rows": 0,
        "numeric_keys_failing_mean_20000_rows": 0, "numeric_keys_failing_spread_20000_rows": 0,
        "category_keys_failing_tvd_20000_rows": 0, "numeric_keys_with_a_void_ks_bar_20000_rows": 0,
        "category_keys_with_a_void_tvd_bar_20000_rows": 0, "numeric_keys_held_20000_rows": 0,
        "numeric_keys_top_coded_20000_rows": 0, "published_key_counts_not_exact_20000_rows": 0,
        "control_runs_passing_the_bars_20000_rows": 0, "runs_whose_validate_misses_20000_rows": 0,
    }
    prices: "list[str]" = []
    keyed_put: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-key-value-") as scratch:
        for form, mode in runs():
            started = time.perf_counter()
            done = run(pathlib.Path(scratch) / form.name / mode, form, mode)
            found = measure(form, mode, done)
            if mode in ("U", "P", "O"):
                totals["rare_keys_named_unanswered_20000_rows"] += int(found["rare_keys_named"])  # type: ignore[arg-type]
            if mode == "Y":
                totals["rare_keys_named_after_yes_20000_rows"] += int(found["rare_keys_named"])  # type: ignore[arg-type]
            totals["names_a_screen_reads_named_20000_rows"] += int(found["names_a_screen_reads"])  # type: ignore[arg-type]
            totals["key_blocks_of_rare_keys_20000_rows"] += int(found["key_blocks_of_rare_keys"])  # type: ignore[arg-type]
            totals["level_counts_of_1_to_10_people_20000_rows"] += int(found["level_counts_of_1_to_10_people"])  # type: ignore[arg-type]
            totals["twin_cells_equal_a_rare_only_value_20000_rows"] += int(found["twin_cells_equal_a_rare_only_value"])  # type: ignore[arg-type]
            if mode in ("N", "M") and form.name not in ("qp", "qpc"):
                # ...recorded apart where the screens refused the names ALL OR
                # NONE (P4-D487's limit (e): six figures one of which reads as
                # a date), so the count is the forms whose names were published.
                off = "key_cells_off_the_list_after_no_20000_rows" if found["names_published"] else (
                    "key_cells_off_the_list_names_refused_20000_rows")
                totals[off] += int(found["key_cells_off_the_list"])  # type: ignore[arg-type]
            # ...the runs of C and E read for HIPAA and the validator, their
            # bars not counted (the same form's are, in its four modes).
            if found["keyed"] and mode not in ("C", "E"):
                for bar, key in (("range", "numeric_keys_failing_range"), ("ks", "numeric_keys_failing_ks"), ("mean", "numeric_keys_failing_mean"),
                                 ("spread", "numeric_keys_failing_spread"), ("tvd", "category_keys_failing_tvd")):
                    totals[f"{key}_20000_rows"] += int(found[f"bars_{bar}_failing"])  # type: ignore[arg-type]
                totals["numeric_keys_with_a_void_ks_bar_20000_rows"] += int(found["bars_ks_void"])  # type: ignore[arg-type]
                totals["category_keys_with_a_void_tvd_bar_20000_rows"] += int(found["bars_tvd_void"])  # type: ignore[arg-type]
                totals["control_runs_passing_the_bars_20000_rows"] += 1 if found["control_passes"] else 0
                if mode == "N":
                    totals["numeric_keys_held_20000_rows"] += len(found["numeric_keys_held"])  # type: ignore[arg-type]
                    totals["numeric_keys_top_coded_20000_rows"] += len(found["numeric_keys_top_coded"])  # type: ignore[arg-type]
            totals["published_key_counts_not_exact_20000_rows"] += int(found["published_key_counts_not_exact"])  # type: ignore[arg-type]
            totals["runs_whose_validate_misses_20000_rows"] += 1 if found["validate_exit"] == 3 else 0
            exposed = found.get("identifiers")
            if form.name == "sp":
                # ...THE POOL OF ONE RARE KEY OF FOUR PEOPLE (LANE KV RULINGS 3
                # (1)): its name and its town, published or written, any mode.
                totals["names_or_values_of_a_pool_of_one_key_or_few_people_20000_rows"] += int(found["names_published"]) + (  # type: ignore[call-overload]
                    sum(int(count) for count in exposed.values()) if isinstance(exposed, dict) else 0)
            if isinstance(exposed, dict):
                ages = int(exposed.get("age_in_years_over_89", 0)) + int(exposed.get("age_in_years_over_89 twin", 0))
                totals["ages_past_89_published_or_written_20000_rows"] += ages
                if mode in ("U", "N", "P", "O", "D", "C", "E"):
                    totals["identifier_values_published_or_written_unanswered_or_truthful_20000_rows"] += sum(
                        int(count) for count in exposed.values())
                if mode == "M" and form.name in ("qp", "qpc"):
                    # ...the classes a careless `no` shows, each shown or written
                    # count that is not 0 (every other class 0).
                    shown = [f"{kind}: {count}" for kind, count in exposed.items() if count]
                    value[f"careless_no_identifiers_{'coded_form_' if form.name == 'qpc' else ''}20000_rows"] = (
                        ", ".join(shown) if shown else "0 in every class")
            said += [f"{form.name} {mode} {round(time.perf_counter() - started, 1)} s {json.dumps(dict(found), sort_keys=True)}"]
            if mode == "N":
                spent = found["seconds"]
                assert isinstance(spent, dict)
                prices += [
                    f"{form.name} {spent.get('profile', 0) + spent.get('answers', 0):.0f}/"
                    f"{spent.get('generate', 0):.0f}/{spent.get('validate', 0):.0f}"
                ]
                keyed_put += [f"{form.name} {found['keyed_put']}"]
        started = time.perf_counter()
        kinds = zoo_kinds(pathlib.Path(scratch) / "zoo")
        value["zoo_key_value_kinds_20000_rows"] = "; ".join(f"{kind}: {verdict}" for kind, verdict in sorted(kinds.items()))
        said += [f"zoo kinds {round(time.perf_counter() - started, 1)} s"]
    value.update(totals)
    value["cpu_seconds_profile_generate_validate_mode_n_20000_rows"] = ", ".join(prices)
    value["keyed_questions_put_mode_n_20000_rows"] = ", ".join(keyed_put)
    kpi_rules.emit("K-HZ-37", value, " | ".join(said))


if __name__ == "__main__":
    main()
