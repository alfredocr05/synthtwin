"""The KPI ledger's rules: how a measured value is judged, and the ledger's own honesty.

The owner, 2026-09-18: "take note of the KPIs of each thing developed on
each phase and stage. This is the way that, in the future, when we will
be stages ahead from here, we will rerun everything and know that nothing
behind is broken!"

`tests/kpi/ledger.json` is the single record. Three readers share this
module so that they can never judge the same value two ways:

* `tests/test_kpi_ledger.py` -- every KPI measured by a test of its own
  asserts the ledger's rule through `judge` and records the value;
* `tests/test_kpi_ledger_integrity.py` -- the honesty guard, which runs
  `integrity_problems` on the committed ledger;
* `tools/measurements/kpi_run.py` -- the one command that prints every
  KPI against its rule and exits non-zero on any drop.

WHAT A VERDICT MEANS. A GREEN entry passes when its value meets its rule.
An OPEN or ACCEPTED_LIMIT entry's `expected` is its MUST-NOT-GET-WORSE
bound: it is "held" at or inside that bound and "worse" outside it, and
an OPEN entry whose value also meets its `target` is IMPROVED, which asks
for the status to be flipped to GREEN and never fails a run. Seconds are
judged only on the reference machine; anywhere else a seconds rule warns
and the machine-free ratio or count beside it is what can fail.

Standard library only, so the runner can load it before pytest runs.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import os
import pathlib
import platform
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "tests" / "kpi" / "ledger.json"
LEDGER_TEST_FILE = "tests/test_kpi_ledger.py"
MEASUREMENTS = REPO_ROOT / "tools" / "measurements"

# The closed enumerations of the ledger. Each is stated here once and
# the integrity guard holds every entry to it.
CATEGORIES = ("CODE", "STATS", "PRIVACY", "SPEED", "TRUST")
STATUSES = ("GREEN", "OPEN", "ACCEPTED_LIMIT")
TIERS = ("FAST", "SLOW")
SOURCES = ("pytest", "driver")
RULE_KINDS = (
    "exact",
    "at_most",
    "at_least",
    "ratio_below",
    "seconds_below",
    "band",
)
# The phases and stages an id may name. P0-P4 are the closed phases,
# S1 and S2 the stages of reopened Phase 4, 2B stage 2b, and S3-S8 the
# stages still to come, whose stage checks may be measured early as baselines.
ID_PATTERN = re.compile(r"^K-(P[0-4]|S[1-8]|2B)-(\d\d)([a-z])?$")
HEADLINES_AT_LEAST = 20
HEADLINES_AT_MOST = 30

# Verdict words, printed by the runner and stored in its report.
PASS = "PASS"
PASS_DRIFT = "PASS-DRIFT"
FAIL = "FAIL"
OPEN_HELD = "OPEN-held"
OPEN_WORSE = "OPEN-WORSE"
IMPROVED = "IMPROVED"
ACCEPTED_HELD = "ACCEPTED-held"
ACCEPTED_WORSE = "ACCEPTED-WORSE"
NOT_RUN = "NOT-RUN(slow)"
NOT_MEASURED = "NOT-MEASURED"
DROPS = (FAIL, OPEN_WORSE, ACCEPTED_WORSE)


def load_ledger(path: "pathlib.Path | None" = None) -> "dict":
    """The ledger document, read strictly (a duplicate key is refused)."""

    def no_duplicates(pairs: "list[tuple[str, object]]") -> "dict":
        seen: "dict" = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"ledger: key {key!r} appears twice")
            seen[key] = value
        return seen

    text = (path or LEDGER_PATH).read_text(encoding="utf-8")
    return json.loads(text, object_pairs_hook=no_duplicates)


def entries_by_id(ledger: "dict") -> "dict[str, dict]":
    """The entries keyed by id."""
    return {entry["id"]: entry for entry in ledger["entries"]}


def owned_test_name(entry_id: str) -> str:
    """The one test function a NEW_FAST_TEST entry owns: K-P2-05 -> test_k_p2_05."""
    return "test_" + entry_id.lower().replace("-", "_")


def group_of(entry_id: str) -> str:
    """The phase or stage an id names: K-2B-14 -> 2B."""
    return entry_id.split("-")[1]


def on_reference_machine(ledger: "dict") -> bool:
    """Whether seconds may fail here: the machine and the core count match."""
    wanted = ledger["reference_machine"]
    return (
        platform.machine() == wanted["platform_machine"]
        and os.cpu_count() == wanted["cores"]
    )


# -- judging one value --------------------------------------------------


def _meets(kind: str, value: object, bound: object) -> bool:
    """One number against one bound under one rule kind."""
    if isinstance(value, bool) or isinstance(bound, bool):
        return value == bound
    if kind == "exact":
        return value == bound
    if not isinstance(value, (int, float)):
        return False
    if kind == "at_most":
        return value <= bound  # type: ignore[operator]
    if kind == "at_least":
        return value >= bound  # type: ignore[operator]
    if kind in ("ratio_below", "seconds_below"):
        return value < bound  # type: ignore[operator]
    if kind == "band":
        low, high = bound  # type: ignore[misc]
        return low <= value <= high
    raise ValueError(f"unknown rule kind {kind!r}")


def _misses(
    kind: str,
    kinds: "dict[str, str]",
    value: object,
    bounds: object,
    seconds_count: bool,
    partial: bool,
) -> "list[str]":
    """Every part of ``value`` outside ``bounds``, named.

    A dict of bounds judges each named key and leaves the value's other
    keys as recorded context. A key whose kind is seconds_below is
    skipped off the reference machine. A key the value does not carry is
    a miss, unless the measurement is ``partial`` (a slow driver was not
    run), in which case it is skipped: the runner says which.
    """
    if isinstance(bounds, dict):
        if not isinstance(value, dict):
            return [f"value {value!r} is not the keyed value the rule names"]
        out = []
        for key in sorted(bounds):
            this_kind = kinds.get(key, kind)
            if this_kind == "seconds_below" and not seconds_count:
                continue
            if key not in value:
                if not partial:
                    out.append(f"{key}: not measured")
            elif not _meets(this_kind, value[key], bounds[key]):
                out.append(f"{key}={value[key]!r} vs {this_kind} {bounds[key]!r}")
        return out
    if kind == "seconds_below" and not seconds_count:
        return []
    if not _meets(kind, value, bounds):
        return [f"{value!r} vs {kind} {bounds!r}"]
    return []


class Verdict:
    """What the ledger says about one measured value."""

    def __init__(self, word: str, message: str) -> None:
        self.word = word
        self.message = message

    @property
    def is_drop(self) -> bool:
        """True where the run must fail: a GREEN miss or a bound made worse."""
        return self.word in DROPS

    def __repr__(self) -> str:
        return f"Verdict({self.word!r}, {self.message!r})"


def judge(
    entry: "dict",
    value: object,
    seconds_count: bool = True,
    partial: bool = False,
) -> Verdict:
    """Judge a measured value against the entry's rule, bound and target.

    ``partial`` is True where only part of the entry was measured -- a
    KPI test judging its own keys, or a fast run that skipped the entry's
    slow driver -- so a key nobody measured is left out, not failed.
    """
    kind = entry["rule_kind"]
    kinds = entry.get("key_kinds", {})
    misses = _misses(kind, kinds, value, entry["expected"], seconds_count, partial)
    status = entry["status"]
    if status == "GREEN":
        if misses:
            return Verdict(FAIL, "; ".join(misses))
        drift = entry.get("drift")
        if drift is not None:
            drifted = _misses(drift["rule_kind"], {}, value, drift["expected"], True, partial)
            if drifted:
                return Verdict(PASS_DRIFT, "; ".join(drifted))
        return Verdict(PASS, "meets its rule")
    if status == "OPEN":
        if misses:
            return Verdict(OPEN_WORSE, "worse than its bound: " + "; ".join(misses))
        target = entry.get("target")
        if target is not None and not _misses(
            entry.get("target_kind", kind), kinds, value, target, seconds_count, False
        ):
            return Verdict(
                IMPROVED,
                "meets its target: flip its status to GREEN in the ledger",
            )
        return Verdict(OPEN_HELD, "held at or inside its bound")
    if misses:
        return Verdict(ACCEPTED_WORSE, "worse than its bound: " + "; ".join(misses))
    return Verdict(ACCEPTED_HELD, "held at or inside its bound")


# -- the ledger's own honesty ----------------------------------------


def split_node(node: str) -> "tuple[str, str]":
    """'tests/f.py::func' -> ('tests/f.py', 'func')."""
    path, _sep, name = node.partition("::")
    return path, name


_PARSED: "dict[tuple[str, int, int], frozenset[str]]" = {}


def functions_in(path: pathlib.Path) -> "frozenset[str]":
    """The names of every function defined anywhere in a Python file.

    Parsed once per file version (its path, size and modification time),
    so the guard and its mutation tests do not re-parse the suite.
    """
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in _PARSED:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        _PARSED[key] = frozenset(
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
    return _PARSED[key]


def driver_script(command: str) -> str:
    """'tools/measurements/x.py --kpi' -> 'tools/measurements/x.py'."""
    return command.split()[0]


def readme_rows() -> "set[str]":
    """The scripts named in the first cell of a row of the measurements README."""
    text = (MEASUREMENTS / "README.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| `([^`]+\.py)` \|", text, flags=re.MULTILINE))


def integrity_problems(ledger: "dict", root: pathlib.Path = REPO_ROOT) -> "list[str]":
    """Every way the ledger fails its own design, named. Empty means honest."""
    problems: "list[str]" = []
    entries = ledger["entries"]
    ids = [entry["id"] for entry in entries]
    for entry_id in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"{entry_id}: the id appears more than once")
    cache: "dict[str, frozenset[str]]" = {}

    def names_in(relative: str) -> "frozenset[str] | None":
        if relative not in cache:
            target = root / relative
            if not target.is_file():
                return None
            cache[relative] = functions_in(target)
        return cache[relative]

    readme = readme_rows() if root == REPO_ROOT else set()
    owned_tests = set()
    for entry in entries:
        entry_id = entry["id"]
        if not ID_PATTERN.match(entry_id):
            problems.append(f"{entry_id}: the id is not K-<phase or stage>-nn")
        for field, allowed in (
            ("category", CATEGORIES),
            ("status", STATUSES),
            ("tier", TIERS),
            ("source", SOURCES),
            ("rule_kind", RULE_KINDS),
        ):
            if entry.get(field) not in allowed:
                problems.append(f"{entry_id}: {field} {entry.get(field)!r} is not one of {allowed}")
        for kind in entry.get("key_kinds", {}).values():
            if kind not in RULE_KINDS:
                problems.append(f"{entry_id}: key kind {kind!r} is not a rule kind")
        if not isinstance(entry.get("headline"), bool):
            problems.append(f"{entry_id}: headline must be true or false")
        if entry.get("status") == "OPEN" and not entry.get("target_stage"):
            problems.append(f"{entry_id}: an OPEN entry names the stage that closes it")
        if "value_at" not in entry or "commit" not in entry["value_at"]:
            problems.append(f"{entry_id}: the value is recorded with no commit")
        measured_by = 0
        for node in entry.get("nodes", []):
            measured_by += 1
            path, name = split_node(node)
            if "[" in node or not name:
                problems.append(f"{entry_id}: node {node!r} is not 'file::function'")
                continue
            names = names_in(path)
            if names is None:
                problems.append(f"{entry_id}: pinned file {path} does not exist")
            elif name not in names:
                problems.append(f"{entry_id}: pinned node {node} does not exist")
        test = entry.get("test")
        if test:
            measured_by += 1
            path, name = split_node(test)
            if path != LEDGER_TEST_FILE or name != owned_test_name(entry_id):
                problems.append(f"{entry_id}: its test must be {LEDGER_TEST_FILE}::{owned_test_name(entry_id)}")
            owned_tests.add(name)
        driver = entry.get("driver")
        if driver:
            measured_by += 1
            script = driver_script(driver)
            if not script.startswith("tools/measurements/"):
                problems.append(f"{entry_id}: driver {script} is not under tools/measurements/")
            elif not (root / script).is_file():
                problems.append(f"{entry_id}: driver {script} does not exist")
            elif root == REPO_ROOT and pathlib.PurePosixPath(script).name not in readme:
                problems.append(f"{entry_id}: driver {script} has no row in tools/measurements/README.md")
        if measured_by == 0:
            problems.append(f"{entry_id}: nothing measures it (no node, test or driver)")
        if entry.get("source") == "driver" and not driver:
            problems.append(f"{entry_id}: source is driver but no driver is named")
    ledger_tests = names_in(LEDGER_TEST_FILE) or frozenset()
    for name in sorted(n for n in ledger_tests if n.startswith("test_k_")):
        if name not in owned_tests:
            problems.append(f"{LEDGER_TEST_FILE}::{name} is a KPI test no ledger entry names")
    for name in sorted(owned_tests - ledger_tests):
        problems.append(f"{LEDGER_TEST_FILE}::{name} is named by the ledger but not defined")
    headlines = [entry for entry in entries if entry.get("headline")]
    if not HEADLINES_AT_LEAST <= len(headlines) <= HEADLINES_AT_MOST:
        problems.append(
            f"{len(headlines)} headlines: the board holds {HEADLINES_AT_LEAST} to {HEADLINES_AT_MOST}"
        )
    for group in sorted({group_of(i) for i in ids}):
        if not any(group_of(e["id"]) == group for e in headlines):
            problems.append(f"phase or stage {group} has no headline")
    for category in CATEGORIES:
        if not any(e.get("category") == category for e in headlines):
            problems.append(f"category {category} has no headline")
    return problems


def select(entries: "list[dict]", patterns: "list[str]") -> "list[dict]":
    """The entries whose id matches any of the shell patterns (all if none)."""
    if not patterns:
        return list(entries)
    return [
        entry
        for entry in entries
        if any(fnmatch.fnmatchcase(entry["id"], pattern) for pattern in patterns)
    ]


# -- what a SLOW driver under tools/measurements/ shares -------------------


def guard_this_tree() -> str:
    """Print where synthtwin was imported from, and refuse unless it is this tree's src.

    A driver measured against an installed copy of another checkout
    reports a confident number about the wrong code; that has voided
    evidence here before.
    """
    import synthtwin

    here = pathlib.Path(synthtwin.__file__).resolve()
    print(f"synthtwin imported from {here}", flush=True)
    if (REPO_ROOT / "src").resolve() not in here.parents:
        raise SystemExit(f"REFUSING: synthtwin resolves to {here}, not under {REPO_ROOT / 'src'}")
    return str(here)


def emit(entry_id: str, value: object, detail: str = "") -> None:
    """One KPI line for `tools/measurements/kpi_run.py --slow`."""
    record = {"id": entry_id, "value": value, "detail": detail}
    print("KPI " + json.dumps(record, sort_keys=True), flush=True)
