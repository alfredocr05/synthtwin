"""Stage 5's gate: results become data (plan P4-D395; lane S5a, plan P4-D437).

STATE's row 5: "a caller distinguishes a good run from a bad one without
reading prose; reports byte-identical". Two KPIs measure it over the
golden battery of `tests/stage5_battery.py`, and this file is their gate:

- `K-S5-01`: each case's result, read through `cli.run`, says what the
  case's row wrote for it when the case was written -- its class, the
  misses a damage must break with their tiers, a refusal's step, the
  warnings, the floor, the next command, the carried entries, and (lane
  S5a's repair 1, clause (j)) its command, the files it wrote and the
  rule keys of what it could not judge -- and each miss's identity, text
  and rank values equal its producer's, checked one by one against
  values found without the result's code. A checker handed a correct
  result corrupted one field at a time must find it unmet.
- `K-S5-02`: every file, screen and exit status a case leaves equals the
  goldens recorded from the code before lane S5a (`tests/stage5_goldens.py`),
  and the goldens' three digests are what they claim. What is
  authoritative is CI's guarded reproduction of every record in a fresh
  interpreter (`tools/goldens/record_stage5_goldens.py`, its step in
  `.github/workflows/ci.yml`); here the battery runs once, through
  `cli.run` with a screen that records, so one pass serves both KPIs.
  The every-role run (G5) is left to that reproduction: it took 281
  seconds at the table floor.

And the four guarantees of part 3: `run` given no screen and no reader
prints nothing and reads nothing; a validate run reaches no generator and
a generate run no reader, proved in a fresh interpreter's `sys.modules`;
and a stop injected at writing, after validate's report was shown, keeps
the misses that report showed.
"""

import dataclasses
import hashlib
import importlib.util
import json
import os
import pathlib
import random
import re
import subprocess
import sys
import types
import typing

import pytest

import dispositions
import stage5_battery as battery
import stage5_goldens as goldens
from synthtwin import asking, canonical, cli, errors, generation, rendering, results, validation, writing

ROOT = pathlib.Path(__file__).resolve().parents[1]
_RECORDER_PATH = ROOT / "tools" / "goldens" / "record_stage5_goldens.py"


def _recorder() -> typing.Any:
    found = sys.modules.get("record_stage5_goldens")
    if found is not None:
        return found
    spec = importlib.util.spec_from_file_location("record_stage5_goldens", _RECORDER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["record_stage5_goldens"] = module
    spec.loader.exec_module(module)
    return module


RECORDER = _recorder()


@dataclasses.dataclass
class Ran:
    """One case's run: its result, its capture, its folder, and what its producers made."""

    case: battery.Case
    result: results.Result
    capture: typing.Any
    folder: pathlib.Path
    outcome: "validation.Outcome | None" = None
    twin: "generation.Twin | None" = None
    checks: "list[typing.Any] | None" = None
    # A profile's files as the run left them, by kind (lane S5b): a later
    # case in the same folder (G7 in G6's) writes over them.
    kept: "dict[str, bytes]" = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Battery:
    root: pathlib.Path
    records: "list[tuple[object, ...]]"
    runs: "dict[str, Ran]"


class _Produced:
    """What the producers made during the run in progress (the test's own spies)."""

    def __init__(self) -> None:
        self.outcome: "validation.Outcome | None" = None
        self.twin: "generation.Twin | None" = None
        self.checks: "list[typing.Any] | None" = None
        self.kept: "dict[str, bytes]" = {}


def _kept(result: results.Result) -> "dict[str, bytes]":
    """A profile's files as the run left them, by kind; nothing for another command."""
    if result.command != results.PROFILE:
        return {}
    return {one.kind: pathlib.Path(one.path).read_bytes() for one in result.files}


def _spied(patch: pytest.MonkeyPatch, produced: "list[_Produced]") -> None:
    """Keep the validator's outcome, the generator's twin and doctor's checks as they are made."""
    measure = validation.measure
    generate_held = generation.generate_held
    doctor_checks = cli._doctor_checks

    def measuring(*given: typing.Any, **named: typing.Any) -> validation.Outcome:
        made = measure(*given, **named)
        produced[-1].outcome = made
        return made

    def generating(*given: typing.Any, **named: typing.Any) -> generation.Twin:
        made = generate_held(*given, **named)
        produced[-1].twin = made
        return made

    def checking(*given: typing.Any, **named: typing.Any) -> "list[typing.Any]":
        made = doctor_checks(*given, **named)
        produced[-1].checks = made
        return made

    patch.setattr(validation, "measure", measuring)
    patch.setattr(generation, "generate_held", generating)
    patch.setattr(cli, "_doctor_checks", checking)


def _faulted(patch: pytest.MonkeyPatch, fault: str) -> None:
    """Inject the fault a K-S5-01-only case's row names."""
    if fault == "questions-unwritable":
        original = writing.write_one_file

        def refusing(target: typing.Any, *given: typing.Any, **named: typing.Any) -> typing.Any:
            if f"{target}".endswith("-questions.json"):
                raise OSError("the battery's injected fault: the questions file cannot be written")
            return original(target, *given, **named)

        patch.setattr(writing, "write_one_file", refusing)
    elif fault == "unencodable":

        def pieces(_twin: typing.Any) -> "typing.Iterator[str]":
            yield "\udcff\n"

        patch.setattr(rendering, "twin_csv_pieces", pieces)
    elif fault == "memory-16-GiB":
        patch.setattr(cli, "_total_memory", lambda: 16 * 1024 * 1024 * 1024)
    elif fault == "memory-unread":
        patch.setattr(cli, "_total_memory", lambda: None)
    elif fault == "memory-100000-bytes":
        patch.setattr(cli, "_total_memory", lambda: 100_000)


@pytest.fixture(scope="module")
def ran(tmp_path_factory: pytest.TempPathFactory) -> Battery:
    """The battery, run once: every recorded case but G5, then the K-S5-01-only ones."""
    return run_battery(tmp_path_factory.mktemp("stage5"), slow=False)


def run_battery(root: pathlib.Path, slow: bool) -> Battery:
    """Run the battery under ``root`` through `cli.run`, once, and keep what each case made.

    The recorded cases run in their order with a screen that records,
    so one pass gives each case's result (`K-S5-01`) and its three
    records (`K-S5-02`); G5, the every-role run, only where ``slow`` is
    true (`tools/measurements/kpi_stage5.py`; CI's guarded recorder runs
    it on every push). Then the cases `K-S5-01` alone runs, each with
    the fault or the reader its row names. Usable outside pytest: the
    patches are `pytest.MonkeyPatch` contexts, undone on return.
    """
    produced: "list[_Produced]" = []
    made: "list[results.Result]" = []
    runs: "dict[str, Ran]" = {}
    with pytest.MonkeyPatch.context() as patch:
        _spied(patch, produced)

        def invoke(argv: "list[str]", write: "typing.Callable[[str, str], None]") -> int:
            produced.extend([_Produced()])
            screen: "list[tuple[str, str]]" = []
            result = cli.run(argv, screen=screen, small_tables_refused=True)
            produced[-1].kept = _kept(result)
            for stream, text in screen:
                write(stream, text)
            made.extend([result])
            return results.exit_code(result)

        cases = [
            case
            for case in battery.RECORDED
            if (slow or case.key not in battery.SLOW)
            and not (case.posix_only and os.name == "nt")
        ]
        records, captures = RECORDER.reproduce(root, invoke, cases)
        for place, case in enumerate(cases):
            runs[case.key] = Ran(
                case,
                made[place],
                captures[case.key],
                root / (case.on or case.key),
                produced[place].outcome,
                produced[place].twin,
                produced[place].checks,
                produced[place].kept,
            )
        for case in battery.UNRECORDED:
            folder = battery.lay_unrecorded(case, root)
            with pytest.MonkeyPatch.context() as faulty:
                _faulted(faulty, case.fault)
                internal = dict(case.internal)

                def invoke_one(
                    argv: "list[str]", write: "typing.Callable[[str, str], None]"
                ) -> int:
                    produced.extend([_Produced()])
                    screen: "list[tuple[str, str]]" = []
                    result = cli.run(
                        argv,
                        screen=screen,
                        ask=[] if case.fault == "reader" else None,
                        small_tables_refused=True,
                        **internal,
                    )
                    produced[-1].kept = _kept(result)
                    for stream, text in screen:
                        write(stream, text)
                    made.extend([result])
                    return results.exit_code(result)

                captured = RECORDER.capture(case.argv, folder, invoke_one)
            runs[case.key] = Ran(
                case,
                made[-1],
                captured,
                folder,
                produced[-1].outcome,
                produced[-1].twin,
                produced[-1].checks,
                produced[-1].kept,
            )
    return Battery(root, records, runs)


# -- K-S5-01: the checker, and the battery read through it -------------


def _golden_exit(key: str) -> "int | None":
    for record in goldens.RECORDS:
        if record[0] == key and record[1] == "exit":
            return typing.cast(int, record[2])
    return None


def _document(folder: pathlib.Path, argv: "tuple[str, ...]") -> "dict[str, typing.Any]":
    """The description the case names, as JSON (the test's own reading), or {} where it names none."""
    for word in argv:
        if word.endswith("-profile.json") and (folder / word).exists():
            return typing.cast(
                "dict[str, typing.Any]",
                json.loads((folder / word).read_text(encoding="utf-8")),
            )
    return {}


def _positions(folder: pathlib.Path, argv: "tuple[str, ...]") -> "dict[str, int]":
    """Each column's position, read from the description the case names (the test's own reading)."""
    document = _document(folder, argv)
    return {block["name"]: block["position"] for block in document.get("columns", [])}


def _groups(folder: pathlib.Path, argv: "tuple[str, ...]") -> "dict[str, str]":
    """Each column's registry group, read off its role in the description through the registry's own table."""
    document = _document(folder, argv)
    return {
        block["name"]: dispositions.ROLE_GROUPS[block["role"]]
        for block in document.get("columns", [])
    }


# The disposition registry's universal fields: column-level keys, whatever
# the role, a column's time grain among them since lane S5b (plan P4-D441:
# plan P4-D437 had named it the one key the generator writes that the
# registry held under no group).
_UNIVERSAL_FIELDS = frozenset(
    fact.field for fact in dispositions.REGISTRY if fact.group == "universal"
)


def _head(field: str) -> str:
    return re.split(r"[.\[]", field, maxsplit=1)[0]


def _qualified(groups: "dict[str, str]", column: str, fact: str, end: str) -> str:
    """A generator fact as the registry names it, found by the test alone (`K-S5-01` (h), (i)).

    The field is the generator's key after its last `levels -> `; the
    group `universal` for a column-level key, else the group the column's
    role publishes under; then `.end` for a ladder end that gave way.
    """
    field = fact.split(" -> ")[-1]
    if _head(field) in _UNIVERSAL_FIELDS:
        group = "universal"
    else:
        group = groups.get(column, "")
    named = f"{group}.{field}" if group else field
    return f"{named}.{end}" if end else named


def _expected_tier(
    expect: battery.Expect, identity: "tuple[str, str, str]", judged: str
) -> "str | None":
    for column, fact, subcheck, tier in expect.breaks:
        if identity == (column, fact, subcheck):
            return tier
    if judged == results.JUDGED_WINDOW:
        return results.TIER_WINDOW
    return results._ranked(identity[1], identity[2])


def recorded_fields_unmet(run: Ran, result: results.Result) -> "list[str]":
    """Clause (j) of `K-S5-01` alone: the command, the files written, validate's rule keys.

    The fields lanes TT and TS read (lane S5a's repair 1): the command
    equals the one its row writes; the kinds of the files, in order, are
    the row's, each path existing, and none on a run that writes
    nothing; and each of validate's unjudged entries carries the key
    whose sentence in `validation.WITHHELD_RULES` is its producer check's
    citation, the fallback only as often as the row writes it.
    """
    case = run.case
    expect = case.expect if case.expect is not None else battery.EXPECTED[case.key]
    found: "list[str]" = []
    if result.command != expect.command:
        found += [f"(j) command {result.command!r}, the row writes {expect.command!r}"]
    kinds = tuple(one.kind for one in result.files)
    if kinds != expect.files:
        found += [f"(j) files {kinds}, the row writes {expect.files}"]
    for one in result.files:
        if not (run.folder / one.path).exists():
            found += [f"(j) {one.path} is named among the files and does not exist"]
    if run.outcome is not None and result.verdict != "refused":
        keyed = dict(validation.WITHHELD_RULES)
        wanted = [
            keyed.get(check.citation, validation.WITHHELD_FALLBACK)
            for check in run.outcome.checks
            if check.verdict == validation.WITHHELD
        ]
        if [one.key for one in result.unjudged] != wanted:
            found += ["(j) an unjudged entry's key is not its producer check's rule"]
        if wanted.count(validation.WITHHELD_FALLBACK) != expect.fallback_keys:
            found += ["(j) an unjudged entry falls to the fallback key the row does not write"]
    return found


# THE QUESTIONS FILE'S ENTRIES, read with `json` alone (lane S5b, plan
# P4-D441): each section's list of entries, in the file's order.
_FILE_SECTIONS = (
    (results.SECTION_ABOUT_FILE, ("about_your_file",)),
    (results.SECTION_ASKED, ("asked",)),
    (results.SECTION_CHECKLIST, ("checklist", "columns")),
    (results.SECTION_HELD, ("held",)),
)


def _file_entries(written: "dict[str, typing.Any]") -> "list[tuple[str, dict[str, typing.Any]]]":
    """Every entry of a written questions file with its section, in the file's order."""
    found: "list[tuple[str, dict[str, typing.Any]]]" = []
    for section, path in _FILE_SECTIONS:
        node: typing.Any = written
        for key in path:
            node = node.get(key, []) if isinstance(node, dict) else []
        found += [(section, entry) for entry in node]
    return found


def _record_as_written(record: results.Asked) -> "dict[str, typing.Any]":
    """A record as the file's entry shows it, by the file's documented keys (the test's own reading)."""
    if record.section == results.SECTION_HELD:
        return {"column": record.subject, "what_synthtwin_saw": record.saw}
    return {
        "column": record.subject,
        "what_synthtwin_saw": record.saw,
        "read_as_now": record.read_as_now,
        "answers_you_can_give": [
            {"answer": offer.answer, "means": offer.means, "then_the_description_publishes": offer.publishes}
            for offer in record.offers
        ],
        "your_answer": "",
    }


def _questions_unmet(run: Ran, result: results.Result) -> "list[str]":
    """Clause (k), lane S5b (plan P4-D441): a profile's questions are its file's entries, one for one.

    The (section, column) of each record as the row writes them; each
    numbered from 1 within its section; none put at a prompt (no case of
    the battery but Q1 has a reader, and Q1 refuses); a held entry
    offering nothing; and, where the run wrote its questions file, each
    entry of the file -- read with `json` -- the record's own words, in
    the same order (a held entry's sentence beside it, `asking`'s
    constant). A record names its column in the file's words, and a
    question about the file names none. The tally counts the records --
    asked, checklist, held -- and no question is put where nobody is asked.
    """
    case = run.case
    expect = case.expect if case.expect is not None else battery.EXPECTED[case.key]
    found: "list[str]" = []
    if expect.questions is None:
        return found
    placed = tuple((one.section, one.column) for one in result.questions)
    if placed != expect.questions:
        found += [f"(k) questions {placed}, the row writes {expect.questions}"]
    counted: "dict[str, int]" = {}
    for one in result.questions:
        counted[one.section] = counted.get(one.section, 0) + 1
        if one.order != counted[one.section]:
            found += [f"(k) {one.column!r} stands at {one.order} in {one.section}, not {counted[one.section]}"]
        if one.put:
            found += [f"(k) {one.column!r} is said put at a prompt, where nobody is asked"]
        if one.section == results.SECTION_HELD and (one.offers or one.read_as_now):
            found += [f"(k) the held {one.column!r} offers an answer"]
        if one.column != ("" if one.section == results.SECTION_ABOUT_FILE else one.subject):
            found += [f"(k) the record of {one.subject!r} in {one.section} names the column {one.column!r}"]
    if results.FILE_QUESTIONS in run.kept:
        document = json.loads(run.kept[results.FILE_QUESTIONS].decode("utf-8"))
        entries = _file_entries(document)
        mine = [(one.section, _record_as_written(one)) for one in result.questions]
        theirs = [
            (section, {key: entry[key] for key in mine[place][1]} if place < len(mine) else entry)
            for place, (section, entry) in enumerate(entries)
        ]
        if mine != theirs:
            found += ["(k) the questions file's entries are not the result's records"]
    if result.command == results.PROFILE and result.verdict == results.NO_MISS:
        records = result.questions
        described = run.kept.get(results.FILE_DESCRIPTION)
        columns = json.loads(described.decode("utf-8"))["n_columns"] if described else -1
        wanted = (
            ("columns", columns),
            ("questions-asked", len([one for one in records if one.section in (results.SECTION_ABOUT_FILE, results.SECTION_ASKED)])),
            ("questions-put", 0),
            ("checklist", len([one for one in records if one.section == results.SECTION_CHECKLIST])),
            ("held", len([one for one in records if one.section == results.SECTION_HELD])),
        )
        if result.tally != wanted:
            found += ["(f) the profile's tally is not its records counted"]
    return found


def unmet(run: Ran, result: results.Result) -> "list[str]":
    """Why ``result`` does not meet the case's row, under `K-S5-01` (a) to (j); empty when met.

    Only the result's fields are read; no text field is parsed or
    searched. Each value is checked against what the case's row writes
    or what the case's producers made, never against the result's code.
    """
    case = run.case
    expect = case.expect if case.expect is not None else battery.EXPECTED[case.key]
    found: "list[str]" = []
    # (a) nothing reached the process's streams and nothing was read
    if run.capture.strays or run.capture.reads:
        found += ["(a) the run reached the process's own streams"]
    # (b) the class
    if result.verdict != expect.verdict:
        found += [f"(b) verdict {result.verdict}, the row writes {expect.verdict}"]
    # (c) the exit status the battery recorded through `main`
    wanted_exit = _golden_exit(case.key) if case.recorded else expect.exit
    if results.exit_code(result) != wanted_exit:
        found += [f"(c) exit {results.exit_code(result)}, recorded {wanted_exit}"]
    # (d) the misses: those the damage breaks, their order, their number, the first tier
    misses = result.misses
    for column, fact, subcheck, tier in expect.breaks:
        if not any(
            (miss.column, miss.fact, miss.subcheck, miss.tier) == (column, fact, subcheck, tier)
            for miss in misses
        ):
            found += [f"(d) {column} {fact} [{subcheck}] at tier {tier} is not among the misses"]
    ranks = [(results.TIER_ORDER[miss.tier], miss.place, miss.arrival) for miss in misses]
    if ranks != sorted(ranks):
        found += ["(d) the misses do not stand in (tier, place, arrival) order"]
    arrivals = sorted(miss.arrival for miss in misses)
    if result.verdict == "refused":
        # A refused run keeps the misses of a report it showed, and only those.
        if len(misses) != expect.misses_kept:
            found += [f"(d) {len(misses)} misses on a refused run, the row writes {expect.misses_kept}"]
    elif run.outcome is not None:
        if len(misses) != run.outcome.census.missed:
            found += [f"(d) {len(misses)} misses, the census counts {run.outcome.census.missed}"]
        missed_at = [
            place
            for place, check in enumerate(run.outcome.checks)
            if check.verdict == validation.MISSED
        ]
        if arrivals != missed_at:
            found += ["(d) the arrivals are not the places of the MISSED checks"]
    elif run.twin is not None:
        if len(misses) != len(run.twin.deviations):
            found += [f"(d) {len(misses)} misses, the twin {len(run.twin.deviations)} deviations"]
        if arrivals != list(range(len(run.twin.deviations))):
            found += ["(d) the arrivals are not the twin's deviations, each once"]
    elif misses:
        found += ["(d) misses where no producer made any"]
    if expect.first_tier and (not misses or misses[0].tier != expect.first_tier):
        found += [f"(d) the first miss is not at tier {expect.first_tier}"]
    if expect.every_tier and any(miss.tier != expect.every_tier for miss in misses):
        found += [f"(d) a miss stands outside tier {expect.every_tier}"]
    # (e) the refusal's step, and its key
    if result.verdict in ("refused", "unusable"):
        if result.refusal is None:
            found += ["(e) no refusal on a run that could not finish"]
        else:
            if result.refusal.step != expect.step:
                found += [f"(e) step {result.refusal.step}, the row writes {expect.step}"]
            if result.refusal.key != expect.key:
                found += [f"(e) key {result.refusal.key!r}, the row writes {expect.key!r}"]
    elif result.refusal is not None:
        found += ["(e) a refusal on a run that finished"]
    # (f) the tally is what the producer counted, `unjudged` its WITHHELD checks
    if run.outcome is not None and result.verdict != "refused":
        census = run.outcome.census
        wanted_tally = (
            ("held", census.held),
            ("within-bound", census.within_bound),
            ("authorized-deviation", census.authorized_deviation),
            ("withheld", census.withheld),
            ("missed", census.missed),
            ("not-checkable", census.not_checkable),
        )
        if result.tally != wanted_tally:
            found += ["(f) the tally is not the census"]
        withheld = [
            (check.column, check.fact, check.subcheck)
            for check in run.outcome.checks
            if check.verdict == validation.WITHHELD
        ]
        if [(one.column, one.fact, one.subcheck) for one in result.unjudged] != withheld:
            found += ["(f) unjudged is not the WITHHELD checks"]
    if run.twin is not None and result.verdict != "refused":
        twin = run.twin
        loaded = rendering.contract.load_profile(f"{run.folder / case.argv[1]}")
        whole, part = rendering._made_up_totals(loaded)
        wanted_tally = (
            ("deviations", len(twin.deviations)),
            ("approximations", len(twin.approximations)),
            ("approximations-inside", sum(1 for one in twin.approximations if one.inside)),
            ("remarks", len(twin.remarks)),
            ("columns-made-up", whole),
            ("columns-partly-made-up", part),
        )
        if result.tally != wanted_tally:
            found += ["(f) the tally is not what the generator counted"]
    if expect.tally is not None:
        if result.tally != expect.tally:
            found += [f"(f) tally {result.tally}, the row writes {expect.tally}"]
        if run.checks is not None:
            unmade = sum(1 for check in run.checks if check.passed and not check.made)
            if len(result.unjudged) != unmade:
                found += ["(f) unjudged is not the checks not made"]
    # (g) warnings, floor, next command
    if tuple(one.key for one in result.warnings) != expect.warnings:
        found += [f"(g) warnings {[one.key for one in result.warnings]}, the row writes {expect.warnings}"]
    if result.floor != expect.floor or result.floor_lowered != expect.floor_lowered:
        found += [f"(g) floor {result.floor}/{result.floor_lowered}, the row writes {expect.floor}/{expect.floor_lowered}"]
    resolved = os.path.realpath(run.folder)
    wanted_words = tuple(word.replace("<FOLDER>", resolved) for word in expect.next_words)
    if not expect.next_words:
        if result.next_command is not None:
            found += ["(g) a next command where the row writes none"]
    elif result.next_command is None or (
        result.next_command.words,
        result.next_command.purpose,
    ) != (wanted_words, expect.next_purpose):
        found += [f"(g) next command {result.next_command}, the row writes {wanted_words} {expect.next_purpose}"]
    # (h) carried: the entries not carried as the row writes them, each
    # with its subject; an approximate entry for each approximation the
    # generator made, or each check the validator judged against a window,
    # with its subject, fact, subcheck, class and reason -- and on validate
    # the checks the row writes, read off the description.
    if expect.carried is not None:
        not_carried = tuple(
            (one.subject, one.kind, one.reason, one.verdict)
            for one in result.carried
            if one.kind == results.CLASS_NOT_CARRIED
        )
        if not_carried != expect.carried:
            found += [f"(h) not carried {not_carried}, the row writes {expect.carried}"]
    found += _questions_unmet(run, result)
    approximate = [one for one in result.carried if one.kind == results.CLASS_APPROXIMATE]
    groups = _groups(run.folder, case.argv)
    if run.twin is not None and result.verdict != "refused":
        wanted = [
            (
                (one.column,),
                _qualified(groups, one.column, one.fact, ""),
                "",
                "approximate",
                "approximated",
                "",
                one.published,
                one.achieved,
                one.lowest,
                one.highest,
                one.inside,
                one.covers_published,
            )
            for one in run.twin.approximations
        ]
        held = [
            (
                one.subject,
                one.fact,
                one.subcheck,
                one.kind,
                one.reason,
                one.verdict,
                one.measures[0].published,
                one.measures[0].achieved,
                one.measures[0].lowest,
                one.measures[0].highest,
                one.measures[0].inside,
                one.measures[0].covers_published,
            )
            for one in approximate
        ]
        if held != wanted:
            found += ["(h)(i) the approximate entries are not the twin's approximations"]
    if run.outcome is not None and result.verdict != "refused":
        # Every check whose obligation the description grants a window
        # (lane S5a's repair 2: `Check.approximate`, kept where the file
        # lacks the column, holds no rows or names, or the gate closed).
        wanted_checks = [check for check in run.outcome.checks if check.approximate]
        if [
            (one.subject, one.fact, one.subcheck, one.kind, one.reason, one.verdict)
            for one in approximate
        ] != [
            (
                (check.column,) if check.column else (),
                check.fact,
                check.subcheck,
                "approximate",
                "approximated",
                check.verdict,
            )
            for check in wanted_checks
        ]:
            found += ["(h) the approximate entries are not the checks judged against a window"]
        if expect.approximate is not None and tuple(
            (one.subject[0] if one.subject else "", one.fact, one.subcheck) for one in approximate
        ) != expect.approximate:
            found += ["(h) the approximate entries are not the ones the row reads off the description"]
        for one, check in zip(approximate, wanted_checks):
            measure = one.measures[0]
            # inside: none where the check is WITHHELD, V5 keeps its measured
            # side back, or no window decided its verdict (repair 2)
            inside = (
                None
                if check.verdict == validation.WITHHELD
                or not check.achieved
                or check.judged != validation.JUDGED_WINDOW
                else check.verdict != validation.MISSED
            )
            if (measure.published, measure.achieved, measure.inside) != (check.published, check.achieved, inside):
                found += [f"(i) a carried measure of {check.fact} is not its check's"]
            # ...and the window's ends and whether it holds the published
            # value, as the producer printed them (repair 2, Codex's item 7)
            if (measure.lowest, measure.highest, measure.covers_published) != (check.lowest, check.highest, check.covers):
                found += [f"(i) a carried measure of {check.fact} does not carry its check's window"]
    # (i) each miss's identity, text and rank values, one by one
    positions = _positions(run.folder, case.argv)
    for miss in misses:
        producer: typing.Any = None
        identity: "tuple[str, str, str, str]" = ("", "", "", "")
        if run.outcome is not None:
            if 0 <= miss.arrival < len(run.outcome.checks):
                producer = run.outcome.checks[miss.arrival]
                if producer.verdict != validation.MISSED:
                    producer = None
            if producer is not None:
                text = (producer.published, producer.achieved, producer.note)
                identity = (producer.column, producer.fact, producer.subcheck, producer.judged)
        elif run.twin is not None:
            if 0 <= miss.arrival < len(run.twin.deviations):
                producer = run.twin.deviations[miss.arrival]
                text = (producer.published, producer.achieved, (producer.note,) if producer.note else ())
                identity = (
                    producer.column,
                    _qualified(groups, producer.column, producer.fact, producer.end),
                    "",
                    producer.judged,
                )
        if producer is None:
            found += [f"(i) arrival {miss.arrival} names no missed check or deviation"]
            continue
        if (miss.column, miss.fact, miss.subcheck, miss.judged) != identity:
            found += [f"(i) arrival {miss.arrival} is named {(miss.column, miss.fact, miss.subcheck, miss.judged)}, its producer {identity}"]
        if (miss.published, miss.achieved, miss.note) != text:
            found += [f"(i) {miss.fact}'s text is not its producer's"]
        if miss.shown != bool(producer.achieved):
            found += [f"(i) {miss.fact} is shown where the producer keeps its measured side back, or the reverse"]
        wanted_place = positions.get(miss.column, 0) if miss.column else 0
        if miss.place != wanted_place:
            found += [f"(i) {miss.fact} at place {miss.place}, the description puts it at {wanted_place}"]
        if _expected_tier(expect, identity[:3], identity[3]) != miss.tier:
            found += [f"(i) {miss.fact} [{miss.subcheck}] at tier {miss.tier}"]
    # (j) the command, the files written, validate's rule keys
    found += recorded_fields_unmet(run, result)
    return found


def classed(ran: Battery) -> "dict[str, Ran]":
    """The cases that name a class (`K-S5-01`): every case run but G5's, which pin bytes only."""
    return {
        key: run
        for key, run in ran.runs.items()
        if run.case.expect is not None or key in battery.EXPECTED
    }


def test_k_s5_01_every_case_of_the_battery_is_met(ran: Battery) -> None:
    """`K-S5-01`: a caller tells each case's run from the result alone."""
    unmet_cases = {}
    cases = classed(ran)
    for key, run in cases.items():
        why = unmet(run, run.result)
        if why:
            unmet_cases[key] = why
    met = len(cases) - len(unmet_cases)
    assert not unmet_cases, f"{met} of {len(cases)} cases met; unmet: {unmet_cases}"


def _corruptions(ran: Battery) -> "list[tuple[str, Ran, results.Result]]":
    """A correct result corrupted one field at a time (the page's list, `K-S5-01`)."""
    found: "list[tuple[str, Ran, results.Result]]" = []
    seven = ran.runs["M7"]
    first = seven.result.misses[0]
    swapped = dataclasses.replace(first, published=first.achieved, achieved=first.published)
    found += [("published and achieved exchanged", seven, dataclasses.replace(seven.result, misses=(swapped,) + seven.result.misses[1:]))]
    found += [("a place moved", seven, dataclasses.replace(seven.result, misses=(dataclasses.replace(first, place=first.place + 1),) + seven.result.misses[1:]))]
    found += [("an arrival moved", seven, dataclasses.replace(seven.result, misses=(dataclasses.replace(first, arrival=first.arrival + 1),) + seven.result.misses[1:]))]
    found += [("a tier moved", seven, dataclasses.replace(seven.result, misses=(dataclasses.replace(first, tier=results.TIER_COUNT),) + seven.result.misses[1:]))]
    found += [("a miss dropped", seven, dataclasses.replace(seven.result, misses=seven.result.misses[1:]))]
    found += [("a miss duplicated", seven, dataclasses.replace(seven.result, misses=(first,) + seven.result.misses))]
    one = ran.runs["D1"]
    outside = [entry for entry in one.result.carried if entry.measures and entry.measures[0].inside is False]
    assert len(outside) >= 2, "D1's twin keeps its two approximations outside their bounds"
    corrupted = tuple(
        dataclasses.replace(entry, measures=(dataclasses.replace(entry.measures[0], inside=True),))
        if entry in outside
        else entry
        for entry in one.result.carried
    )
    found += [("inside made true on approximations outside their bounds", one, dataclasses.replace(one.result, carried=corrupted))]
    hidden = [
        (key, run, place)
        for key, run in ran.runs.items()
        for place, miss in enumerate(run.result.misses)
        if not miss.shown
    ]
    assert hidden, "the battery holds a miss whose measured side V5 keeps back"
    _key, run, place = hidden[0]
    kept = run.result.misses
    found += [("shown made true on a side kept back", run, dataclasses.replace(run.result, misses=kept[:place] + (dataclasses.replace(kept[place], shown=True),) + kept[place + 1:]))]
    two = ran.runs["G2"]
    assert two.result.next_command is not None
    found += [("the next command's purpose changed", two, dataclasses.replace(two.result, next_command=dataclasses.replace(two.result.next_command, purpose="doctor")))]
    # Lane S5a's repair 1: the identity of a miss the row does not name,
    # the carried entries' subjects, reasons and subcheck, the fields lanes
    # TT and TS read, and a refused run's misses.
    four = ran.runs["M4"]
    named = {(column, fact, subcheck) for column, fact, subcheck, _tier in battery.EXPECTED["M4"].breaks}
    unnamed = [place for place, miss in enumerate(four.result.misses) if (miss.column, miss.fact, miss.subcheck) not in named]
    assert unnamed, "M4 holds misses its row does not name"
    place = unnamed[-1]
    kept = four.result.misses
    other = kept[place]

    def with_miss(changed: results.Miss) -> results.Result:
        return dataclasses.replace(four.result, misses=kept[:place] + (changed,) + kept[place + 1:])

    renamed = "numeric.std" if other.fact != "numeric.std" else "numeric.mean"
    found += [("a miss's fact renamed", four, with_miss(dataclasses.replace(other, fact=renamed)))]
    moved = "distinct.n_distinct" if other.subcheck != "distinct.n_distinct" else "moments.std"
    found += [("a miss's subcheck changed", four, with_miss(dataclasses.replace(other, subcheck=moved)))]
    flipped = "window" if other.judged == "exact" else "exact"
    found += [("a miss's judged flipped, its tier kept", four, with_miss(dataclasses.replace(other, judged=flipped)))]
    three = ran.runs["G3"]
    carried = three.result.carried
    first_approximate = [place for place, entry in enumerate(carried) if entry.kind == "approximate"][0]
    first_not_carried = [place for place, entry in enumerate(carried) if entry.kind == "not-carried"][0]

    def with_carried(at: int, changed: results.Carried) -> results.Result:
        return dataclasses.replace(three.result, carried=carried[:at] + (changed,) + carried[at + 1:])

    entry = carried[first_approximate]
    found += [("an approximate entry's subject changed", three, with_carried(first_approximate, dataclasses.replace(entry, subject=("ward",))))]
    found += [("an approximate entry's reason changed", three, with_carried(first_approximate, dataclasses.replace(entry, reason="held-back")))]
    found += [("an approximate entry's subcheck changed", three, with_carried(first_approximate, dataclasses.replace(entry, subcheck=entry.subcheck + ".other")))]
    # Lane S5a's repair 2: a window's printed ends and whether it holds the
    # published value, carried as data.
    windowed = [place for place, one in enumerate(carried) if one.kind == "approximate" and one.measures[0].lowest]
    assert windowed, "G3 prints windows"
    at = windowed[0]
    measure = carried[at].measures[0]
    found += [("a carried window's low end changed", three, with_carried(at, dataclasses.replace(carried[at], measures=(dataclasses.replace(measure, lowest="-" + measure.lowest),))))]
    flipped_cover = False if measure.covers_published is not False else True
    found += [("a carried window's cover flipped", three, with_carried(at, dataclasses.replace(carried[at], measures=(dataclasses.replace(measure, covers_published=flipped_cover),))))]
    entry = carried[first_not_carried]
    found += [("a not-carried entry's subject changed", three, with_carried(first_not_carried, dataclasses.replace(entry, subject=("ward",))))]
    found += [("a not-carried entry's reason changed", three, with_carried(first_not_carried, dataclasses.replace(entry, reason="held-back")))]
    found += [("the command changed", three, dataclasses.replace(three.result, command="generate"))]
    found += [("a file dropped", two, dataclasses.replace(two.result, files=two.result.files[:1]))]
    five = ran.runs["M5"]
    assert five.result.unjudged, "M5 keeps checks back"
    found += [("an unjudged entry's rule key changed", five, dataclasses.replace(five.result, unjudged=(dataclasses.replace(five.result.unjudged[0], key="gate-pooled"),) + five.result.unjudged[1:]))]
    refused = ran.runs["R3"]
    found += [("a miss kept on a refused run that showed no report", refused, dataclasses.replace(refused.result, misses=two.result.misses[:1]))]
    # Lane S5b (plan P4-D441): a profile's questions, its carried entries
    # and its tally.
    six = ran.runs["G6"]
    asked = six.result.questions
    assert len(asked) >= 2 and asked[0].offers, "G6 lists two columns"
    offer = asked[0].offers[0]
    reworded = dataclasses.replace(asked[0], offers=(dataclasses.replace(offer, publishes=offer.publishes + " and more"),) + asked[0].offers[1:])
    found += [("a question's offer reworded", six, dataclasses.replace(six.result, questions=(reworded,) + asked[1:]))]
    found += [("a question dropped", six, dataclasses.replace(six.result, questions=asked[1:]))]
    found += [("two questions exchanged", six, dataclasses.replace(six.result, questions=(asked[1], asked[0]) + asked[2:]))]
    found += [("a question said put at a prompt", six, dataclasses.replace(six.result, questions=(dataclasses.replace(asked[0], put=True),) + asked[1:]))]
    found += [("a question's standing reading changed", six, dataclasses.replace(six.result, questions=(dataclasses.replace(asked[0], read_as_now="code"),) + asked[1:]))]
    one = ran.runs["G1"]
    found += [("a profile's made-up column dropped from carried", one, dataclasses.replace(one.result, carried=one.result.carried[1:]))]
    found += [("a profile's tally miscounted", one, dataclasses.replace(one.result, tally=one.result.tally[:-1] + (("held", 1),)))]
    return found


def test_k_s5_01_a_corrupted_result_is_never_met(ran: Battery) -> None:
    """Each field corrupted alone leaves its case unmet, so the checker can fail."""
    for name, run, corrupted in _corruptions(ran):
        assert unmet(run, run.result) == [], name
        assert unmet(run, corrupted), f"the checker met a result with {name}"


def test_the_command_files_and_rule_keys_are_the_row_s(ran: Battery) -> None:
    """Clause (j) on its own (lane S5a's repair 1): the fields lanes TT and TS read.

    Every case's command and files are its row's, and each unjudged
    entry of validate carries its producer check's rule key; the command
    changed, a file dropped or a key changed is found by this clause alone.
    """
    wrong = {
        key: found
        for key, run in classed(ran).items()
        if (found := recorded_fields_unmet(run, run.result))
    }
    assert not wrong, wrong
    keyed = [run for run in classed(ran).values() if run.result.unjudged and run.outcome is not None]
    assert {run.case.key for run in keyed} >= {"M5", "M9"}
    for name, run, corrupted in _corruptions(ran):
        if name in ("the command changed", "a file dropped", "an unjudged entry's rule key changed"):
            assert recorded_fields_unmet(run, corrupted), name


def test_inside_is_none_where_the_measured_side_is_kept_back(ran: Battery) -> None:
    """A window check whose measured side V5 keeps back carries `inside` None (lane S5a's repair 1)."""
    described = rendering.contract.load_profile(f"{ran.root / 'G1' / 't-profile.json'}")
    window = "70.1 (between 69.0 and 71.0)"
    checks = (
        validation.Check("weight", "numeric.mean", "moments.mean", validation.WITHIN_BOUND, window, "", "c", judged="window", approximate=True),
        validation.Check("weight", "numeric.std", "moments.std", validation.MISSED, window, "", judged="window", approximate=True),
        validation.Check("weight", "numeric.skew", "moments.skew", validation.WITHIN_BOUND, window, "70.2", "c", judged="window", approximate=True),
        validation.Check("weight", "numeric.kurtosis", "moments.kurtosis", validation.WITHHELD, window, "", "c", judged="window", approximate=True),
    )
    outcome = validation.Outcome(checks, (), validation.Census(0, 2, 0, 1, 1, 0), "t-twin.csv")
    session = cli._Session(None, None)
    cli._OPEN.sessions += [session]
    try:
        cli._validated(described, outcome)
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    insides = [entry.measures[0].inside for entry in session.carried if entry.kind == "approximate"]
    assert insides == [None, None, True, None]
    assert [miss.shown for miss in session.misses] == [False]


# -- K-S5-02: every byte held ------------------------------------------


def compared(ran: Battery) -> "dict[str, tuple[list[str], list[str]]]":
    """Each recorded case run, its records against its goldens: (differences, skips).

    Case by case through the recorder's own comparison, so a difference
    is counted against the case that holds it without reading its words.
    """
    found: "dict[str, tuple[list[str], list[str]]]" = {}
    for key, run in ran.runs.items():
        if not run.case.recorded:
            continue
        held = types.SimpleNamespace(
            RECORDS=tuple(record for record in goldens.RECORDS if record[0] == key),
            RECORDER_PYTHON=goldens.RECORDER_PYTHON,
        )
        made = [record for record in ran.records if record[0] == key]
        found[key] = RECORDER.compare(made, held, ran.root)
    return found


def test_k_s5_02_every_record_equals_the_goldens(ran: Battery) -> None:
    """Every file, screen run and exit status of the battery equals its golden."""
    differences = [
        line for moved, _skips in compared(ran).values() for line in moved
    ]
    assert not differences, "\n".join(differences)


def test_k_s5_02_the_goldens_digests_hold() -> None:
    """The records, the battery's table of cases and the recorder are those recorded."""
    assert RECORDER.consistency(goldens) == []


def kpi_values(ran: Battery) -> "dict[str, dict[str, int]]":
    """`K-S5-01`'s and `K-S5-02`'s values over one run of the battery (the driver's).

    `K-S5-01`: the cases that name a class, those met, and the corrupted
    results the checker met (each must be unmet). `K-S5-02`: the records
    compared and skipped, those that differ and the cases holding them,
    and the goldens' digests that differ from the ones computed again.
    """
    cases = classed(ran)
    met = [key for key, run in cases.items() if not unmet(run, run.result)]
    corruptions = _corruptions(ran)
    corrupted_met = [
        name for name, run, corrupted in corruptions if not unmet(run, corrupted)
    ]
    moved = compared(ran)
    return {
        "K-S5-01": {
            "cases": len(cases),
            "cases_met": len(met),
            "cases_unmet": len(cases) - len(met),
            "corrupted_results": len(corruptions),
            "corrupted_results_met": len(corrupted_met),
        },
        "K-S5-02": {
            "cases_compared": len(moved),
            "records_compared": len(
                [record for record in ran.records if record[0] in moved]
            ),
            "records_skipped": sum(len(skips) for _lines, skips in moved.values()),
            "records_differing": sum(len(lines) for lines, _skips in moved.values()),
            "cases_differing": len([key for key, (lines, _skips) in moved.items() if lines]),
            "digests_differing": len(RECORDER.consistency(goldens)),
        },
    }


# -- the rank, decided once ---------------------------------------------


def test_the_rank_table_is_total_over_the_registry() -> None:
    """Every fact the disposition registry names has a tier in the rank table."""
    lacking = [
        f"{fact.group}.{fact.field}"
        for fact in dispositions.REGISTRY
        if results._ranked(f"{fact.group}.{fact.field}", "") is None
    ]
    assert not lacking, lacking


def test_every_miss_key_on_the_battery_is_in_the_rank_table(ran: Battery) -> None:
    """No miss the battery makes is ranked by the fallback."""
    lacking = [
        (key, miss.fact, miss.subcheck)
        for key, run in ran.runs.items()
        for miss in run.result.misses
        if miss.judged != results.JUDGED_WINDOW and results._ranked(miss.fact, miss.subcheck) is None
    ]
    assert not lacking, lacking


def test_the_censuses_of_a_writing_fact_rank_count() -> None:
    """The form and mark censuses rank `count`; the cells wearing no named mark `writing` (lane S5a's repair 1).

    Each published form of an identifier's layouts or a number column's
    spellings, and each published mark of a datetime column, is checked
    as a census of the cells wearing it (`validation._form_checks`,
    `_mark_checks`), which part 2 ranks `count`.
    """
    table = (
        ("identifier.layout_forms", "forms.published.@@@%%%%%%", "count"),
        ("numeric.number_spellings", "spellings.published.07", "count"),
        ("datetime.datetime_separators", "marks.T", "count"),
        ("datetime.datetime_separators", "marks.unnamed", "writing"),
        ("datetime.datetime_separators", "", "writing"),
        ("label.shape_forms", "forms.published.@@", "count"),
        ("numeric.numeric_styles", "styles.spelled", "writing"),
        ("identifier.layout_prefixes", "prefix.@@@%%%%%%", "writing"),
        # the orchestrator's ruling of 2026-10-26 (lane S5a's repair 2): an
        # exact census of cells per missing spelling ranks count
        ("universal.missing_by_source", "holes.by_source.NA", "count"),
        ("universal.sentinel_verdicts", "", "writing"),
    )
    for fact, subcheck, tier in table:
        assert results.tier_of(fact, subcheck, "exact") == tier, (fact, subcheck)


def test_m4_s_layout_census_ranks_count(ran: Battery) -> None:
    """Twelve rows dropped move the record number's layout census, which ranks behind no spelling."""
    layouts = [miss for miss in ran.runs["M4"].result.misses if miss.fact == "identifier.layout_forms"]
    assert layouts and all(miss.tier == "count" for miss in layouts), layouts


def _generator_keys() -> "list[tuple[int, str]]":
    """Every fact key the generator writes as a literal or a module's constant (an AST scan of `generation`)."""
    import ast

    from synthtwin import calendar_clock, calendar_rules

    modules = {"calendar_rules": calendar_rules, "calendar_clock": calendar_clock}
    tree = ast.parse(pathlib.Path(generation.__file__).read_text(encoding="utf-8"))
    found: "list[tuple[int, str]]" = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        called = node.func
        name = called.id if isinstance(called, ast.Name) else getattr(called, "attr", "")
        if name not in ("_deviation", "Deviation"):
            continue
        given = node.args[1] if len(node.args) >= 2 else None
        for keyword in node.keywords:
            if keyword.arg == "fact":
                given = keyword.value
        if isinstance(given, ast.Constant) and isinstance(given.value, str):
            found += [(node.lineno, given.value)]
        elif (
            isinstance(given, ast.Attribute)
            and isinstance(given.value, ast.Name)
            and given.value.id in modules
        ):
            found += [(node.lineno, getattr(modules[given.value.id], given.attr))]
    return found


def _registry_pairs() -> "set[tuple[str, str]]":
    return {(fact.group, fact.field) for fact in dispositions.REGISTRY}


def _in_the_registry(fact: str) -> bool:
    """A result's fact is a registry `group.field`, less a ladder end and an index."""
    plain = re.sub(r"\[[0-9]+\]", "", fact)
    for end in (".min", ".max"):
        if plain.endswith(end):
            plain = plain[: -len(end)]
    group, _dot, field = plain.partition(".")
    return (group, field) in _registry_pairs()


def test_every_miss_fact_is_a_registry_fact(ran: Battery) -> None:
    """A miss names the registry's `group.field`, on the battery and for every key the generator writes.

    Lane S5a's repair 1: `levels -> variants_withheld` is the label
    group's `variants_withheld`, and the column-level counts (present,
    missing, out of range) are `universal` whatever the role, and so is
    the time grain, which the registry holds in that group since lane S5b
    (plan P4-D441).
    The validator's two byte rules (`validation.BYTE_RULE_FACTS`) are the
    contract's rules of the file's bytes, named apart from the registry
    as the suite's entry table names them.
    """
    lacking = [
        (key, miss.fact)
        for key, run in ran.runs.items()
        for miss in run.result.misses
        if not _in_the_registry(miss.fact) and miss.fact not in validation.BYTE_RULE_FACTS
    ]
    assert not lacking, lacking


def test_every_key_the_generator_writes_is_named_as_the_registry_names_it() -> None:
    """Each literal key of `generation`'s deviations, named by `cli._registry_fact`, is a registry fact.

    Its column-level counts are `universal` under every group, and every
    other key is a field of some group's (lane S5a's repair 1); the time
    grain is the universal group's since lane S5b (plan P4-D441), so no
    key the generator writes is outside the registry.
    """
    keys = _generator_keys()
    assert len(keys) >= 60, len(keys)
    universal = {field for group, field in _registry_pairs() if group == "universal"}
    groups = sorted({group for group, _field in _registry_pairs()} - {"universal", "document"})
    wrong = []
    for line, key in keys:
        field = key.split(" -> ")[-1]
        if _head(field) in universal:
            if any(cli._registry_fact(group, key, "") != f"universal.{field}" for group in groups):
                wrong += [(line, key, "not universal")]
            continue
        if not any(_in_the_registry(cli._registry_fact(group, key, "")) for group in groups):
            wrong += [(line, key, "in no group")]
    assert not wrong, wrong
    # cli's list of column-level keys is the registry's, the time grain among them
    assert "time_grain" in universal
    assert set(cli._UNIVERSAL_FACTS) <= universal
    assert {_head(key.split(" -> ")[-1]) for _line, key in keys} & universal <= set(cli._UNIVERSAL_FACTS)


def test_judged_is_window_at_the_sites_the_page_names(ran: Battery) -> None:
    """M7's misses are judged against windows; M10's two width misses and D1's ladder end exactly."""
    assert all(miss.judged == "window" for miss in ran.runs["M7"].result.misses)
    widths = [miss for miss in ran.runs["M10"].result.misses if miss.fact == "datetime.date_field_widths"]
    assert {miss.subcheck for miss in widths} >= {"widths.padded", "widths.unnamed"}
    assert all((miss.judged, miss.tier) == ("exact", "count") for miss in widths)
    ladder = [miss for miss in ran.runs["D1"].result.misses if miss.fact == "numeric.percentiles.min"]
    assert ladder and ladder[0].judged == "exact"
    assert any(miss.judged == "window" for miss in ran.runs["D1"].result.misses)


def _returns_marked(name: str) -> "list[int]":
    """The lines of `validation.<name>`'s returns that are not marked `_judged_window`."""
    import ast

    tree = ast.parse(pathlib.Path(validation.__file__).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return [
                inner.lineno
                for inner in ast.walk(node)
                if isinstance(inner, ast.Return)
                and inner.value is not None
                and not (
                    isinstance(inner.value, ast.Call)
                    and isinstance(inner.value.func, ast.Name)
                    and inner.value.func.id == "_judged_window"
                )
            ]
    raise AssertionError(f"validation has no function {name}")


def _function(name: str) -> typing.Any:
    import ast

    tree = ast.parse(pathlib.Path(validation.__file__).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"validation has no function {name}")


def test_every_window_check_is_marked_where_it_is_made() -> None:
    """`_within`, `_within_clock`, `_within_instant` and `_tail_window_check` mark every check."""
    import ast

    for name in ("_within", "_within_clock", "_within_instant", "_tail_window_check"):
        assert _returns_marked(name) == [], name
    # `_lesser_or_held` (lane S5a's repair 1): where the description gives
    # the corner no window, every check is exact -- withheld, held or the
    # deviation, three returns inside that one branch; where it gives one,
    # every check is marked, held and withheld included.
    unmarked = _returns_marked("_lesser_or_held")
    assert len(unmarked) == 3, unmarked
    windowless = [
        node
        for node in ast.walk(_function("_lesser_or_held"))
        if isinstance(node, ast.If) and "supply is None" in ast.unparse(node.test)
    ]
    assert len(windowless) == 1
    inside = {inner.lineno for inner in ast.walk(windowless[0]) if isinstance(inner, ast.Return)}
    assert set(unmarked) == inside, (unmarked, inside)
    # The compound column's distinctness (`_distinctness_checks`): marked
    # where its window's two ends differ, exact where they meet.
    compound = [
        node
        for node in ast.walk(_function("_distinctness_checks"))
        if isinstance(node, ast.If) and "CompoundFacts" in ast.unparse(node.test)
    ]
    assert len(compound) == 1
    text = ast.unparse(compound[0])
    assert text.count("_judged_window(") == 2, text
    assert "outside if low == high else _judged_window(outside," in text


# -- part 3: `run` prints nothing; each command reaches only its own modules --


def test_run_given_no_screen_and_no_reader_prints_nothing(ran: Battery, tmp_path: pathlib.Path) -> None:
    """No screen, no reader: nothing reaches the process's streams, and the files are as the command writes them."""
    folder = tmp_path / "quiet"
    folder.mkdir()
    for name in ("t-profile.json", "t-twin.csv"):
        (folder / name).write_bytes((ran.root / "G1" / name).read_bytes())
    lines = [
        ("validate", "t-profile.json"),
        (),
        ("--help",),
        ("--version",),
        ("profile", "t.csv", "--no-such-option"),
        ("profile", "missing.csv"),
        ("generate", "t-profile.json", "--seed", "-1"),
        ("--s", "1"),
    ]
    for argv in lines:

        def quiet(given: "list[str]", _write: "typing.Callable[[str, str], None]") -> int:
            return results.exit_code(cli.run(given, small_tables_refused=True))

        captured = RECORDER.capture(argv, folder, quiet)
        assert captured.runs == [] and captured.strays == [] and captured.reads == 0, argv
    # ...and a profile and a generate that run whole, each writing its files.
    whole = tmp_path / "quiet-whole"
    whole.mkdir()
    (whole / "t.csv").write_bytes((ran.root / "G1" / "t.csv").read_bytes())
    for argv, verdict in (
        (("profile", "t.csv", "--identifier", "record_no"), "no-miss"),
        # G2's: the weight's commonest value given up at the table floor.
        (("generate", "t-profile.json", "--seed", "7"), "missed"),
    ):
        made: "list[results.Result]" = []

        def kept(given: "list[str]", _write: "typing.Callable[[str, str], None]") -> int:
            made.extend([cli.run(given, small_tables_refused=True)])
            return results.exit_code(made[-1])

        captured = RECORDER.capture(argv, whole, kept)
        assert captured.runs == [] and captured.strays == [] and captured.reads == 0, argv
        assert made[-1].verdict == verdict and made[-1].files, argv
    golden = [
        record
        for record in goldens.RECORDS
        if record[0] == "G3" and record[1] == "file" and record[2] == "t-twin-quality.txt"
    ]
    data = (folder / "t-twin-quality.txt").read_bytes()
    assert golden and golden[0][3] == RECORDER._digest(data)


def test_main_and_run_show_the_same_characters(ran: Battery, tmp_path: pathlib.Path) -> None:
    """`main` is `exit_code(run(..., screen=TERMINAL))`: the terminal shows what a list receives."""
    for argv in ((), ("--help",), ("--version",), ("profile", "t.csv", "--no-such-option"), ("--s", "1")):
        through_main = RECORDER.capture(argv, tmp_path)

        def listed(given: "list[str]", write: "typing.Callable[[str, str], None]") -> int:
            screen: "list[tuple[str, str]]" = []
            result = cli.run(given, screen=screen, small_tables_refused=True)
            for stream, text in screen:
                write(stream, text)
            return results.exit_code(result)

        through_run = RECORDER.capture(argv, tmp_path, listed)
        assert (through_main.exit, through_main.runs) == (through_run.exit, through_run.runs), argv


_FRESH = """
import sys
from synthtwin import cli, results
result = cli.run(sys.argv[1:], small_tables_refused=False)
print(result.command, result.verdict, results.exit_code(result))
print(" ".join(sorted(name for name in sys.modules if name.startswith(("synthtwin", "pandas", "numpy")))))
"""


def _fresh(folder: pathlib.Path, *argv: str) -> "tuple[str, set[str]]":
    env = dict(os.environ)
    package = pathlib.Path(cli.__file__).resolve().parents[1]
    env["PYTHONPATH"] = os.pathsep.join([f"{package}"] + [part for part in env.get("PYTHONPATH", "").split(os.pathsep) if part])
    done = subprocess.run(
        [sys.executable, "-c", _FRESH, *argv],
        cwd=folder,
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=600,
    )
    said, loaded = done.stdout.strip().split("\n")
    return said, set(loaded.split())


def test_a_validate_run_reaches_no_generator_and_a_generate_run_no_reader(tmp_path: pathlib.Path) -> None:
    """V10's boundary, read off a fresh interpreter's `sys.modules` after `cli.run`."""
    table = tmp_path / "t.csv"
    table.write_text(battery.step0_table(400), encoding="utf-8", newline="\n")
    assert cli.main(["profile", f"{table}", "--identifier", "record_no"], small_tables_refused=False) == 0
    said, loaded = _fresh(tmp_path, "generate", "t-profile.json", "--seed", "7")
    assert said == "generate no-miss 0", said
    assert "synthtwin.generation" in loaded
    assert not {"synthtwin.reading", "synthtwin.validation", "pandas"} & loaded, loaded
    said, loaded = _fresh(tmp_path, "validate", "t-profile.json")
    assert said == "validate no-miss 0", said
    assert "synthtwin.validation" in loaded
    assert not {"synthtwin.generation", "synthtwin.rendering"} & loaded, loaded


def test_a_stop_at_writing_after_the_report_keeps_its_misses(
    ran: Battery, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Validate refused at `writing` after its report was shown keeps the misses it showed, exit 1."""
    folder = tmp_path / "stopped"
    folder.mkdir()
    for name in ("t-profile.json", "t-twin.csv"):
        (folder / name).write_bytes((ran.root / "M7" / name).read_bytes())
    sentence = "The battery's injected stop: the quality report was not written, and nothing is at its name."

    def stopping(target: typing.Any, *_given: typing.Any, **named: typing.Any) -> typing.Any:
        named["state"].sentence = sentence
        raise errors.TransactionRefusal(sentence)

    monkeypatch.setattr(writing, "write_one_file", stopping)
    screen: "list[tuple[str, str]]" = []
    here = os.getcwd()
    os.chdir(folder)
    try:
        result = cli.run(["validate", "t-profile.json"], screen=screen, small_tables_refused=True)
    finally:
        os.chdir(here)
    assert result.verdict == "refused" and results.exit_code(result) == 1
    assert result.refusal is not None and result.refusal.step == "writing"
    assert result.misses == ran.runs["M7"].result.misses
    assert result.files == ()


def test_every_caution_key_is_one_the_command_gives() -> None:
    """`results.CAUTIONS` holds exactly the keys `cli` gives a caution under: none unused, none unlisted."""
    import re

    given = set(re.findall(r"results\.(CAUTION_[A-Z_]+)", pathlib.Path(cli.__file__).read_text(encoding="utf-8")))
    listed = {name for name in vars(results) if name.startswith("CAUTION_")}
    assert given == listed, (sorted(given - listed), sorted(listed - given))
    assert set(results.CAUTIONS) == {getattr(results, name) for name in listed}
    assert len(results.CAUTIONS) == len(set(results.CAUTIONS))


# -- the parser's own words ------------------------------------------------

# argparse's usage block on the recorder's Python (3.11) at 80 columns,
# as the base f677d6a0 showed it before every ambiguous-option refusal.
_USAGE_311 = (
    "usage: synthtwin [-h] [--version] [--twin PATH] [--out-dir FOLDER]\n"
    "                 [--seed NUMBER] [--replace] [--smallest-group ROWS]\n"
    "                 [--identifier COLUMN] [--code COLUMN]\n"
    "                 [--decimal-comma COLUMN] [--measurement COLUMN]\n"
    "                 [--century COLUMN=YEAR] [--date-column COLUMN]\n"
    "                 [--twelve-hour COLUMN] [--date-count COLUMN SYSTEM]\n"
    "                 [--metadata-rows N] [--delimiter CHARACTER] [--answers FILE]\n"
    "                 [--keep-value VALUE] [--missing-value VALUE] [--day-first]\n"
    "                 [--sheet NAME] [--first-row {auto,names,data}]\n"
    "                 [{profile,generate,validate,doctor}] [path]\n"
)


def _argparse_sorts_first() -> bool:
    """Whether this Python's argparse refuses an ambiguous word as it sorts the words (3.11's way).

    Asked of argparse itself, on a parser of its own with its own help
    option: the help word first, an ambiguous word after it. Sorting
    first, it refuses (exit 2); reading in order, it shows the help (0).
    """
    import argparse
    import contextlib
    import io

    probe = argparse.ArgumentParser(prog="probe")
    probe.add_argument("--alpha")
    probe.add_argument("--also")
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            probe.parse_known_args(["--help", "--al"])
        except SystemExit as stop:
            return stop.code == 2
    raise AssertionError("argparse's help option did not stop")


def test_the_ambiguity_rule_is_this_python_s() -> None:
    """`cli._AMBIGUITY_SORTED_FIRST` is how this Python's argparse refuses an ambiguous word (lane S5a's repair 2)."""
    assert cli._AMBIGUITY_SORTED_FIRST == _argparse_sorts_first()


def test_an_ambiguous_word_after_the_help_word_is_refused_as_before(tmp_path: pathlib.Path) -> None:
    """A word abbreviating several options, after the help word: answered as this Python's argparse answered it.

    Lane S5a's repair 1: the base f677d6a0 answered these three lines
    under Python 3.11 with exit 2, its usage block and argparse's
    ambiguous-option line; lane S5a's repair 2 (Codex's item 3): on a
    Python whose argparse refuses the word only when it reaches it
    (3.12.7 and later), the base showed the help page with exit 0. Through
    `main` and through `run` they still do.
    """
    lines = (
        (("--help", "--d"), "--d could match --decimal-comma, --date-column, --date-count, --delimiter, --day-first"),
        (("-h", "--da"), "--da could match --date-column, --date-count, --day-first"),
        (("profile", "x.csv", "-h", "--tw"), "--tw could match --twin, --twelve-hour"),
    )
    usage = _USAGE_311
    page = RECORDER.capture(("--help",), tmp_path)
    if f"{sys.version_info[0]}.{sys.version_info[1]}" != goldens.RECORDER_PYTHON:
        # argparse lays its usage out per Python: read it off this one's help page.
        usage = page.runs[0][1].split("\n\n")[0] + "\n"
    for argv, matches in lines:
        wanted = [("err", usage + f"synthtwin: error: ambiguous option: {matches}\n")]
        status, verdict = 2, "unusable"
        if not _argparse_sorts_first():
            wanted, status, verdict = page.runs, 0, "no-miss"
        through_main = RECORDER.capture(argv, tmp_path)
        assert (through_main.exit, through_main.runs) == (status, wanted), argv

        def listed(given: "list[str]", write: "typing.Callable[[str, str], None]") -> int:
            screen: "list[tuple[str, str]]" = []
            result = cli.run(given, screen=screen, small_tables_refused=True)
            command = ("profile" if "profile" in given else "") if verdict == "unusable" else "help"
            assert (result.verdict, result.command) == (verdict, command)
            for stream, text in screen:
                write(stream, text)
            return results.exit_code(result)

        through_run = RECORDER.capture(argv, tmp_path, listed)
        assert (through_run.exit, through_run.runs, through_run.strays) == (status, wanted, []), argv


# THE LINES argparse ITSELF ANSWERS, by refusing them or showing its help
# page: abbreviations, help words run together, options short of values,
# values that look like options. Each is held below to what argparse
# answers on the Python that runs the gate, read off argparse with its own
# help option, as the base f677d6a0 used it.
_PARSER_LINES = (
    ("--help", "--d"), ("-h", "--da"), ("profile", "x.csv", "-h", "--tw"), ("--d", "--help"),
    ("--seed", "--d"), ("--seed", "5", "--d"), ("profile", "--d", "x.csv"), ("--d",), ("--d=5",),
    ("-hh",), ("-hhh",), ("-hfoo",), ("-h=h",), ("-h=x",), ("-hh", "--d"), ("--d", "-hh"),
    ("--out-dir", "-hh"), ("--out-dir", "-h"), ("frobnicate",), ("frobnicate", "-h"), ("-h", "frobnicate"),
    ("profile", "--seed"), ("--he",), ("--h",), ("--help=x",), ("--he=x",), ("-h x",), ("--", "-h"),
    ("--sheet", "--d"), ("--seed", "-hh"), ("--date-count", "a", "--d"), ("--date-count", "a", "-h"),
    ("--date-count", "-h", "a"), ("--date-count", "a", "b", "-h"), ("--version", "--d"), ("-hx", "--d"),
    ("profile", "-hfoo", "--d"), ("--first-row", "names", "-hh"), ("frob", "-hh"), ("--he", "--d"),
    ("--date-count", "--d", "-h", "x"), ("--d=\x1b[31m",), ("--keep-value", "-h"),
    ("-hh", "--seed"), ("-hfoo", "--seed"), ("-h", "--seed"), ("--seed", "-h"), ("-hh", "frob"),
)


def _base_parser() -> typing.Any:
    """The command's own parser, given back argparse's help option and its exits, as the base had them."""
    import argparse

    seen: "list[argparse.ArgumentParser]" = []
    original = argparse.ArgumentParser.parse_known_args

    def caught(self: argparse.ArgumentParser, *_given: object, **_named: object) -> object:
        seen.extend([self])
        raise SystemExit(0)

    argparse.ArgumentParser.parse_known_args = caught  # type: ignore[assignment,method-assign]
    try:
        with pytest.raises(SystemExit):
            cli._parse_arguments(["profile", "x.csv"], None)
    finally:
        argparse.ArgumentParser.parse_known_args = original  # type: ignore[method-assign]
    parser = seen[0]
    parser.exit_on_error = True
    helper = parser._option_string_actions["-h"]
    helper.__class__ = argparse._HelpAction  # type: ignore[assignment]
    helper.default = argparse.SUPPRESS
    return parser


def test_argparse_s_own_answer_on_this_python_is_kept(tmp_path: pathlib.Path) -> None:
    """Every line argparse answers shows, through `main` and `run`, what argparse showed here (lane S5a's repair 2).

    Codex's items 2 to 4: a help word run together (`-hh`, `-hfoo`) shows
    the help page wherever this Python's argparse shows it, and never by
    argparse's own print; an ambiguous word is refused where this
    Python's argparse refuses it; and a refusal keeps its words in the
    result, the characters shown less the last line feed, with no screen
    at all too. A line argparse reads through is answered by the command.
    """
    parser = _base_parser()
    stopped = 0
    for argv in _PARSER_LINES:

        def by_argparse(given: "list[str]", _write: "typing.Callable[[str, str], None]") -> int:
            try:
                parser.parse_known_args(given)
            except SystemExit as stop:
                return int(f"{stop.code}")
            return -1

        oracle = RECORDER.capture(argv, tmp_path, by_argparse)
        through_main = RECORDER.capture(argv, tmp_path)
        quiet = cli.run(list(argv), small_tables_refused=True)
        if oracle.exit < 0:
            assert not any(text.startswith("usage: ") for _stream, text in through_main.runs), argv
            continue
        stopped = stopped + 1
        assert (through_main.exit, through_main.runs) == (oracle.exit, oracle.strays), argv
        screen: "list[tuple[str, str]]" = []

        def listed(given: "list[str]", write: "typing.Callable[[str, str], None]") -> int:
            result = cli.run(given, screen=screen, small_tables_refused=True)
            for stream, text in screen:
                write(stream, text)
            return results.exit_code(result)

        through_run = RECORDER.capture(argv, tmp_path, listed)
        assert (through_run.exit, through_run.runs, through_run.strays) == (oracle.exit, oracle.strays, []), argv
        if oracle.exit == 0:
            assert quiet.verdict == "no-miss" and quiet.command == "help", argv
            continue
        shown = "".join(text for _stream, text in screen)
        assert quiet.verdict == "unusable" and quiet.refusal is not None, argv
        assert quiet.refusal.words == shown[: len(shown) - 1] and quiet.refusal.words, argv
    assert stopped >= 30, stopped


def test_the_command_is_the_one_argparse_read(ran: Battery, tmp_path: pathlib.Path) -> None:
    """A command word standing as an option's value names no command (lane S5a's repair 2, Codex's item 1).

    `--out-dir profile validate` validates into a folder named `profile`:
    the run is validate's, its miss exit 3; `--out-dir validate generate`
    generates into `validate`: generate's, its miss exit 0.
    """
    folder = tmp_path / "words"
    folder.mkdir()
    for name in ("t-profile.json", "t-twin.csv"):
        (folder / name).write_bytes((ran.runs["M7"].folder / name).read_bytes())
    (folder / "profile").mkdir()
    (folder / "validate").mkdir()
    here = os.getcwd()
    os.chdir(folder)
    try:
        checked = cli.run(["--out-dir", "profile", "validate", "t-profile.json"], small_tables_refused=True)
        made = cli.run(["--out-dir", "validate", "generate", "t-profile.json", "--seed", "7"], small_tables_refused=True)
    finally:
        os.chdir(here)
    assert (checked.command, checked.verdict, results.exit_code(checked)) == ("validate", "missed", 3)
    assert (made.command, made.verdict, results.exit_code(made)) == ("generate", "missed", 0)
    assert [one.kind for one in made.files] == ["twin", "twin-report"]


def test_the_long_options_are_the_parser_s_in_its_order() -> None:
    """`cli._LONG_OPTIONS` is the parser's own list, so an ambiguous word names argparse's matches."""
    import argparse

    seen: "list[str]" = []
    shorts: "list[str]" = []
    original = argparse.ArgumentParser.parse_known_args

    def caught(self: argparse.ArgumentParser, *_given: object, **_named: object) -> object:
        seen.extend([option for option in self._option_string_actions if option.startswith("--")])
        shorts.extend([option for option in self._option_string_actions if not option.startswith("--")])
        usage = self.format_usage()
        assert self.format_help().split("\n\n")[0] + "\n" == usage
        raise SystemExit(0)

    argparse.ArgumentParser.parse_known_args = caught  # type: ignore[assignment,method-assign]
    try:
        with pytest.raises(SystemExit):
            cli._parse_arguments(["profile", "x.csv"], None)
    finally:
        argparse.ArgumentParser.parse_known_args = original  # type: ignore[method-assign]
    assert tuple(seen) == cli._LONG_OPTIONS
    # ...and `-h` is its one short option, which `cli._could_ask_for_help`
    # takes a word of short options run together to begin with (repair 2).
    assert tuple(shorts) == ("-h",)


# -- lane S5a's repair 2: Codex's items 5 to 8 -----------------------------


def _carried_approximately(result: results.Result) -> "list[tuple[tuple[str, ...], str, str]]":
    return sorted((one.subject, one.fact, one.subcheck) for one in result.carried if one.kind == "approximate")


def _step0_rows(text: str) -> "list[list[str]]":
    return [line.split(",") for line in text.split("\n") if line]


def test_what_validate_carries_follows_the_description_whatever_the_file_lacks(
    ran: Battery, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Columns the file lacks, no rows, no names, a closed gate: the same approximate entries (Codex's item 5).

    Lane S5a's repair 2: the copies that put a verdict no window decided
    keep `Check.approximate`, so validate's inventory of what is carried
    approximately is the description's -- G3's, of the good twin -- and
    each miss the absence decided is `exact`, its entry's `inside` None.
    """
    good = _carried_approximately(ran.runs["G3"].result)
    assert len(good) == 33, len(good)
    twin = (ran.root / "G1" / "t-twin.csv").read_text(encoding="utf-8")
    rows = _step0_rows(twin)
    place = rows[0].index("weight")
    # The validator finds a column by its position: a file of the columns
    # before the weight holds no column at the weight's number, or after.
    lacking = "\n".join(",".join(row[:place]) for row in rows) + "\n"
    header_only = ",".join(rows[0]) + "\n"
    for name, text in (("lacking", lacking), ("no-rows", header_only)):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "t-profile.json").write_bytes((ran.root / "G1" / "t-profile.json").read_bytes())
        (folder / "t-twin.csv").write_text(text, encoding="utf-8", newline="\n")
        monkeypatch.chdir(folder)
        result = cli.run(["validate", "t-profile.json"], small_tables_refused=True)
        assert result.verdict == "missed", name
        assert _carried_approximately(result) == good, name
        weight = [one for one in result.carried if one.kind == "approximate" and one.subject == ("weight",)]
        assert weight and all(one.measures[0].inside is None for one in weight), name
        # each miss the absence decided is `exact`
        absences = (validation._NO_COLUMN_HERE, validation._NO_ROWS_HERE, validation._NO_NAMES_HERE)
        absent = [miss for miss in result.misses if miss.achieved in absences]
        assert absent and all(miss.judged == "exact" and miss.tier != "window" for miss in absent), name
    # A header naming no column, and a gate closed over a measured file:
    # the two other copies, asked of the validator directly.
    described = rendering.contract.load_profile(f"{ran.root / 'G1' / 't-profile.json'}")
    unnamed = validation._no_column_is_named(described, "the file's first row names none", True)
    wanted = sorted(((check.column,) if check.column else (), check.fact, check.subcheck) for check in unnamed if check.approximate)
    assert wanted == good
    assert all(check.judged == "exact" for check in unnamed)
    measured = ran.runs["G3"].outcome
    assert measured is not None
    closed = validation._withheld_if(list(measured.checks), True, "the gate's sentence")
    assert [check.approximate for check in closed] == [check.approximate for check in measured.checks]
    # ...the window's ends kept only where the copy's published text still
    # prints them: a tail's or a rung's, printed in the note it drops, go.
    kinds = set()
    for before, after in zip(measured.checks, closed):
        if before.lowest:
            printed = before.published.endswith(f"(between {before.lowest} and {before.highest})")
            kinds.add(printed)
            assert (after.lowest, after.highest, after.covers) == (
                (before.lowest, before.highest, before.covers) if printed else ("", "", None)
            ), (before.fact, before.subcheck)
    assert kinds == {True, False}


def test_a_window_s_ends_are_carried_where_the_report_prints_them(ran: Battery) -> None:
    """Every window the quality report prints is in the result as data, and no other (Codex's item 7).

    For each approximate entry of every validate run: where its check's
    published text ends with the window, or its note says what the file
    is allowed, the measure's `lowest` and `highest` are those printed
    ends; where neither prints one, both are empty; and `covers_published`
    is false exactly where the note says the window does NOT reach the
    description's value, true where it says it covers it.
    """
    in_published = 0
    in_note = 0
    for key, run in ran.runs.items():
        if run.outcome is None or run.result.verdict == "refused":
            continue
        checks = [check for check in run.outcome.checks if check.approximate]
        carried = [one for one in run.result.carried if one.kind == "approximate"]
        assert len(checks) == len(carried), key
        for one, check in zip(carried, checks):
            measure = one.measures[0]
            note = "\n".join(check.note)
            window = re.search(r"\(between (\S+) and (\S+)\)$", check.published)
            where = (key, check.fact, check.subcheck)
            if window:
                in_published = in_published + 1
                assert (measure.lowest, measure.highest) == window.groups(), where
            elif "allowed from" in note:
                # a tail's distances or a rung's distances from its value
                in_note = in_note + 1
                assert measure.lowest and measure.highest, (where, note)
                assert f"allowed from {measure.lowest}" in note, (where, note)
                assert f"to {measure.highest}" in note, (where, note)
            else:
                assert (measure.lowest, measure.highest, measure.covers_published) == ("", "", None), where
            if "does NOT reach" in note:
                assert measure.covers_published is False, where
            if "it covers the value above" in note:
                assert measure.covers_published is True, where
    assert in_published > 0 and in_note > 0, (in_published, in_note)


def test_a_window_s_ends_and_cover_reach_the_result(ran: Battery) -> None:
    """`_within`'s window, published 70.1 and the file 70.2 between 69 and 71, as data (Codex's item 7).

    Beside it the same window against a published 75.0, which it does not
    reach: the cover is false, said in the note as before.
    """
    inside = validation._within("weight", "numeric.mean", "moments.mean", "70.1", 70.2, (69.0, 71.0), "c", value=70.1)
    beside = validation._within("weight", "numeric.std", "moments.std", "75.0", 70.2, (69.0, 71.0), "c", value=75.0)
    assert (inside.verdict, inside.published) == (validation.WITHIN_BOUND, "70.1 (between 69.0 and 71.0)")
    assert beside.verdict == validation.WITHIN_BOUND and "does NOT reach" in "".join(beside.note)
    outcome = validation.Outcome((inside, beside), (), validation.Census(0, 2, 0, 0, 0, 0), "t-twin.csv")
    session = cli._Session(None, None)
    cli._OPEN.sessions += [session]
    try:
        cli._validated(rendering.contract.load_profile(f"{ran.root / 'G1' / 't-profile.json'}"), outcome)
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    measures = [entry.measures[0] for entry in session.carried if entry.kind == "approximate"]
    assert [(one.lowest, one.highest, one.inside, one.covers_published) for one in measures] == [
        ("69.0", "71.0", True, True),
        ("69.0", "71.0", True, False),
    ]


def _compound_count(result: results.Result, field: str) -> results.Carried:
    found = [
        one
        for one in result.carried
        if one.kind == "approximate" and one.subject == ("value",) and one.fact == f"compound.{field}"
    ]
    assert len(found) == 1, result.carried
    return found[0]


def test_a_compound_count_carries_its_window_s_ends_only_beside_a_count_it_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A numbers-with-labels column's count of different values, met and missed inside its window (S5a verify 2, new item 1).

    `validation._distinctness_checks`' compound branch prints the window
    only beside a count the twin did not meet exactly, so its ends are
    carried only there. Measured at 2,000 rows (the library's size, the
    table floor set aside as the joined-ranking case sets it): readings
    0.0 to 29.9 beside `<0.1` and `>99` publish 242 different values in
    G12.8's corner, a window of two different ends (242 and 1602). The
    table itself as the twin meets 242 exactly: HELD, no end carried and
    no cover. Eight readings more, 250: AUTHORIZED-DEVIATION, the ends
    those the quality report prints and the cover true.
    """
    rows = [f"{index},{(index % 300) / 10:.1f}" if index % 5 else f"{index},{'<0.1' if index % 2 else '>99'}" for index in range(2000)]
    more = list(rows)
    for extra in range(8):
        more[5 * extra + 1] = f"{5 * extra + 1},{30 + extra / 10 + 0.1:.1f}"
    monkeypatch.chdir(tmp_path)
    (tmp_path / "t.csv").write_text("id,value\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    (tmp_path / "more.csv").write_text("id,value\n" + "\n".join(more) + "\n", encoding="utf-8", newline="\n")
    assert cli.run(["profile", "t.csv", "--identifier", "id"], small_tables_refused=False).verdict == "no-miss"
    document = json.loads((tmp_path / "t-profile.json").read_text(encoding="utf-8"))
    described = [column for column in document["columns"] if column["name"] == "value"][0]
    assert described["role"] == "numbers_with_labels"
    loaded = rendering.contract.load_profile(f"{tmp_path / 't-profile.json'}")
    column = [one for one in loaded.columns if one.name == "value"][0]
    assert isinstance(column.facts, rendering.contract.CompoundFacts)
    mine = validation.corners_of(loaded)["value"]
    low, high, _said = validation._compound_window(column, column.facts, mine, "n_distinct")
    assert (low, high, column.n_distinct) == (242, 1602, 242)
    met = cli.run(["validate", "t-profile.json", "--twin", "t.csv"], small_tables_refused=False)
    held = _compound_count(met, "n_distinct")
    assert held.verdict == validation.HELD, held
    assert (held.measures[0].lowest, held.measures[0].highest, held.measures[0].covers_published) == ("", "", None)
    assert "between" not in held.measures[0].published
    missed = cli.run(["validate", "t-profile.json", "--twin", "more.csv"], small_tables_refused=False)
    inside = _compound_count(missed, "n_distinct")
    assert inside.verdict == validation.AUTHORIZED_DEVIATION, inside
    assert inside.measures[0].achieved == "250", inside
    printed = re.search(r"\(between (\S+) and (\S+)\)$", inside.measures[0].published)
    assert printed is not None, inside.measures[0].published
    assert (inside.measures[0].lowest, inside.measures[0].highest) == printed.groups() == ("242.0", "1602.0")
    assert inside.measures[0].covers_published is True


def test_joined_positions_rank_as_columns_of_numbers(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A joined position's type miss ranks `writing`, ahead of an earlier column's counts (Codex's item 6).

    The validator names a position's facts `joined.parts[N].X`, its
    subcheck led by `number N+1`; the rank reads them back as the number
    column's `numeric.X`. Measured on 2,000 readings `100/60` to `139/84`
    beside a ward, the first number written with a decimal and 100 wards
    moved: the position's whole-number miss stands before the ward's counts.
    """
    table = [f"{'A' if index % 2 else 'B'},{100 + index % 40}/{60 + index % 25}" for index in range(2000)]
    damaged = [
        f"{'A' if index % 2 or index < 100 else 'B'},{100 + index % 40}.5/{60 + index % 25}" for index in range(2000)
    ]
    monkeypatch.chdir(tmp_path)
    (tmp_path / "t.csv").write_text("ward,bp\n" + "\n".join(table) + "\n", encoding="utf-8", newline="\n")
    (tmp_path / "d.csv").write_text("ward,bp\n" + "\n".join(damaged) + "\n", encoding="utf-8", newline="\n")
    assert cli.run(["profile", "t.csv", "--measurement", "bp"], small_tables_refused=False).verdict == "no-miss"
    checked = cli.run(["validate", "t-profile.json", "--twin", "d.csv"], small_tables_refused=False)
    whole = [miss for miss in checked.misses if miss.fact == "joined.parts[0].integer_valued"]
    assert whole and whole[0].tier == "writing", whole
    first_count = [place for place, miss in enumerate(checked.misses) if miss.tier == "count"][0]
    assert checked.misses.index(whole[0]) < first_count
    assert any(miss.column == "ward" and miss.tier == "count" for miss in checked.misses)
    table_rows = (
        ("joined.parts[0].integer_valued", "type.number 1 is whole", "writing"),
        ("joined.parts[1].numeric_styles", "number 2 styles.spelled", "writing"),
        ("joined.parts[0].numeric_styles", "number 1 styles.published.plain", "count"),
        ("joined.parts[0].number_spellings", "number 1 spellings.published.07", "count"),
        ("joined.parts[0].group_separator", "", "writing"),
        ("joined.parts[0].percentiles", "number 1 ladder.p50", "count"),
        ("joined.parts[12].max", "ends.number 13 max", "count"),
        ("joined.part_above[0]", "above.number 1", "count"),
        ("joined.separator", "", "writing"),
    )
    for fact, subcheck, tier in table_rows:
        assert results.tier_of(fact, subcheck, "exact") == tier, (fact, subcheck)


def test_a_write_the_transaction_refused_names_what_is_on_disk(
    ran: Battery, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A quality report whose working file could not be written: the refusal's `on_disk` is the transaction's account (Codex's item 8)."""
    folder = tmp_path / "unwritten"
    folder.mkdir()
    for name in ("t-profile.json", "t-twin.csv"):
        (folder / name).write_bytes((ran.root / "M7" / name).read_bytes())

    def refusing(*_given: typing.Any, **_named: typing.Any) -> "tuple[str, str]":
        return ("The battery's injected stop: the disk would not take the working file.", errors.ON_DISK_WORKING)

    monkeypatch.setattr(writing, "_write_part", refusing)
    monkeypatch.chdir(folder)
    screen: "list[tuple[str, str]]" = []
    result = cli.run(["validate", "t-profile.json"], screen=screen, small_tables_refused=True)
    assert result.verdict == "refused" and results.exit_code(result) == 1
    assert result.refusal is not None and result.refusal.step == "writing"
    assert result.refusal.on_disk, result.refusal
    assert result.refusal.words.endswith(result.refusal.on_disk)
    assert result.refusal.words.startswith("The battery's injected stop")
    assert result.files == () and result.misses == ran.runs["M7"].result.misses


# -- lane S5b (plan P4-D441): profile's questions and carried as data ----


def _rendered_questions(result: results.Result, kept: "dict[str, bytes]", table_name: str) -> bytes:
    """The questions file rendered from the result's records (plan P4-D441).

    The file's other words are the run's: the table's name, the
    description's sentences about the whole table (its notes naming no
    column, read from the written description), and the answers the run
    acted on, written back for the file handed back (plans P4-D401 and
    P4-D408), which are answers and no question, read from the file.
    """
    notes = json.loads(kept[results.FILE_DESCRIPTION].decode("utf-8"))["publication_notes"]
    about = [note["note"] for note in notes if note["column"] == ""]
    answers: "dict[str, typing.Any]" = (
        json.loads(kept[results.FILE_QUESTIONS].decode("utf-8")) if results.FILE_QUESTIONS in kept else {}
    )
    document = asking.questions_document_of(
        table_name,
        result.questions,
        about,
        answers.get(asking.ANSWERED_BEFORE),
        answers.get(asking.ANSWERED_BEFORE_COLUMNS),
    )
    return canonical.serialize(document).encode("utf-8")


def _golden_digest(key: str, name: str) -> str:
    found = [record[3] for record in goldens.RECORDS if record[:3] == (key, "file", name)]
    assert len(found) == 1, (key, name)
    return typing.cast(str, found[0])


def test_the_questions_file_rendered_from_the_result_is_today_s_file(ran: Battery) -> None:
    """G6's checklist, G1's and G7's: rendered from the result's records, the goldens' bytes (plan P4-D441).

    The goldens were recorded from the code before lane S5a (P4-D437), so
    the records reproduce today's file byte for byte, not merely the file
    this run wrote from them.
    """
    for key in ("G6", "G1", "G7"):
        result = ran.runs[key].result
        assert result.questions, key
        rendered = _rendered_questions(result, ran.runs[key].kept, "t.csv")
        assert hashlib.sha256(rendered).hexdigest() == _golden_digest(key, "t-questions.json"), key


# THE QUESTIONS FILES OF TWO TABLES THE BATTERY DOES NOT HOLD, as the code
# before lane S5b wrote them (S5a's head 87dc440e, measured by lane S5b's
# planning-notes/work-2026-10/wave6/S5b/shapes_probe.py at 20,000 rows):
# a patient key, ZIP codes and ages, whose key and ZIP codes HX's literal
# rule holds (plan P4-D401) and whose questions are asked column by column;
# and dates whose day and month are each at most 12, which raise the
# question about the file of plan P4-D381 (plan P4-D81's section).
_TODAY_S_FILES = {
    "held": "8343dd05b0c747497d9374a924ea77d26166d0972d7523027f4a214dd4081b39",
    "filequestion": "f9a69d985e8802fb2016a7933542441c473467716dc69027ce292203506d199e",
}


def _held_table(rows: int) -> str:
    """A patient key of six figures (2,000 people), a five-figure ZIP code (40), an age 18 to 103, a ward."""
    stream = random.Random(11)
    people = [f"{100000 + stream.randint(0, 899999)}" for _ in range(2000)]
    zips = [f"{52240 + k}" for k in range(40)]
    found = ["patient_key,zip,age,ward"]
    for index in range(rows):
        found += [
            f"{people[index % 2000]},{zips[stream.randint(0, 39)]},{stream.randint(18, 103)},"
            f"{battery.WARDS[index % 4]}"
        ]
    return "\n".join(found) + "\n"


def _day_or_month_table(rows: int) -> str:
    """Dates whose day and month are each at most 12, beside a ward: no value says which comes first."""
    stream = random.Random(7)
    found = ["visit,ward"]
    for index in range(rows):
        found += [f"{stream.randint(1, 12):02d}/{stream.randint(1, 12):02d}/2024,{battery.WARDS[index % 4]}"]
    return "\n".join(found) + "\n"


def _profiled_shape(folder: pathlib.Path, text: str, monkeypatch: pytest.MonkeyPatch) -> results.Result:
    folder.mkdir()
    (folder / "t.csv").write_text(text, encoding="utf-8", newline="\n")
    monkeypatch.chdir(folder)
    return cli.run(["profile", "t.csv"], small_tables_refused=True)


def _record_words(record: results.Asked) -> "list[str]":
    found = [record.column, record.subject, record.role, record.reason, record.saw, record.read_as_now]
    for offer in record.offers:
        found += [offer.answer, offer.means, offer.publishes]
    return found


def _tokens(text: str) -> "set[str]":
    return set(re.findall(r"[0-9A-Za-z][0-9A-Za-z.]*[0-9A-Za-z]|[0-9A-Za-z]", text))


def test_asked_and_file_questions_render_today_s_file_and_hold_nothing_unpublished(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Asked questions, a question about the file and held columns, at the table floor (plan P4-D441).

    Each file rendered from the result's records is the file the code
    before this lane wrote (its digest above). HIPAA FIRST: no record and
    no carried entry holds a value of the table the description does not
    publish -- the held patient key and ZIP codes publish none, so none
    of theirs stands in a record at all -- and the held columns are
    carried as made up.
    """
    held = _profiled_shape(tmp_path / "held", _held_table(battery.TABLE_ROWS), monkeypatch)
    dated = _profiled_shape(tmp_path / "filequestion", _day_or_month_table(battery.TABLE_ROWS), monkeypatch)
    for key, result in (("held", held), ("filequestion", dated)):
        assert result.verdict == "no-miss", (key, result.refusal)
        assert hashlib.sha256(_rendered_questions(result, _kept(result), "t.csv")).hexdigest() == _TODAY_S_FILES[key], key
    sections = {one.section for one in held.questions}
    assert results.SECTION_ASKED in sections, held.questions
    # Each tally as the records count it, written literally (skeptic 1's
    # item 3): the dates' one question is about the file.
    assert held.tally == _profile_tally(2, 0, 1, 0, 4), [(one.section, one.column) for one in held.questions]
    assert dated.tally == _profile_tally(1, 0, 0, 0, 2), [(one.section, one.column) for one in dated.questions]
    assert {one.section for one in dated.questions} >= {results.SECTION_ABOUT_FILE}, dated.questions
    cells = [line.split(",") for line in _held_table(battery.TABLE_ROWS).split("\n")[1:] if line]
    described = (tmp_path / "held" / "t-profile.json").read_text(encoding="utf-8")
    published = _tokens(described)
    words = [word for record in held.questions for word in _record_words(record)]
    words += [entry.words for entry in held.carried] + [part for entry in held.carried for part in entry.subject]
    found = set()
    for word in words:
        found |= _tokens(word)
    for place, name in ((0, "patient_key"), (1, "zip")):
        real = {row[place] for row in cells}
        assert not real & published, name
        assert not real & found, name
        assert ((name,), "not-carried", "made-up") in [(one.subject, one.kind, one.reason) for one in held.carried], name
    ages = {row[2] for row in cells}
    assert not (ages & found) - published


_INVENTED_LEAD = "  twin has to invent what it writes --"


def _summary_invented(text: str) -> "list[str]":
    """The columns the summary says a twin makes up whole, read from its words (the test's own reading)."""
    lines = text.split("\n")
    if _INVENTED_LEAD not in lines:
        return []
    named = lines[lines.index(_INVENTED_LEAD) + 1].strip()
    return [name for name in named.split(", ") if name]


def test_the_summary_s_made_up_columns_are_the_carried_ones(ran: Battery) -> None:
    """On every profile case that wrote one, the summary names as made up exactly the carried `made-up` columns (plan P4-D441).

    The summary is rendered from the description as before (its list by
    role and by labels held back, `carried`'s by cells, A-P4-2); on the
    battery the two agree, so a result read in place of the page says
    what the page says.
    """
    seen = 0
    for key, run in ran.runs.items():
        result = run.result
        if result.command != results.PROFILE or results.FILE_SUMMARY not in run.kept:
            continue
        text = run.kept[results.FILE_SUMMARY].decode("utf-8")
        carried = [one.subject[0] for one in result.carried if one.reason == results.REASON_MADE_UP]
        assert _summary_invented(text) == carried, key
        seen = seen + 1
    assert seen >= 5, seen


# THE PROMPT, THE HELD SECTION AND THE FILE'S ORDER, AT THE LIBRARY'S SIZE
# (lane S5b's repair 1: skeptic 1's items 2 to 4 and Codex's items 1 to 3).
# Each table is 2,000 rows with the table floor set aside, as the
# joined-ranking case sets it, and every shape asks what it asks at the
# floor's size (measured: planning-notes/work-2026-10/wave6/S5b/repair1/).
_LIBRARY_ROWS = 2000


def _library_table(kind: str) -> str:
    """One of five invented tables of 2,000 rows (lane S5b's repairs 1 and 2).

    `stamp`: six-figure stamps `yymmdd`, asked column by column (the
    fixed-width question); `day`: `2024-001` to `2024-366`, which the
    two-numbers question and the days-of-the-year question both reach;
    `two`: the days beside the stamps, so one prompt puts two questions;
    `held`: a person beside day counts written `42.345`, declared
    `excel-1900` and held (plan P4-D406); `ordered`: dates whose day and
    month are each at most 12 (the question about the file, plan P4-D381)
    beside the stamps and a weight of one decimal (the checklist).
    """
    stream = random.Random(5)
    found: "list[str]" = []
    if kind == "stamp":
        found = ["stamp,ward"]
        for index in range(_LIBRARY_ROWS):
            found += [
                f"{stream.randint(20, 24):02d}{stream.randint(1, 12):02d}{stream.randint(1, 28):02d},"
                f"{battery.WARDS[index % 4]}"
            ]
    elif kind == "day":
        found = ["day,ward"] + [f"2024-{1 + index % 366:03d},{battery.WARDS[index % 4]}" for index in range(_LIBRARY_ROWS)]
    elif kind == "two":
        found = ["day,stamp,ward"]
        for index in range(_LIBRARY_ROWS):
            found += [
                f"2024-{1 + index % 366:03d},"
                f"{stream.randint(20, 24):02d}{stream.randint(1, 12):02d}{stream.randint(1, 28):02d},"
                f"{battery.WARDS[index % 4]}"
            ]
    elif kind == "held":
        found = ["person,visit,ward"]
        for index in range(_LIBRARY_ROWS):
            found += [
                f"P{1000 + index % 500},{stream.randint(40, 45)}.{stream.randint(0, 999):03d},{battery.WARDS[index % 4]}"
            ]
    else:
        found = ["visit,stamp,weight,ward"]
        for index in range(_LIBRARY_ROWS):
            weight = 50.0 + 18.0 * (stream.random() + stream.random() + stream.random())
            found += [
                f"{stream.randint(1, 12):02d}/{stream.randint(1, 12):02d}/2024,"
                f"{stream.randint(20, 24):02d}{stream.randint(1, 12):02d}{stream.randint(1, 28):02d},"
                f"{weight:.1f},{battery.WARDS[index % 4]}"
            ]
    return "\n".join(found) + "\n"


def _library_profile(
    folder: pathlib.Path,
    kind: str,
    monkeypatch: pytest.MonkeyPatch,
    *options: str,
    ask: "list[str | None] | None" = None,
) -> results.Result:
    folder.mkdir()
    (folder / "t.csv").write_text(_library_table(kind), encoding="utf-8", newline="\n")
    monkeypatch.chdir(folder)
    result = cli.run(["profile", "t.csv", *options], ask=ask, small_tables_refused=False)
    assert result.verdict == "no-miss", (kind, result.refusal)
    return result


def _profile_tally(asked: int, put: int, checklist: int, held: int, columns: int) -> "tuple[tuple[str, int], ...]":
    return (
        ("columns", columns),
        ("questions-asked", asked),
        ("questions-put", put),
        ("checklist", checklist),
        ("held", held),
    )


def test_a_question_put_at_a_prompt_is_said_put_and_counted(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`put` and the tally's `questions-put` follow the prompt, question by question (plan P4-D441).

    Skeptic 1's item 2: kept at the prompt with Enter, the stamps' one
    question is said put and counted; written down with nobody to ask, it
    is neither. Codex's item 1: on `2024-001` the prompt puts the
    two-numbers question alone, and the days-of-the-year question the
    final records also hold on that column is not said put. Codex's item
    2: answered at the prompt, the question leaves the file and stays
    counted as put, since it was. Repair 2: one prompt that puts two
    questions counts two, not one.
    """
    quiet = _library_profile(tmp_path / "quiet", "stamp", monkeypatch)
    kept = _library_profile(tmp_path / "kept", "stamp", monkeypatch, ask=["", "", ""])
    for result, put in ((quiet, False), (kept, True)):
        assert [(one.section, one.column, one.reason, one.put) for one in result.questions] == [
            (results.SECTION_ASKED, "stamp", "fixed-width", put)
        ]
        assert result.tally == _profile_tally(1, 1 if put else 0, 0, 0, 2)
    answered = _library_profile(tmp_path / "answered", "stamp", monkeypatch, ask=["2"])
    assert answered.questions == ()
    assert answered.tally == _profile_tally(0, 1, 0, 0, 2)
    days = _library_profile(tmp_path / "days", "day", monkeypatch, ask=["", "", ""])
    assert [(one.column, one.reason, one.put) for one in days.questions] == [
        ("day", "two-numbers", True),
        ("day", "figures-that-may-be-days-of-the-year", False),
    ]
    assert days.tally == _profile_tally(2, 1, 0, 0, 2)
    two = _library_profile(tmp_path / "two", "two", monkeypatch, ask=["", "", "", ""])
    assert [(one.column, one.reason, one.put) for one in two.questions] == [
        ("day", "two-numbers", True),
        ("stamp", "fixed-width", True),
        ("day", "figures-that-may-be-days-of-the-year", False),
    ]
    assert two.tally == _profile_tally(3, 2, 0, 0, 3)


def test_the_held_section_s_record_and_the_tally_that_counts_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A column declared as counted dates that did not read so: one `held` record, counted (skeptic 1's item 3; plan P4-D406)."""
    held = _library_profile(
        tmp_path / "held", "held", monkeypatch, "--identifier", "person", "--date-count", "visit", "excel-1900"
    )
    assert held.questions == (
        results.Asked(
            results.SECTION_HELD,
            1,
            "visit",
            "",
            asking.BECAUSE_HELD_COUNTED_DATES,
            "you said this column writes its dates as counts (excel-1900), and its cells did not read as such dates",
            "",
            subject="visit",
        ),
    )
    assert held.tally == _profile_tally(0, 0, 0, 1, 3)


def test_records_stand_in_the_file_s_order_and_a_file_question_names_no_column(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The question about the file, then the columns asked, then the checklist (skeptic 1's item 4; Codex's item 3).

    The question about the file names no column: its record's `column` is
    empty and its `subject` is what the file writes under `column`, so
    the file rendered from the records is the file written.
    """
    ordered = _library_profile(tmp_path / "ordered", "ordered", monkeypatch)
    assert [(one.section, one.order, one.column, one.subject) for one in ordered.questions] == [
        (results.SECTION_ABOUT_FILE, 1, "", "the order of the day and the month in your dates"),
        (results.SECTION_ASKED, 1, "stamp", "stamp"),
        (results.SECTION_CHECKLIST, 1, "weight", "weight"),
    ]
    assert ordered.tally == _profile_tally(2, 0, 1, 0, 4)
    written = (tmp_path / "ordered" / "t-questions.json").read_bytes()
    assert _rendered_questions(ordered, _kept(ordered), "t.csv") == written
    entries = _file_entries(json.loads(written.decode("utf-8")))
    assert [(section, entry["column"]) for section, entry in entries] == [
        (one.section, one.subject) for one in ordered.questions
    ]
