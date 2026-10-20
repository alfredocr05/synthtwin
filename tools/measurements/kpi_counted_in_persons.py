"""K-S3-65: published values fewer than eleven people hold, on tables of several rows a person (plan P4-D406).

Runs long tables through the real `synthtwin profile` (scripted, whatever
terminal this is started from: nothing answered), `generate` (seed 0) and
`validate`, and counts with `tests/persons_counted.py` -- written apart from
the product's own count -- every value of a column but the subject columns
(the declared person columns and every column an open question offering
`identifier` holds, that repeat, of any number of different values, each
read with its spellings merged) that the description
publishes and one to ten subjects hold, in the rule's scope (a column
attached to the subject or of dates or times of day, or a value eleven
rows and more hold published off the points along the range), with the
written forms it names, its remainder and present rows, a record number's
layout pool, and the person
column's census of rows a person (`persons_counted.count`). Target 0; and
no twin misses its own validation where the twin made without the count
meets its own, but the generator's named limits (`GENERATOR_LIMITS`,
counted apart as `twins_failing_validation_stated`).

Recorded beside it, never failed, per battery: `literal`, the published
values one to ten subjects hold whatever their rows (the points of a
measurement a patient holds on a row or two, judged as on a table of one
row a person), and `withheld`, the values the count withholds that the row
floor alone publishes (each table profiled again with the count off).

THE BATTERIES. `shapes`: K-S3-64's long tables (`tests/unanswered_identifier_
shapes.py`) -- the held shapes at 600 rows, the shapes beside a declared
person column and the counted shapes at 600 and 20,000. `people`: the
population floor's repeated-measures tables with declared people and the
person question's four negatives (`tests/kpi_shapes.py`), and the gate's
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
import typing

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


@contextlib.contextmanager
def count_off() -> "typing.Iterator[None]":
    """The product with the count in people switched off: the row floor alone."""
    saved = (profile._counted_in_subjects, profile._layouts_in_subjects,
             taxonomy.with_census_in_people)
    profile._counted_in_subjects = lambda *_a, **_k: False  # type: ignore[assignment]
    profile._layouts_in_subjects = lambda described, *_a, **_k: described  # type: ignore[assignment]
    taxonomy.with_census_in_people = lambda column, *_a, **_k: column  # type: ignore[assignment]
    try:
        yield
    finally:
        (profile._counted_in_subjects, profile._layouts_in_subjects,
         taxonomy.with_census_in_people) = saved


# THE GENERATOR'S STATED LIMITS (plan P4-D406, lane CODES-1 part C): a
# table whose twin misses its own validation because the identifier
# generator writes a held column's withheld pool in a stand-in that moves
# the column's layout reading (`@----` beside 578 five-figure codes, the
# catalogue's diagnoses table at 600 rows, a code column held beside the
# person question's code candidates). Counted apart, named, never failed.
#
# ...and a column of names written in capitals on some rows (lane HX2's
# skeptic, round 2, item 5): held, its layouts -- five and more beside a
# pool -- met by an even census the identifier generator's packing walk
# does not always find, so its twin misses a few rows of each named
# layout at 2,000 and 20,000 rows; and the catalogue's patients table,
# unanswered, whose `gender_code` and `ancestry` are held beside its ZIP
# codes, themselves held until their question is answered (round 2,
# item 1's price): the twin misses those columns' layouts.
GENERATOR_LIMITS = ("z-diagnoses_procedures", "z-patients", "g-caps-2000", "g-caps-20000")

# THE COVERAGE EACH BATTERY MUST REACH (Codex's review of lane HX2, item
# 13): the tables with a subject column the run counted, battery by battery.
# A table the counter could not read, or the profile refused, is counted
# against its battery's coverage unless it is named below with its reason,
# and fewer tables than these is `coverage_short` -- never a green run on
# lost coverage. The catalogue must be on the path.
EXPECTED_TABLES = {"shapes": 0, "people": 0, "zoo": 0}
# The tables a battery may lose, each named with why: none.
PERMITTED_NOT_COUNTED: "dict[str, str]" = {}


def _one(table: pathlib.Path, folder: pathlib.Path, declared: "list[str]") -> "dict[str, object]":
    """Profile with the count and without it; count, generate and validate the counted one."""
    ruled = folder / "on"
    plain = folder / "off"
    ruled.mkdir()
    plain.mkdir()
    stem = table.name[: -len(".csv")]
    if _quiet(["profile", f"{table}", "--out-dir", f"{ruled}", "--replace"] + declared) != 0:
        return {"skipped": True}
    with count_off():
        _quiet(["profile", f"{table}", "--out-dir", f"{plain}", "--replace"] + declared)
    found = persons_counted.count_files(table, ruled)
    found["withheld"] = persons_counted.withheld_values(table, ruled, plain)
    described = ruled / f"{stem}-profile.json"
    found["generated"] = _quiet(["generate", f"{described}", "--out-dir", f"{ruled}",
                                 "--seed", "0", "--replace"])
    found["validated"] = _quiet(["validate", f"{described}", "--twin",
                                 f"{ruled / (stem + '-twin.csv')}", "--out-dir",
                                 f"{ruled}", "--replace"])
    # A twin missing its own validation is the count's only where the
    # twin of the description made without it meets its own.
    found["validated_without"] = 0
    if found["validated"] != 0:
        alone = plain / f"{stem}-profile.json"
        _quiet(["generate", f"{alone}", "--out-dir", f"{plain}", "--seed", "0", "--replace"])
        found["validated_without"] = _quiet(["validate", f"{alone}", "--twin",
                                             f"{plain / (stem + '-twin.csv')}",
                                             "--out-dir", f"{plain}", "--replace"])
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
    # Lane HX2's second repair (skeptic 1, round 2): two record systems in
    # one person column, a plan written apart for three patients (one
    # person column declared, then two), spellings of one key, and names
    # in capitals on some rows.
    for stem, text, declared in (
        ("systems-2000", persons_counted.two_systems_table(2000), ["--identifier", "patient"]),
        ("systems-20000", persons_counted.two_systems_table(20000), ["--identifier", "patient"]),
        ("plans-20000", persons_counted.plan_rare_table(20000), ["--identifier", "patient"]),
        ("plans2-20000", persons_counted.plan_rare_table(20000),
         ["--identifier", "patient", "--identifier", "x"]),
        ("spelled-2000", persons_counted.spellings_table(2000), []),
        ("caps-2000", persons_counted.capitals_table(2000), []),
        ("caps-20000", persons_counted.capitals_table(20000), []),
    ):
        home = scratch / f"g-{stem}"
        home.mkdir()
        path = home / "x.csv"
        path.write_text(text, encoding="utf-8", newline="\n")
        found += [("people", path, declared)]
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


value: "dict[str, object]" = {"few": 0, "twins_failing_validation": 0, "tables": 0,
                              "not_counted": 0, "skipped": 0, "coverage_short": 0}
counted: "dict[str, int]" = {"shapes": 0, "people": 0, "zoo": 0}
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
        except Exception as failure:  # noqa: BLE001 -- every failure is named and judged
            # A table the counter cannot read is named, and fails the KPI
            # unless PERMITTED_NOT_COUNTED names it with its reason.
            lines += [f"{battery:7s} {path.parent.name}: not counted ({type(failure).__name__})"]
            if path.parent.name not in PERMITTED_NOT_COUNTED:
                value["not_counted"] = int(value["not_counted"]) + 1
            continue
        if found.get("skipped"):
            lines += [f"{battery:7s} {path.parent.name}: profile refused it"]
            if path.parent.name not in PERMITTED_NOT_COUNTED:
                value["skipped"] = int(value["skipped"]) + 1
            continue
        if not found["subjects"]:
            continue
        value["tables"] = int(value["tables"]) + 1
        counted[battery] = counted[battery] + 1
        value["few"] = int(value["few"]) + int(found["few"])
        if (found["validated"] != 0 and found["validated_without"] == 0
                and path.parent.name in GENERATOR_LIMITS):
            value["twins_failing_validation_stated"] = int(
                value.get("twins_failing_validation_stated", 0)) + 1
        elif found["validated"] != 0 and found["validated_without"] == 0:
            value["twins_failing_validation"] = int(value["twins_failing_validation"]) + 1
        elif found["validated"] != 0:
            value["twins_failing_without_it_too"] = int(
                value.get("twins_failing_without_it_too", 0)) + 1
        for key in ("literal", "withheld"):
            name = f"{key}_{battery}"
            value[name] = int(value.get(name, 0)) + int(found[key])
        lines += [f"{battery:7s} {path.parent.name}: subjects {found['subjects']}, few "
                  f"{found['few']} {found['named'][:3]}, literal {found['literal']}, withheld "
                  f"{found['withheld']}, validate {found['validated']} "
                  f"(without the count {found['validated_without']})"]
    value["zoo_on_this_tree"] = zoo_measured
for battery in sorted(counted):
    value[f"tables_{battery}"] = counted[battery]
    if counted[battery] < EXPECTED_TABLES[battery]:
        value["coverage_short"] = int(value["coverage_short"]) + 1
        lines += [f"{battery:7s} COVERAGE SHORT: {counted[battery]} tables, "
                  f"{EXPECTED_TABLES[battery]} expected"]
for line in lines:
    print(line)
kpi_rules.emit("K-S3-65", value, f"{value['tables']} tables with a subject column")
