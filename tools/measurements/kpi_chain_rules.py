"""K-S6-06 at 20,000 rows, K-BC-10's rule readings, and the rules page's price on the built product (lane RO, plan P4-D459).

Every table is invented (`tests/rules_event_table.py`, round figures by
hand). Each is described with the chain's switch and its rule steps on
(`chain.ChainSwitch(..., rows_per_person=chain.ROWS_UNASKED, rules=True)`, a fixed test key) on the library
path, written with its computed columns' blocks (`chain.with_rules`),
loaded behind the switch (`contract.load_profile(..., chain=True)`),
generated (`generation.generate_held`) and read back as text.

- K-S6-06 (contract 4.6b.7, MR.10), the parts lane RO stamps, each on three
  twin seeds: (i) `ended_on >= started_on` with `days_open` their gap: the
  twin rows ending before they start and the rows disagreeing, 0 and 0;
  (ii) `closed_at >= opened_at`: 0 rows; (v) 6 rows keyed into (ii): the
  phrase and 0 twin rows, 150 rows keyed: the count 150 and exactly 150;
  (vii) `chain_rows()`, a chain of events: the twin rows breaking each
  adjacent pair, counted, the part OPEN until lane RO2. Beside them, the
  page's baseline re-read on this head (the twin with the chain off), and
  the formula's and the impossible combination's rows (RD's and RZ's).
- K-BC-10's three readings (MR.10), read from each fixture's own rule
  inventory (every carried rule and every inferred rule left uncarried, on
  the event tables and the chain of events alike), on every twin: PLACED,
  every carried rule's twin rows breaking it against its class, each twin
  judged on its own (`rules_placed_off`, judged 0 by K-S6-06, which
  carries it); UNPLACED, the twin rows breaking an inferred rule the draw
  left uncarried, summed over its pairs with the pairs counted and their
  reasons (reported, never failing). The NEAR-RULE reading is private and
  is never printed here.

    PYTHONPATH=src:tests python tools/measurements/kpi_chain_rules.py --kpi [--rows 20000] [--seeds 0,1,2]
    PYTHONPATH=src:tests python tools/measurements/kpi_chain_rules.py --time <rows> <columns>

No count of 1 to 10 rows of the real table tied to a rule is printed: the
real tables' failing rows are the fixture's own, and a class is printed
only as the description publishes it.
"""

import csv
import datetime
import fractions
import io
import json
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import rules_event_table as events  # noqa: E402

from synthtwin import (  # noqa: E402
    canonical,
    chain,
    chain_order,
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
)

FLOOR = 11
TEST_KEY = bytes(range(32))


def _argument(flag: str, default: "list[int]") -> "list[int]":
    if flag in sys.argv:
        place = sys.argv.index(flag)
        return [int(item) for item in sys.argv[place + 1].split(",")]
    return default


def _describe(folder: pathlib.Path, name: str, header: "tuple[str, ...]", rows: "list[list[str]]", rules: bool = True, seen: "list[chain_order.Inference] | None" = None):  # type: ignore[no-untyped-def]
    """The table described with the chain's switch (and its rule steps), written with its rules and loaded behind it;
    the inference's rule inventory kept in `seen` where one is handed in."""
    path = folder / f"{name}.csv"
    path.write_text(events.as_text(header, rows), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    started = time.time()
    document = profile.build_document(table, settings, [], [], [])
    profiled = time.time() - started
    original = chain._rule_steps

    def keeping(inference, switch, names):  # type: ignore[no-untyped-def]
        if seen is not None:
            seen.append(inference)
        return original(inference, switch, names)

    chain._rule_steps = keeping  # type: ignore[assignment]
    started = time.time()
    try:
        chained = chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=rules))
    finally:
        chain._rule_steps = original  # type: ignore[assignment]
    described = time.time() - started
    plain_path = folder / f"{name}-plain.json"
    plain_path.write_text(canonical.serialize(document), encoding="utf-8", newline="\n")
    plain = contract.load_profile(str(plain_path))
    loaded = None
    if chained.statistical is not None:
        on = folder / f"{name}-switched.json"
        on.write_text(canonical.serialize(chain.with_rules(document, chained)), encoding="utf-8", newline="\n")
        loaded = contract.load_profile(str(on), chain=True)
    return chained, loaded, plain, round(profiled, 1), round(described, 1)


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    return {rows[0][at]: [row[at] for row in rows[1:]] for at in range(len(rows[0]))}


def _day(text: str) -> "datetime.date | None":
    return datetime.date.fromisoformat(text) if text else None


def _stamp(text: str) -> "datetime.datetime | None":
    return datetime.datetime.strptime(text, "%Y-%m-%d %H:%M") if text else None


def _event_counts(text: str) -> "dict[str, int]":
    """The event table's five rules counted on one table (MR.10's parts (i) to (iv))."""
    cells = _columns(text)
    out = {"end_before_start": 0, "days_open_off": 0, "closed_before_opened": 0, "total_off": 0, "impossible": 0}
    for row in range(len(cells["started_on"])):
        started, ended, days = _day(cells["started_on"][row]), _day(cells["ended_on"][row]), cells["days_open"][row]
        if started and ended and ended < started:
            out["end_before_start"] += 1
        if started and days and (ended is None or (ended - started).days != int(days)):
            out["days_open_off"] += 1
        opened, closed = _stamp(cells["opened_at"][row]), _stamp(cells["closed_at"][row])
        if opened and closed and closed < opened:
            out["closed_before_opened"] += 1
        units, rate, total = cells["units"][row], cells["rate"][row], cells["total"][row]
        if units and rate and total and events._money(int(units), rate) != total:
            out["total_off"] += 1
        if cells["gender"][row] == "M" and cells["pregnant"][row] == "yes":
            out["impossible"] += 1
    return out


def _chain_counts(text: str) -> "dict[str, int]":
    """`chain_rows()`'s adjacent pairs broken on one table (part (vii))."""
    cells = _columns(text)
    out = {"seen_before_arrived": 0, "left_before_seen": 0, "left_on_off": 0}
    for row in range(len(cells["arrived_at"])):
        arrived, seen, left = _stamp(cells["arrived_at"][row]), _stamp(cells["seen_at"][row]), _stamp(cells["left_at"][row])
        if arrived and seen and seen < arrived:
            out["seen_before_arrived"] += 1
        if seen and left and left < seen:
            out["left_before_seen"] += 1
        if left and cells["left_on"][row] and cells["left_on"][row] != left.date().isoformat():
            out["left_on_off"] += 1
    return out


def _gap_shape(cells: "dict[str, list[str]]") -> "tuple[float, int]":
    """`closed_at - opened_at` on one table: the share of rows where both read whose gap is 0, and the median
    gap in minutes (K-S6-06's judged leg against an erased gap, lane RO's repair 1)."""
    gaps: "list[int]" = []
    for opened_text, closed_text in zip(cells["opened_at"], cells["closed_at"]):
        opened, closed = _stamp(opened_text), _stamp(closed_text)
        if opened and closed:
            gaps += [int((closed - opened).total_seconds()) // 60]
    if not gaps:
        return 0.0, 0
    ordered = sorted(gaps)
    return round(gaps.count(0) / len(gaps), 4), ordered[(len(ordered) - 1) // 2]


def _twin_text(loaded: contract.Profile, seed: int) -> "tuple[str, float, int, int]":
    started = time.time()
    twin = generation.generate_held(loaded, seed)
    seconds = time.time() - started
    planned = generation.plan_generation(loaded).words_planned
    return "".join(rendering.twin_csv_pieces(twin)), round(seconds, 1), planned, twin.words_drawn


def _reading(text: str) -> "tuple[str, object] | None":
    """A fixture's cell read as a stamp, a date or an exact number; None where it holds none."""
    if not text:
        return None
    for kind, read in (("stamp", _stamp), ("date", _day)):
        try:
            return kind, read(text)
        except ValueError:
            pass
    try:
        return "number", fractions.Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def _broken(cells: "dict[str, list[str]]", first: str, target: str) -> int:
    """The twin rows breaking `target` on or after `first` (MR.1): a stamp beside a date read by its day."""
    count = 0
    for a_text, b_text in zip(cells[first], cells[target]):
        a, b = _reading(a_text), _reading(b_text)
        if a is None or b is None or (a[0] != b[0] and "number" in (a[0], b[0])):
            continue
        x, y = a[1], b[1]
        if a[0] != b[0]:
            x = x.date() if a[0] == "stamp" else x  # type: ignore[attr-defined]
            y = y.date() if b[0] == "stamp" else y  # type: ignore[attr-defined]
        count += 1 if y < x else 0  # type: ignore[operator]
    return count


def _source_off(cells: "dict[str, list[str]]", first: str, target: str, carrier: str, unit: str) -> int:
    """The twin rows breaking a source rule: `B` below `A`, or `B` other than `A + D` times the unit where both read."""
    seconds = {name: size for name, size in (("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1))}
    off = _broken(cells, first, target)
    for a_text, b_text, d_text in zip(cells[first], cells[target], cells[carrier]):
        a, d, b = _reading(a_text), _reading(d_text), _reading(b_text)
        if a is None or d is None or d[0] != "number":
            continue
        if b is None or b[0] != a[0]:
            off += 1
        elif a[0] == "number":
            off += 0 if b[1] == a[1] + d[1] else 1  # type: ignore[operator]
        else:
            size = seconds[unit] if unit in seconds else 1
            gap = (b[1] - a[1]).total_seconds()  # type: ignore[operator]
            off += 0 if gap == d[1] * size else 1  # type: ignore[operator]
    return off


def _inventory(chained: chain.Chained, seen: "list[chain_order.Inference]") -> "tuple[list[dict[str, object]], list[tuple[str, str, str]]]":
    """A described fixture's rule inventory: its carried rules as published, and every inferred rule the draw
    left uncarried as `(A, B, reason)`, the reason as the private notes give it."""
    carried = list(chained.statistical["rules"]) if chained.statistical is not None else []  # type: ignore[arg-type]
    named = {(f"{rule['inputs'][0]}", f"{rule['computed']}") for rule in carried}  # type: ignore[index]
    left: "list[tuple[str, str, str]]" = []
    for rule in seen[0].rules if seen else ():
        pair = (rule.inputs[0], rule.computed)
        if pair in named:
            continue
        lead = f"the rule {rule.computed} on or after {rule.inputs[0]} was not carried among "
        why = next((note[note.rfind("(") + 1 : -1] for note in chained.notes if note.startswith(lead)), "drawn")
        left += [(pair[0], pair[1], why)]
    return carried, left  # type: ignore[return-value]


def _farthest(previous: "int | None", count: int, wanted: int) -> int:
    """Of a twin seed's count and the seeds' before it, the one farthest from the class it places (the first
    such where two stand as far): never the largest count, which hides a twin placing too few."""
    if previous is None or abs(count - wanted) > abs(previous - wanted):
        return count
    return previous


def _readings_of(cells: "dict[str, list[str]]", carried: "list[dict[str, object]]", left: "list[tuple[str, str, str]]", tally: "dict[str, object]") -> None:
    """K-BC-10's PLACED and UNPLACED readings on one twin, added to `tally` (MR.10)."""
    for rule in carried:
        first, target, klass = f"{rule['inputs'][0]}", f"{rule['computed']}", rule["class"]  # type: ignore[index]
        if rule["carrier"] == "derived":
            off = _broken(cells, first, target) != (0 if klass == "phrase" else int(f"{klass}"))
        else:
            off = _source_off(cells, first, target, f"{rule['carrier']}", f"{rule['unit']}") != 0
        tally["rules_placed_checked"] = int(f"{tally['rules_placed_checked']}") + 1
        tally["rules_placed_off"] = int(f"{tally['rules_placed_off']}") + (1 if off else 0)
    reasons = tally["rules_unplaced_reasons"]
    assert isinstance(reasons, dict)
    for first, target, why in left:
        tally["rules_unplaced_pairs"] = int(f"{tally['rules_unplaced_pairs']}") + 1
        tally["rules_unplaced_rows"] = int(f"{tally['rules_unplaced_rows']}") + _broken(cells, first, target)
        reasons[why] = (reasons[why] if why in reasons else 0) + 1


def _class_of(chained: chain.Chained, computed: str) -> "str | int | None":
    if chained.statistical is None:
        return None
    for rule in chained.statistical["rules"]:  # type: ignore[union-attr]
        if rule["computed"] == computed:
            klass = rule["class"]
            return klass if isinstance(klass, (str, int)) else None
    return None


def measure(rows: int, seeds: "list[int]") -> "tuple[dict[str, object], dict[str, object]]":
    """K-S6-06's parts (i), (ii), (v) and (vii) and K-BC-10's placed and unplaced readings, each twin judged
    on its own: a keyed class's rows are stamped from the seed farthest from the class, and every carried
    rule of every fixture is a PLACED check on every twin (lane RO's repair 2, the outside review's items
    12 and 13)."""
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-"))
    value: "dict[str, object]" = {"rows": rows, "twins": 0, "words_off": 0}
    readings: "dict[str, object]" = {"rules_placed_checked": 0, "rules_placed_off": 0, "rules_unplaced_pairs": 0,
                                     "rules_unplaced_rows": 0, "rules_unplaced_reasons": {}}
    gap_kept = True
    seconds: "dict[str, object]" = {}
    for keyed in (0, 6, 150):
        real_rows = events.event_rows(rows, keyed_rows=keyed)
        real_share, real_median = _gap_shape(_columns(events.as_text(events.HEADER, real_rows)))
        value[f"keyed_{keyed}_zero_share_real"] = real_share
        value[f"keyed_{keyed}_median_minutes_real"] = real_median
        seen: "list[chain_order.Inference]" = []
        chained, loaded, plain, profiled, described = _describe(folder, f"event{keyed}", events.HEADER, real_rows, seen=seen)
        seconds[f"event{keyed}"] = {"profile": profiled, "describe_with_rules": described}
        assert loaded is not None
        carried, left = _inventory(chained, seen)
        klass = _class_of(chained, "closed_at")
        value[f"class_keyed_{keyed}"] = "not carried" if klass is None else klass
        value[f"days_open_carrier_keyed_{keyed}"] = next(
            (rule["carrier"] for rule in chained.statistical["rules"] if rule["computed"] == "ended_on"), "not carried"  # type: ignore[index, union-attr]
        )
        wanted = 0 if klass is None or klass == "phrase" else int(f"{klass}")
        worst: "dict[str, int]" = {}
        for seed in seeds:
            text, generated, planned, drawn = _twin_text(loaded, seed)
            seconds[f"event{keyed}_generate_seed{seed}"] = generated
            value["twins"] = int(f"{value['twins']}") + 1
            value["words_off"] = int(f"{value['words_off']}") + abs(planned - drawn)
            counts = _event_counts(text)
            for key in counts:
                if key == "closed_before_opened":
                    # The seed farthest from the class it places, never the largest count.
                    worst[key] = _farthest(worst[key] if key in worst else None, counts[key], wanted)
                else:
                    worst[key] = max(worst[key] if key in worst else 0, counts[key])
            # An erased gap passes (ii) and (v), which count only rows ending before they start: the twin's
            # share of zero gaps beside the real's (lane RO's repair 1, the statistics review's item 7).
            cells = _columns(text)
            twin_share, twin_median = _gap_shape(cells)
            if twin_share >= float(f"{value.get(f'keyed_{keyed}_zero_share_twin', -1.0)}"):
                value[f"keyed_{keyed}_zero_share_twin"] = twin_share
                value[f"keyed_{keyed}_median_minutes_twin"] = twin_median
            if real_share < 0.99 and twin_share > real_share + 0.05:
                gap_kept = False
            _readings_of(cells, carried, left, readings)
        for key in worst:
            value[f"keyed_{keyed}_{key}"] = worst[key]
        if keyed == 0:
            text = "".join(rendering.twin_csv_pieces(generation.generate_held(plain, 7)))
            baseline = _event_counts(text)
            for key in baseline:
                value[f"baseline_chain_off_{key}"] = baseline[key]
    value["i_end_before_start"] = value["keyed_0_end_before_start"]
    value["i_days_open_off"] = value["keyed_0_days_open_off"]
    value["ii_closed_before_opened"] = value["keyed_0_closed_before_opened"]
    value["v_phrase_class"] = value["class_keyed_6"] == "phrase"
    value["v_phrase_rows"] = value["keyed_6_closed_before_opened"]
    value["v_count_class"] = value["class_keyed_150"]
    value["v_count_rows"] = value["keyed_150_closed_before_opened"]
    value["ii_gap_kept"] = gap_kept
    seen = []
    chained, loaded, _plain, profiled, described = _describe(folder, "chain", events.CHAIN_HEADER, events.chain_rows(rows), seen=seen)
    seconds["chain"] = {"profile": profiled, "describe_with_rules": described}
    carried, left = _inventory(chained, seen)
    broken: "dict[str, int]" = {}
    if loaded is not None:
        for seed in seeds:
            text, generated, planned, drawn = _twin_text(loaded, seed)
            value["twins"] = int(f"{value['twins']}") + 1
            value["words_off"] = int(f"{value['words_off']}") + abs(planned - drawn)
            counts = _chain_counts(text)
            for key in counts:
                broken[key] = max(broken[key] if key in broken else 0, counts[key])
            _readings_of(_columns(text), carried, left, readings)
    for key in broken:
        value[f"vii_{key}"] = broken[key]
    value["vii_carried"] = [f"{rule['computed']} from {rule['inputs'][0]}" for rule in chained.statistical["rules"]] if chained.statistical else []  # type: ignore[index, union-attr]
    # K-BC-10's PLACED reading, bound here: a carried rule's twin rows other than its class on any twin fails.
    value["rules_placed_checked"] = readings["rules_placed_checked"]
    value["rules_placed_off"] = readings["rules_placed_off"]
    value["seconds"] = seconds
    return value, readings


def inference_seconds(rows: int, columns: int) -> "dict[str, object]":
    """The inference's own seconds on an invented table of numbers, dates and stamps mixed (limit 15's time bar)."""
    import random

    draw = random.Random(11)
    header: "list[str]" = []
    kinds = ("number", "date", "stamp")
    for at in range(columns):
        header += [f"{kinds[at % 3]}_{at}"]
    body: "list[list[str]]" = []
    for _row in range(rows):
        day = draw.randrange(720)
        minute = draw.randrange(720 * 1440)
        line: "list[str]" = []
        for at in range(columns):
            kind = kinds[at % 3]
            if kind == "number":
                line += [f"{draw.randint(0, 200) + at}"]
            elif kind == "date":
                line += [(events._FIRST_DAY + datetime.timedelta(days=day + (at // 3) % 4)).isoformat()]
            else:
                stamp = events._FIRST_STAMP + datetime.timedelta(minutes=minute + 7 * ((at // 3) % 5))
                line += [stamp.strftime("%Y-%m-%d %H:%M")]
        body += [line]
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-time-"))
    path = folder / "wide.csv"
    path.write_text(events.as_text(tuple(header), body), encoding="utf-8", newline="\n")
    body = []
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    started = time.time()
    document = profile.build_document(table, settings, [], [], [])
    profiled = time.time() - started
    timing: "dict[str, float]" = {}
    original = chain_order.infer_rules

    def timed(*arguments):  # type: ignore[no-untyped-def]
        begun = time.time()
        found = original(*arguments)
        timing["inference"] = time.time() - begun
        timing["opened"] = len(found.rules)
        timing["pairs_read"] = found.pairs_read
        return found

    chain_order.infer_rules = timed  # type: ignore[assignment]
    started = time.time()
    chained = chain.describe(table, document, settings, chain.ChainSwitch("wide", TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True))
    described = time.time() - started
    chain_order.infer_rules = original  # type: ignore[assignment]
    return {
        "rows": rows,
        "columns": columns,
        "profile_seconds": round(profiled, 1),
        "describe_seconds_with_rules": round(described, 1),
        "inference_seconds": round(timing["inference"] if "inference" in timing else -1.0, 1),
        "steps_opened": timing["opened"] if "opened" in timing else 0,
        "pairs_read": timing["pairs_read"] if "pairs_read" in timing else 0,
        "rules_carried": chained.counts["rules_carried"] if "rules_carried" in chained.counts else 0,
    }


SHAPES = {
    "stay": (events.STAY_HEADER, events.stay_rows),
    "emergency": (events.EMERGENCY_HEADER, events.emergency_rows),
    "lab": (events.LAB_HEADER, events.lab_rows),
}


def price(shape: str, rows: int, keyed: int, command: bool) -> "dict[str, object]":
    """MR.9's price re-read on the built product: the steps opened, carried by source or derived in the
    phrase or a count, and left uncarried by reason (every reason a word, never a count of real rows)."""
    import os

    from synthtwin import cli

    header, maker = SHAPES[shape]
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-price-"))
    path = folder / f"{shape}.csv"
    path.write_text(events.as_text(header, maker(rows, keyed=keyed)), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    if command:
        here = os.getcwd()
        os.chdir(folder)
        try:
            saved = sys.stdout
            sys.stdout = io.StringIO()
            try:
                cli.main(["profile", path.name])
            finally:
                sys.stdout = saved
        finally:
            os.chdir(here)
        document = json.loads((folder / f"{shape}-profile.json").read_text(encoding="utf-8"))
    else:
        document = profile.build_document(table, settings, [], [], [])
    seen: "list[chain_order.Inference]" = []
    original = chain._rule_steps

    def keeping(inference, switch, names):  # type: ignore[no-untyped-def]
        seen.append(inference)
        return original(inference, switch, names)

    chain._rule_steps = keeping  # type: ignore[assignment]
    started = time.time()
    try:
        chained = chain.describe(table, document, settings, chain.ChainSwitch(shape, TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True))
    finally:
        chain._rule_steps = original  # type: ignore[assignment]
    described = time.time() - started
    plain = chain.describe(table, document, settings, chain.ChainSwitch(shape, TEST_KEY, rows_per_person=chain.ROWS_UNASKED))
    inference = seen[0] if seen else chain_order.Inference((), (), (), 0)
    carried = {rule["computed"]: rule for rule in chained.statistical["rules"]} if chained.statistical else {}  # type: ignore[index, union-attr]
    out: "dict[str, object]" = {
        "shape": shape, "rows": rows, "keyed": keyed, "path": "command" if command else "library",
        "pairs_read": inference.pairs_read, "steps_opened": len(inference.rules),
        "steps_both_read": sum(1 for rule in inference.rules if rule.antecedent),
        "carried": len(carried),
        "carried_source": sum(1 for rule in carried.values() if rule["carrier"] != "derived"),
        "carried_derived": sum(1 for rule in carried.values() if rule["carrier"] == "derived"),
        "carried_phrase": sum(1 for rule in carried.values() if rule["class"] == "phrase"),
        "carried_count": sum(1 for rule in carried.values() if rule["class"] != "phrase"),
        "describe_seconds_with_rules": round(described, 1),
        "eligible_with_rules": chained.counts["eligible_columns"] if "eligible_columns" in chained.counts else 0,
        "eligible_without_rules": plain.counts["eligible_columns"] if "eligible_columns" in plain.counts else 0,
        "near_rules": len(inference.near),
    }
    reasons: "dict[str, int]" = {}
    for rule in inference.rules:
        entry = carried[rule.computed] if rule.computed in carried else None
        if entry is not None and entry["inputs"] == list(rule.inputs):
            continue
        if not rule.antecedent:
            why = "the computed column reads under its input's kind on fewer than f rows"
        elif rule.why:
            why = rule.why
        elif not rule.options:
            why = "no carried option eligible (the derived family refused)"
        else:
            why = "blocked by a rule carried before it, or drawn not carried"
        reasons[why] = reasons[why] + 1 if why in reasons else 1
    out["not_carried_by_reason"] = reasons
    out["carried_rules"] = [
        f"{rule['computed']} from {rule['inputs'][0]} by {rule['carrier']}, class {rule['class']}"
        + (f", level {rule['derived']['name']}" if rule["derived"] else "")
        for rule in carried.values()
    ]
    return out


def _gaps_of(text: str, first: str, second: str) -> "list[int]":
    """The whole-day gaps `second - first` of every row where both are dates."""
    cells = _columns(text)
    out: "list[int]" = []
    for row in range(len(cells[first])):
        a, b = _day(cells[first][row]), _day(cells[second][row])
        if a and b:
            out += [(b - a).days]
    return out


def _quantiles(values: "list[int]") -> "dict[str, int]":
    ordered = sorted(values)
    if not ordered:
        return {}
    return {f"p{p}": ordered[(p * (len(ordered) - 1)) // 100] for p in (50, 90, 99)} | {"max": ordered[-1]}


def stay_agreement(rows: int, seed: int) -> "list[dict[str, object]]":
    """Limit 18: what `(released_on - admitted_on).days == stay_days` reads on the twin at 0, 5, 11, 100
    and 1,000 keyed rows, beside the carrier; limit 8: the gap's tail on the twin against the real table."""
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-stay-"))
    out: "list[dict[str, object]]" = []
    for keyed in (0, 5, 11, 100, 1000):
        real = events.stay_rows(rows, keyed=keyed)
        real_text = events.as_text(events.STAY_HEADER, real)
        chained, loaded, _plain, _profiled, _described = _describe(folder, f"stay{keyed}", events.STAY_HEADER, real)
        carrier = "not carried"
        if chained.statistical is not None:
            for rule in chained.statistical["rules"]:  # type: ignore[union-attr]
                if rule["computed"] == "released_on" and rule["inputs"] == ["admitted_on"]:
                    carrier = f"{rule['carrier']}, class {rule['class']}"
        twin_text = _twin_text(loaded, seed)[0] if loaded is not None else ""
        cells = _columns(twin_text) if twin_text else {}
        agree = 0
        both = 0
        for row in range(len(cells["admitted_on"]) if cells else 0):
            a, b, days = _day(cells["admitted_on"][row]), _day(cells["released_on"][row]), cells["stay_days"][row]
            if a and b and days:
                both += 1
                agree += 1 if (b - a).days == int(days) else 0
        real_cells = _columns(real_text)
        real_agree = sum(
            1 for row in range(len(real_cells["admitted_on"]))
            if real_cells["released_on"][row] and (_day(real_cells["released_on"][row]) - _day(real_cells["admitted_on"][row])).days == int(real_cells["stay_days"][row])  # type: ignore[operator]
        )
        out += [{
            "keyed": keyed, "carrier": carrier,
            "twin_share_agreeing": round(agree / both, 4) if both else None,
            "real_share_agreeing": round(real_agree / rows, 4),
            "twin_gap": _quantiles(_gaps_of(twin_text, "admitted_on", "released_on")) if twin_text else {},
            "real_gap": _quantiles(_gaps_of(real_text, "admitted_on", "released_on")),
        }]
    return out


def heaps(rows: int, seed: int) -> "list[dict[str, object]]":
    """Limit 19 on the product: a heap at 0 and at 7 days with 1 to 21 rows above its top rung, and a heap at
    0 with 190 failing rows and 15 above: carried or not, its level and class, and the twin's rows ending
    before they start (counted, at most the class, as it places them)."""
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-heap-"))
    cases = [(0, above, 0) for above in (1, 5, 11, 12, 15, 21, 22)] + [(7, above, 0) for above in (1, 11, 12, 21, 22)] + [(0, 15, 190), (0, 15, 5), (0, 21, 15)]
    out: "list[dict[str, object]]" = []
    for heap, above, failing in cases:
        made = events.heap_rows(rows, heap_days=heap, above=above, failing=failing)
        chained, loaded, _plain, _profiled, _described = _describe(folder, f"heap{heap}_{above}_{failing}", events.HEAP_HEADER, made)
        carried = "not carried"
        if chained.statistical is not None:
            for rule in chained.statistical["rules"]:  # type: ignore[union-attr]
                if rule["computed"] == "closed_on":
                    carried = f"{rule['carrier']}, class {rule['class']}" + (f", level {rule['derived']['name']}" if rule["derived"] else "")
        broken = 0
        if loaded is not None:
            cells = _columns(_twin_text(loaded, seed)[0])
            for row in range(len(cells["opened_on"])):
                a, b = _day(cells["opened_on"][row]), _day(cells["closed_on"][row])
                if a and b and b < a:
                    broken += 1
        out += [{"heap_days": heap, "above": above, "failing_class_keyed": "the phrase" if failing < FLOOR else failing,
                 "carried": carried, "twin_rows_ending_before_start": "under the floor" if 0 < broken < FLOOR else broken}]
    return out


KEYS = (("k0", TEST_KEY), ("k1", bytes(range(1, 33))), ("k2", bytes([7] * 32)))


def _ruled_table(name: str, rows: int) -> "tuple[tuple[str, ...], list[list[str]]]":
    """The tables of LANE RO RULINGS 3's legs: this file's invented shapes, the battery's survival table and
    two of the zoo's exports, at `rows` rows."""
    import analyst_tables
    import health_zoo

    if name.startswith("event"):
        return events.HEADER, events.event_rows(rows, keyed_rows=int(name[5:]))
    if name == "stay25":
        return events.STAY_HEADER, events.stay_rows(rows, keyed=25)
    if name == "heap":
        return events.HEAP_HEADER, events.heap_rows(rows, heap_days=0, above=21)
    if name == "chain":
        return events.CHAIN_HEADER, events.chain_rows(rows)
    if name == "visit":
        return events.VISIT_HEADER, events.visit_rows(rows)
    if name == "vitals":
        return events.VITALS_HEADER, events.vitals_rows(rows)
    if name == "emergency":
        return events.EMERGENCY_HEADER, events.emergency_rows(rows, keyed=25)
    if name == "lab":
        return events.LAB_HEADER, events.lab_rows(rows, keyed=25)
    if name == "survival":
        cells = list(csv.reader(io.StringIO(analyst_tables.text("ST3", rows, 1))))
        return tuple(cells[0]), cells[1:]
    maker = health_zoo.registry_extract if name == "registry" else health_zoo.encounters
    header, body = maker(rows, 1)
    return tuple(header), body


# Each leg: the table, the rule (computed, input), and what LANE RO RULINGS 3 asks of it under every key.
RULED_LEGS = (
    ("one band (1)", "event6", "closed_at", "opened_at", "no one band"),
    ("one band (1)", "event150", "closed_at", "opened_at", "no one band"),
    ("one band (1)", "stay25", "released_on", "admitted_on", "no one band"),
    ("one band (1)", "registry", "seen_date", "referral_date", "no one band"),
    ("one band (1)", "heap", "closed_on", "opened_on", "carried at one"),
    ("tighter (3)", "chain", "left_at", "arrived_at", "carried"),
    ("association (4)", "visit", "departure", "arrival", "worth"),
    ("association (4)", "stay25", "operated_on", "admitted_on", "worth"),
    ("association (4)", "emergency", "seen_at", "arrived_at", "worth"),
    ("association (4)", "lab", "received_at", "drawn_at", "worth"),
    ("association (4)", "survival", "censor_date", "entry_date", "worth"),
    ("association (4)", "encounters", "discharge_ts", "admit_ts", "worth"),
    ("association (4)", "vitals", "pressure", "pulse", "refused"),
    ("presence (5)", "survival", "event_date", "entry_date", "refused"),
)


def ruled(rows: int) -> "dict[str, object]":
    """LANE RO RULINGS 3's legs at `rows` rows under three keys: each rule's outcome on the library path
    (worth or its reason, the option carried and its level), and whether the ruling's ask holds under all
    three; and on the survival table, the twin's event dates written on censored rows at each key. Each
    table is profiled once and described once a key."""
    folder = pathlib.Path(tempfile.mkdtemp(prefix="kpi-chain-rules-ruled-"))
    out: "dict[str, object]" = {}
    found: "dict[int, list[str]]" = {at: [] for at in range(len(RULED_LEGS))}
    holds: "dict[int, bool]" = {at: True for at in range(len(RULED_LEGS))}
    for name in sorted({leg[1] for leg in RULED_LEGS}):
        header, body = _ruled_table(name, rows)
        path = folder / f"{name}.csv"
        path.write_text(events.as_text(header, body), encoding="utf-8", newline="\n")
        body = []
        settings = taxonomy.Settings(small_cell_floor=FLOOR)
        table = reading.read_table(str(path), small_cell_floor=FLOOR)
        document = profile.build_document(table, settings, [], [], [])
        for label, key in KEYS:
            seen: "list[chain_order.Inference]" = []
            original = chain._rule_steps

            def keeping(inference, switch, names):  # type: ignore[no-untyped-def]
                seen.append(inference)
                return original(inference, switch, names)

            chain._rule_steps = keeping  # type: ignore[assignment]
            try:
                chained = chain.describe(table, document, settings, chain.ChainSwitch(name, key, rows_per_person=chain.ROWS_UNASKED, rules=True))
            finally:
                chain._rule_steps = original  # type: ignore[assignment]
            for at in range(len(RULED_LEGS)):
                _leg, table_name, computed, first, ask = RULED_LEGS[at]
                if table_name != name:
                    continue
                rule = next((one for one in seen[0].rules if one.computed == computed and one.inputs == (first,)), None) if seen else None
                entry = None
                if chained.statistical is not None:
                    for carried in chained.statistical["rules"]:  # type: ignore[union-attr]
                        if carried["computed"] == computed and carried["inputs"] == [first]:
                            entry = carried
                level = entry["derived"]["name"] if entry is not None and entry["derived"] else ("source" if entry is not None else "not carried")
                why = "no step" if rule is None else (rule.why or "worth")
                found[at] += [f"{label}: {why}; {level}"]
                if ask == "no one band":
                    holds[at] = holds[at] and level != "one"
                elif ask == "carried at one":
                    holds[at] = holds[at] and level == "one"
                elif ask == "carried":
                    holds[at] = holds[at] and entry is not None
                elif ask == "worth":
                    holds[at] = holds[at] and why == "worth"
                else:
                    holds[at] = holds[at] and why not in ("worth", "no step")
            if name == "survival" and chained.statistical is not None:
                on = folder / "survival-switched.json"
                on.write_text(canonical.serialize(chain.with_rules(document, chained)), encoding="utf-8", newline="\n")
                twin = _columns("".join(rendering.twin_csv_pieces(generation.generate_held(contract.load_profile(str(on), chain=True), 0))))
                written = sum(1 for status, when in zip(twin["status"], twin["event_date"]) if status == "censored" and when)
                out[f"survival_event_dates_on_censored_rows_{label}"] = written
    for at in range(len(RULED_LEGS)):
        leg, name, computed, first, ask = RULED_LEGS[at]
        out[f"{leg} {name} {computed} from {first}"] = {"ask": ask, "holds": holds[at], "keys": found[at]}
    for item in sorted(folder.iterdir()):
        item.unlink()
    folder.rmdir()
    return out


def main() -> int:
    if "--stay" in sys.argv:
        print(json.dumps(stay_agreement(_argument("--rows", [20000])[0], 0), sort_keys=True))
        return 0
    if "--ruled" in sys.argv:
        print(json.dumps(ruled(_argument("--rows", [20000])[0]), indent=1, sort_keys=True))
        return 0
    if "--heap" in sys.argv:
        print(json.dumps(heaps(_argument("--rows", [20000])[0], 0), sort_keys=True))
        return 0
    if "--price" in sys.argv:
        place = sys.argv.index("--price")
        shape, keyed = sys.argv[place + 1], int(sys.argv[place + 2])
        rows = _argument("--rows", [20000])[0]
        print(json.dumps(price(shape, rows, keyed, "--command" in sys.argv), sort_keys=True))
        return 0
    if "--time" in sys.argv:
        place = sys.argv.index("--time")
        print(json.dumps(inference_seconds(int(sys.argv[place + 1]), int(sys.argv[place + 2])), sort_keys=True))
        return 0
    value, readings = measure(_argument("--rows", [20000])[0], _argument("--seeds", [0, 1, 2]))
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-06", "value": value, "detail": "order rules carried behind the switch (lane RO)"}, sort_keys=True))
        print("KPI " + json.dumps({"id": "K-BC-10", "value": readings, "detail": "the rules' placed and unplaced readings (lane RO)"}, sort_keys=True))
    else:
        print(json.dumps({"K-S6-06": value, "K-BC-10": readings}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
