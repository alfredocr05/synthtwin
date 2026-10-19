"""K-S3-65: published values fewer than eleven people hold, on tables of several rows a person (plan P4-D406).

Runs long tables through the real `synthtwin profile` (scripted, whatever
terminal this is started from: nothing answered), `generate` (seed 0) and
`validate`, and counts with `tests/persons_counted.py` -- written apart from
the product's own count -- every value of a column but the subject columns
(the declared person columns and the open person question's candidates)
that the description publishes and one to ten subjects hold, in the rule's
scope (a column attached to the subject, or a value eleven rows and more
hold published off the points along the range). Target 0.

Recorded beside it, never failed, per battery: `literal`, the published
values one to ten subjects hold whatever their rows (the points of a
measurement a patient holds on a row or two, judged as on a table of one
row a person), and `withheld`, the values the count withholds that the row
floor alone publishes (each table profiled again with the count off).

THE BATTERIES. `shapes`: K-S3-64's long tables (`tests/unanswered_identifier_
shapes.py`) -- the held shapes at 600 rows, the shapes beside a declared
person column and the counted shapes at 600 and 20,000. `people`: the
population floor's repeated-measures tables with declared people and the
person question's four negatives (`tests/kpi_shapes.py`), and the gate's two
tables (`tests/persons_counted.py`). `zoo`: the healthcare catalogue's
tables (`tests/health_zoo.py`, where this tree has it), profiled unanswered.
About ten minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_counted_in_persons.py --kpi
"""

import contextlib
import io
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import kpi_shapes  # noqa: E402
import persons_counted  # noqa: E402
import unanswered_identifier_shapes as shapes  # noqa: E402
from synthtwin import cli, profile, taxonomy  # noqa: E402


def _quiet(argv: "list[str]") -> int:
    sink = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            return cli.main(argv)


def _rule_off(described: object, *_args: object, **_kwargs: object) -> object:
    return described


def _one(table: pathlib.Path, folder: pathlib.Path, declared: "list[str]") -> "dict[str, object]":
    """Profile with the count and without it; count, generate and validate the counted one."""
    ruled = folder / "on"
    plain = folder / "off"
    ruled.mkdir()
    plain.mkdir()
    stem = table.name[: -len(".csv")]
    if _quiet(["profile", f"{table}", "--out-dir", f"{ruled}", "--replace"] + declared) != 0:
        return {"skipped": True}
    counted, census = profile._counted_in_subjects, taxonomy.with_even_census
    profile._counted_in_subjects = _rule_off  # type: ignore[assignment]
    taxonomy.with_even_census = lambda column: column  # type: ignore[assignment]
    try:
        _quiet(["profile", f"{table}", "--out-dir", f"{plain}", "--replace"] + declared)
    finally:
        profile._counted_in_subjects, taxonomy.with_even_census = counted, census
    found = persons_counted.count_files(table, ruled)
    found["withheld"] = persons_counted.withheld_values(table, ruled, plain)
    described = ruled / f"{stem}-profile.json"
    found["generated"] = _quiet(["generate", f"{described}", "--out-dir", f"{ruled}",
                                 "--seed", "0", "--replace"])
    found["validated"] = _quiet(["validate", f"{described}", "--twin",
                                 f"{ruled / (stem + '-twin.csv')}", "--out-dir",
                                 f"{ruled}", "--replace"])
    return found


def _tables(scratch: pathlib.Path) -> "list[tuple[str, pathlib.Path, list[str]]]":
    found: "list[tuple[str, pathlib.Path, list[str]]]" = []
    for kind in shapes.HELD:
        sizes = (600,)
        for rows in sizes:
            home = scratch / f"t-{kind}-{rows}"
            home.mkdir()
            path, _real = shapes.write_table(home, kind, rows)
            found += [("shapes", path, [])]
    for kind in shapes.BESIDE + shapes.COUNTED:
        for rows in (600, 20000):
            home = scratch / f"t-{kind}-{rows}"
            home.mkdir()
            path, _real = shapes.write_table(home, kind, rows)
            declared = ["--identifier", "patient"] if kind.endswith("_beside") else []
            found += [("shapes", path, declared)]
    for name, rows, people, declared in kpi_shapes.POPULATION_BATTERY:
        if people is None or not declared or rows < 100:
            continue
        home = scratch / f"p-{rows}-{people}"
        home.mkdir()
        path = home / "visits.csv"
        path.write_text(kpi_shapes.visits_table(rows, people), encoding="utf-8", newline="\n")
        found += [("people", path, ["--identifier", "subject_id"])]
    for _said, name, different, rows in kpi_shapes.PERSON_QUESTION_NEGATIVES:
        home = scratch / f"n-{name}-{different}"
        home.mkdir()
        path = home / f"{name}.csv"
        path.write_text(kpi_shapes.label_table(name, different, rows), encoding="utf-8", newline="\n")
        found += [("people", path, [])]
    for stem, text in (("two", persons_counted.two_candidates(600)),
                       ("sites", persons_counted.site_table(1200))):
        home = scratch / f"g-{stem}"
        home.mkdir()
        path = home / f"{stem}.csv"
        path.write_text(text, encoding="utf-8", newline="\n")
        found += [("people", path, ["--identifier", "patient"] if stem == "sites" else [])]
    return found


def _zoo(scratch: pathlib.Path) -> "list[tuple[str, pathlib.Path, list[str]]]":
    try:
        import health_zoo  # noqa: PLC0415
    except ImportError:
        return []
    found: "list[tuple[str, pathlib.Path, list[str]]]" = []
    for place, table in enumerate(health_zoo.runnable_tables()):
        if table.suffix != ".csv":
            continue
        home = scratch / f"z-{table.name}"
        home.mkdir()
        path = health_zoo.write_table(table, home, 600, 20261016 + place)
        found += [("zoo", pathlib.Path(path), [])]
    return found


value: "dict[str, object]" = {"few": 0, "twins_failing_validation": 0, "tables": 0}
lines: "list[str]" = []
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    tables = _tables(scratch) + _zoo(scratch)
    zoo_measured = any(battery == "zoo" for battery, _path, _declared in tables)
    for battery, path, declared in tables:
        folder = path.parent / "runs"
        folder.mkdir()
        try:
            found = _one(path, folder, declared)
        except (UnicodeDecodeError, ValueError, IndexError, KeyError) as failure:
            # The counter reads a table back as UTF-8 and commas; a zoo
            # table written otherwise (a file-level kind) is named, never
            # counted as clean.
            lines += [f"{battery:7s} {path.parent.name}: not counted ({type(failure).__name__})"]
            value["not_counted"] = int(value.get("not_counted", 0)) + 1
            continue
        if found.get("skipped"):
            lines += [f"{battery:7s} {path.parent.name}: profile refused it"]
            continue
        if not found["subjects"]:
            continue
        value["tables"] = int(value["tables"]) + 1
        value["few"] = int(value["few"]) + int(found["few"])
        if found["validated"] != 0:
            value["twins_failing_validation"] = int(value["twins_failing_validation"]) + 1
        for key in ("literal", "withheld"):
            name = f"{key}_{battery}"
            value[name] = int(value.get(name, 0)) + int(found[key])
        lines += [f"{battery:7s} {path.parent.name}: subjects {found['subjects']}, few "
                  f"{found['few']} {found['named'][:3]}, literal {found['literal']}, withheld "
                  f"{found['withheld']}, validate {found['validated']}"]
    value["zoo_on_this_tree"] = zoo_measured
for line in lines:
    print(line)
kpi_rules.emit("K-S3-65", value, f"{value['tables']} tables with a subject column")
