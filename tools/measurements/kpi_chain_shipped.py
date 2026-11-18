"""K-S6-16's slow part: THE SHIPPED COMMAND'S WALK AT 20,000 ROWS (lane CHON, plan P4-D464).

The switch is on for every shipped run. This driver runs the gate's checks
of `tests/test_stage6_switch_on.py` at the owner's table floor, 20,000
rows, through the shipped command (`cli.run`, no switch handed in, the
table floor on), on three invented tables -- a clinic whose group,
pressure and event follow age; a ward whose stay is its last day less its
first (an order rule); and a visit table whose record number repeats
-- each in a data folder of its own holding the oracle's fixed test key:

- `walked` (exact): the tables walked;
- `held_rounds` (exact): first rounds that published nothing between
  columns and named the question and its file on the screen;
- `chained_rounds` (exact): answered rounds that published a chain;
- `rules_carried` (at least): order or formula rules the answered rounds
  carried, their computed blocks written;
- `one_path` (exact): answered rounds whose description is
  `chain.with_rules` of `chain.describe` over what the command handed it;
- `null_path` (exact): descriptions publishing nothing between columns
  whose twin, report and quality report the shipped and the unswitched
  commands write alike;
- `shared_leaks` (target 0): shared files (description, summary,
  questions file, twin, both reports) holding a refusal's or the hold's
  words, the key, or the private report's words;
- `private_outside` (exact): private reports written in the data folder
  alone, 0700 and 0600 where modes exist;
- `refused_left` (target 0): files, folders or keys a run refused before
  the chain left in a fresh data folder;
- `cpu_seconds`: the process time of each table's answered profile,
  generate and validate, read and printed, never judged here.

    PYTHONPATH=src:tests python tools/measurements/kpi_chain_shipped.py [--kpi] [--rows N]
    PYTHONPATH=src:tests python tools/measurements/kpi_chain_shipped.py --degraded K [--rows N] [--twins]

`--degraded K` (LANE CHON RULINGS 2 (2); contract 4.6b.13, stated limit
4) measures THE DEGRADED CHAIN against the whole one instead of the
walk: an invented table of 40 columns, four families of five that each
follow a shared factor (numbers, three-level labels and binaries cut from
it) and twenty that follow nothing, described once and chained twice
through the library with the shipped switch (the rule steps on, the
subject question answered 'one row each', the 24 partners): whole, and
over at most K columns. It prints the columns kept against the factor
families, the whole chain's family links and published squared
correlations that fall inside the kept columns, each chain's CPU
seconds and description bytes, and with `--twins` each twin's
correlations against the table's (the shipped generate, seed 0): the
mean absolute gap over the pairs inside the kept columns and over the
pairs the degraded chain left out.
"""

import argparse
import contextlib
import hashlib
import io
import json
import os
import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
from synthtwin import asking, chain, cli, installation, profile, results  # noqa: E402

ROWS = 20_000
TEST_KEY = bytes(range(32))
EMPTY_RECORD = '{\n  "tables": [],\n  "version": 1\n}\n'


def _clinic(rows: int, seed: int = 7) -> str:
    draw = random.Random(seed)
    lines = ["age,gender,group,pressure,event"]
    for _row in range(rows):
        age = draw.randint(18, 88)
        group = draw.choice(["a", "b", "c"]) if age < 50 else draw.choice(["c", "d"])
        event = "1" if draw.random() < 0.05 + age / 120 else "0"
        lines += [f"{age},{draw.choice(['f', 'm'])},{group},{round(100 + age * 0.5 + draw.gauss(0, 8), 1)},{event}"]
    return "\n".join(lines) + "\n"


def _ward(rows: int, seed: int = 11) -> str:
    draw = random.Random(seed)
    lines = ["first_day,last_day,stay,ward"]
    for _row in range(rows):
        first = draw.randint(1, 300)
        stay = draw.randint(0, 20)
        lines += [f"{first},{first + stay},{stay},{draw.choice(['north', 'south', 'east'])}"]
    return "\n".join(lines) + "\n"


def _visits(rows: int, seed: int = 5) -> str:
    draw = random.Random(seed)
    lines = ["pid,weight,ward"]
    for row in range(rows):
        lines += [f"P{100000 + row % (rows // 4)},{round(draw.gauss(70, 9), 1)},{draw.choice(['north', 'south'])}"]
    return "\n".join(lines) + "\n"


TABLES = (("clinic", _clinic, True), ("ward", _ward, True), ("visits", _visits, False))


@contextlib.contextmanager
def _installation(place: pathlib.Path, key: bool = True):  # type: ignore[no-untyped-def]
    """XDG_DATA_HOME and LOCALAPPDATA at ``place``, holding the fixed test key and an empty record where ``key``."""
    data = place / installation.FOLDER
    if key:
        data.mkdir(mode=0o700, parents=True)
        (data / installation.KEY_FILE).write_bytes(TEST_KEY)
        (data / installation.LEDGER_FILE).write_text(EMPTY_RECORD, encoding="utf-8", newline="\n")
        if os.name != "nt":
            data.chmod(0o700)
            (data / installation.KEY_FILE).chmod(0o600)
            (data / installation.LEDGER_FILE).chmod(0o600)
    saved = {name: os.environ.get(name) for name in ("XDG_DATA_HOME", "LOCALAPPDATA")}
    os.environ["XDG_DATA_HOME"] = str(place)
    os.environ["LOCALAPPDATA"] = str(place)
    try:
        yield data
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _ran(argv: "list[str]", **named: object) -> "tuple[results.Result, str, float]":
    screen: "list[tuple[str, str]]" = []
    started = time.process_time()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        made = cli.run(argv, screen=screen, **named)  # type: ignore[arg-type]
    return made, "".join(text for _stream, text in screen), time.process_time() - started


def _answered(questions: pathlib.Path) -> None:
    document = json.loads(questions.read_text(encoding="utf-8"))
    document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = asking.ANSWER_ONE_ROW_EACH
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")


def _leaks(folder: pathlib.Path, words: "list[str]") -> int:
    """Shared files of ``folder`` holding any of ``words`` or the key's hex."""
    found = 0
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix not in (".json", ".txt", ".csv"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if TEST_KEY.hex() in text or any(word and word in text for word in words):
            found += 1
    return found


def walk(rows: int, work: pathlib.Path) -> "dict[str, object]":
    """The three tables through the shipped command, each in its own data folder; the record of K-S6-16's slow part."""
    out: "dict[str, object]" = {
        "walked": 0, "held_rounds": 0, "chained_rounds": 0, "rules_carried": 0, "one_path": 0,
        "null_path": 0, "shared_leaks": 0, "private_outside": 0, "refused_left": 0,
    }
    cpu: "dict[str, list[float]]" = {}
    for name, made, draws in TABLES:
        folder = work / name
        folder.mkdir(parents=True)
        table = folder / f"{name}.csv"
        table.write_text(made(rows), encoding="utf-8", newline="\n")
        with _installation(work / f".{name}-installation") as data:
            first, said, _seconds = _ran(["profile", str(table)])
            questions = folder / f"{name}-questions.json"
            described = folder / f"{name}-profile.json"
            # The hold's paragraph opens alike whichever question holds the
            # chain: the subject question, the person question, or the person
            # question naming its columns (lane CHON's repair 1, F2), whose
            # first sentence runs on past "yet".
            opening = "Between columns: nothing is published for this table yet"
            words = [cli._hold_paragraph(cli._WAITS_FOR_SUBJECT, cli._shown(questions)).strip(), cli._AFTER_A_HELD_ROUND, opening]
            if first.verdict in (results.NO_MISS, results.MISSED) and json.loads(described.read_text(encoding="utf-8"))["relationships"]["statistical"] is None and opening in said:
                out["held_rounds"] = int(f"{out['held_rounds']}") + 1
            # THE NULL PATH: the first round's description, built from by the shipped and the unswitched commands.
            alike = []
            for label, setting in (("on", False), ("off", True)):
                where = folder / label
                where.mkdir()
                _ran(["generate", str(described), "--out-dir", str(where)], unswitched=setting)
                checked, _said, _seconds = _ran(["validate", str(described), "--twin", str(where / f"{name}-twin.csv"), "--out-dir", str(where)], unswitched=setting)
                alike += [tuple((where / f"{name}{suffix}").read_bytes() for suffix in ("-twin.csv", "-twin-report.txt", "-twin-quality.txt")) + (results.exit_code(checked),)]
            if alike[0] == alike[1]:
                out["null_path"] = int(f"{out['null_path']}") + 1
            if draws:
                _answered(questions)
                handed: "list[tuple[object, ...]]" = []
                real = chain.describe

                def kept(*given: object, **keyed: object) -> chain.Chained:
                    nonlocal handed
                    handed += [(given, keyed)]
                    return real(*given, **keyed)  # type: ignore[arg-type]

                chain.describe = kept  # type: ignore[assignment]
                try:
                    second, said, seconds = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
                finally:
                    chain.describe = real  # type: ignore[assignment]
                cpu[name] = [round(seconds, 1)]
                statistical = json.loads(described.read_text(encoding="utf-8"))["relationships"]["statistical"]
                if second.verdict in (results.NO_MISS, results.MISSED) and isinstance(statistical, dict) and statistical["chain"]:
                    out["chained_rounds"] = int(f"{out['chained_rounds']}") + 1
                    out["rules_carried"] = int(f"{out['rules_carried']}") + len(statistical["rules"])
                if handed:
                    given, keyed = handed[len(handed) - 1]
                    document = json.loads(json.dumps(given[1]))
                    library = chain.with_rules(document, real(given[0], document, given[2], given[3], *given[4:], **keyed))  # type: ignore[arg-type]
                    if profile.serialize(library) == described.read_text(encoding="utf-8"):
                        out["one_path"] = int(f"{out['one_path']}") + 1
                for command in (["generate", str(described), "--replace"], ["validate", str(described), "--replace"]):
                    _done, _said, seconds = _ran(command)
                    cpu[name] += [round(seconds, 1)]
            out["shared_leaks"] = int(f"{out['shared_leaks']}") + _leaks(folder, words)
            private = data / "private-reports"
            reports = sorted(private.iterdir()) if private.is_dir() else []
            modes = os.name == "nt" or (private.stat().st_mode & 0o777 == 0o700 and all(one.stat().st_mode & 0o777 == 0o600 for one in reports))
            if reports and modes and not [one for one in folder.rglob("*") if "private-report" in one.name]:
                out["private_outside"] = int(f"{out['private_outside']}") + 1
        out["walked"] = int(f"{out['walked']}") + 1
    # A RUN REFUSED BEFORE THE CHAIN LEAVES NOTHING in a fresh data folder:
    # a table under the floor, and a table that is not there.
    fresh = work / ".fresh-installation"
    with _installation(fresh, key=False):
        # In a folder of their own: a data folder inside the table's folder
        # is refused before anything else (lane CHON's repair 1).
        (work / "small").mkdir()
        small = work / "small" / "small.csv"
        small.write_text(_clinic(300), encoding="utf-8", newline="\n")
        _ran(["profile", str(small)], small_tables_refused=True)
        _ran(["profile", str(work / "small" / "nowhere.csv")])
    out["refused_left"] = len(list(fresh.rglob("*"))) if fresh.exists() else 0
    out["cpu_seconds"] = cpu
    return out


FAMILIES = ("a", "b", "c", "d")


def _structured(rows: int, seed: int = 17) -> str:
    """Forty invented columns: four families of five, each following a shared factor, and twenty following nothing."""
    draw = random.Random(seed)
    header = [f"{family}{at}" for family in FAMILIES for at in range(5)] + [f"z{at:02d}" for at in range(20)]
    lines = [",".join(header)]
    for _row in range(rows):
        factors = [draw.gauss(0, 1) for _family in FAMILIES]
        cells: "list[str]" = []
        for place in range(4):
            factor = factors[place]
            for at in range(5):
                if place == 1 and at >= 3:
                    level = factor + draw.gauss(0, 0.6)
                    cells += ["low" if level < -0.5 else ("high" if level > 0.5 else "middle")]
                elif place == 3 and at >= 3:
                    cells += ["1" if factor + draw.gauss(0, 0.7) > 0 else "0"]
                else:
                    cells += [f"{50 + 10 * factor + draw.gauss(0, 4 + at):.1f}"]
        cells += [f"{draw.gauss(50, 7):.1f}" for _at in range(15)]
        cells += [draw.choice(["n", "s", "e", "w"]) for _at in range(5)]
        lines += [",".join(cells)]
    return "\n".join(lines) + "\n"


def _correlations(path: pathlib.Path, names: "list[str]") -> "dict[tuple[str, str], float]":
    """Each pair of ``names``' Pearson correlation over the rows of ``path`` holding both as numbers."""
    import csv

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        places = [header.index(name) for name in names]
        columns: "list[list[float | None]]" = [[] for _name in names]
        for row in reader:
            for at, place in enumerate(places):
                try:
                    columns[at] += [float(row[place])]
                except (ValueError, IndexError):
                    columns[at] += [None]
    out: "dict[tuple[str, str], float]" = {}
    for first in range(len(names)):
        for second in range(first):
            pairs = [(x, y) for x, y in zip(columns[first], columns[second]) if x is not None and y is not None]
            n = len(pairs)
            if n < 3:
                continue
            mx = sum(x for x, _y in pairs) / n
            my = sum(y for _x, y in pairs) / n
            sxx = sum((x - mx) ** 2 for x, _y in pairs)
            syy = sum((y - my) ** 2 for _x, y in pairs)
            sxy = sum((x - mx) * (y - my) for x, y in pairs)
            if sxx > 0 and syy > 0:
                out[(names[first], names[second])] = sxy / (sxx * syy) ** 0.5
    return out


def degraded(rows: int, at_most: int, work: pathlib.Path, twins: bool) -> "dict[str, object]":
    """THE DEGRADED CHAIN against the whole one on the structured table (LANE CHON RULINGS 2 (2)); every value MEASURED."""
    from synthtwin import reading, taxonomy

    table_path = work / "structured.csv"
    table_path.write_text(_structured(rows), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    table = reading.read_table(str(table_path))
    started = time.process_time()
    document = profile.build_document(table, settings, [], [], [])
    out: "dict[str, object]" = {"rows": rows, "at_most": at_most, "plain_describe_cpu_seconds": round(time.process_time() - started, 1)}
    found: "dict[str, dict[str, object]]" = {}
    for label, bound in (("whole", 0), ("degraded", at_most)):
        handed = json.loads(json.dumps(document))
        switch = chain.ChainSwitch(
            "structured", TEST_KEY, rows_per_person=chain.ROWS_ONE, rules=True, columns_at_most=bound
        )
        started = time.process_time()
        chained = chain.describe(table, handed, settings, switch)
        seconds = round(time.process_time() - started, 1)
        written = chain.with_rules(handed, chained)
        statistical = written["relationships"]["statistical"]
        assert isinstance(statistical, dict), chained.notes
        found[label] = statistical
        out[f"{label}_cpu_seconds"] = seconds
        out[f"{label}_description_bytes"] = len(profile.serialize(written).encode("utf-8"))
        out[f"{label}_families"] = len(statistical["chain"])
        if twins:
            folder = work / label
            folder.mkdir()
            described = folder / "structured-profile.json"
            described.write_text(profile.serialize(written), encoding="utf-8", newline="\n")
            made, _said, generate_seconds = _ran(["generate", str(described), "--out-dir", str(folder), "--seed", "0"])
            out[f"{label}_generate_cpu_seconds"] = round(generate_seconds, 1)
            out[f"{label}_generate_exit"] = results.exit_code(made)
    kept = [entry["column"] for entry in found["degraded"]["ladder"]]
    in_families = [f"{family}{at}" for family in FAMILIES for at in range(5)]
    out["kept"] = kept
    out["kept_in_families"] = len([name for name in kept if name in in_families])
    out["kept_unrelated"] = len([name for name in kept if name not in in_families])
    links = [(family["child"], parent["column"]) for family in found["whole"]["chain"] for parent in family["parents"]]
    out["whole_links"] = len(links)
    out["whole_links_kept"] = len([link for link in links if link[0] in kept and link[1] in kept])
    moments = found["whole"]["moments"]
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"] if isinstance(moments, dict) else []
    total = 0.0
    inside = 0.0
    if isinstance(moments, dict):
        for row in range(len(numbers)):
            for other in range(row):
                pair = moments["correlations"][row][other]
                if pair:
                    square = (pair[0] / 10**12) ** 2
                    total += square
                    if numbers[row] in kept and numbers[other] in kept:
                        inside += square
    out["whole_r_squared"] = round(total, 4)
    out["whole_r_squared_kept"] = round(inside, 4)
    if twins:
        real = _correlations(table_path, numbers)
        for label in ("whole", "degraded"):
            twin = _correlations(work / label / "structured-twin.csv", numbers)
            gaps_in = [abs(twin[pair] - real[pair]) for pair in real if pair in twin and pair[0] in kept and pair[1] in kept]
            gaps_out = [abs(twin[pair] - real[pair]) for pair in real if pair in twin and not (pair[0] in kept and pair[1] in kept)]
            gaps_families = [abs(twin[pair] - real[pair]) for pair in real if pair in twin and pair[0][0] == pair[1][0] and pair[0] in in_families]
            out[f"{label}_twin_gap_kept_pairs"] = round(sum(gaps_in) / max(1, len(gaps_in)), 4)
            out[f"{label}_twin_gap_other_pairs"] = round(sum(gaps_out) / max(1, len(gaps_out)), 4)
            out[f"{label}_twin_gap_within_families"] = round(sum(gaps_families) / max(1, len(gaps_families)), 4)
    return out


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line kpi_run.py reads")
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--degraded", type=int, default=0, help="measure the degraded chain over at most this many columns")
    parser.add_argument("--twins", action="store_true", help="with --degraded, generate both twins and read their correlations")
    args = parser.parse_args(argv)
    if args.degraded:
        with tempfile.TemporaryDirectory(prefix="kpi-chain-degraded-") as made:
            with _installation(pathlib.Path(made) / ".installation"):
                print(json.dumps(degraded(args.rows, args.degraded, pathlib.Path(made), args.twins), sort_keys=True))
        return 0
    with tempfile.TemporaryDirectory(prefix="kpi-chain-shipped-") as made:
        found = walk(args.rows, pathlib.Path(made))
    found["rows"] = args.rows
    digest = hashlib.sha256(json.dumps(found, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    print(json.dumps(found, sort_keys=True))
    if args.kpi:
        value = {key: found[key] for key in found if key not in ("cpu_seconds",)}
        print("KPI " + json.dumps({"id": "K-S6-16", "value": value, "detail": f"cpu_seconds {found['cpu_seconds']}; record {digest}"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
