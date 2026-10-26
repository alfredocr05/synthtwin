"""Stage 5's gate: results become data (plan P4-D395; lane S5a, plan P4-D437).

STATE's row 5: "a caller distinguishes a good run from a bad one without
reading prose; reports byte-identical". Two KPIs measure it over the
golden battery of `tests/stage5_battery.py`, and this file is their gate:

- `K-S5-01`: each case's result, read through `cli.run`, says what the
  case's row wrote for it when the case was written -- its class, the
  misses a damage must break with their tiers, a refusal's step, the
  warnings, the floor, the next command, the carried entries -- and each
  miss's text and rank values equal its producer's, checked one by one
  against values found without the result's code. A checker handed a
  correct result corrupted one field at a time must find it unmet.
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
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import types
import typing

import pytest

import dispositions
import stage5_battery as battery
import stage5_goldens as goldens
from synthtwin import cli, errors, generation, rendering, results, validation, writing

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
            )
    return Battery(root, records, runs)


# -- K-S5-01: the checker, and the battery read through it -------------


def _golden_exit(key: str) -> "int | None":
    for record in goldens.RECORDS:
        if record[0] == key and record[1] == "exit":
            return typing.cast(int, record[2])
    return None


def _positions(folder: pathlib.Path, argv: "tuple[str, ...]") -> "dict[str, int]":
    """Each column's position, read from the description the case names (the test's own reading)."""
    for word in argv:
        if word.endswith("-profile.json") and (folder / word).exists():
            document = json.loads((folder / word).read_text(encoding="utf-8"))
            return {block["name"]: block["position"] for block in document["columns"]}
    return {}


def _expected_tier(
    expect: battery.Expect, miss: results.Miss, judged: str
) -> "str | None":
    for column, fact, subcheck, tier in expect.breaks:
        if (miss.column, miss.fact, miss.subcheck) == (column, fact, subcheck):
            return tier
    if judged == results.JUDGED_WINDOW:
        return results.TIER_WINDOW
    return results._ranked(miss.fact, miss.subcheck)


def unmet(run: Ran, result: results.Result) -> "list[str]":
    """Why ``result`` does not meet the case's row, under `K-S5-01` (a) to (i); empty when met.

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
    if run.outcome is not None and result.verdict != "refused":
        if len(misses) != run.outcome.census.missed:
            found += [f"(d) {len(misses)} misses, the census counts {run.outcome.census.missed}"]
    elif run.twin is not None and result.verdict != "refused":
        if len(misses) != len(run.twin.deviations):
            found += [f"(d) {len(misses)} misses, the twin {len(run.twin.deviations)} deviations"]
    elif misses and result.verdict != "refused":
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
    # (h) carried: the entries not carried as the row writes them, and an
    # approximate entry for each approximation the producer made
    if expect.carried is not None:
        not_carried = tuple(
            (one.kind, one.reason, one.verdict)
            for one in result.carried
            if one.kind == results.CLASS_NOT_CARRIED
        )
        if not_carried != expect.carried:
            found += [f"(h) not carried {not_carried}, the row writes {expect.carried}"]
    approximate = [one for one in result.carried if one.kind == results.CLASS_APPROXIMATE]
    if run.twin is not None and result.verdict != "refused":
        wanted = [
            (one.column, one.fact, one.published, one.achieved, one.lowest, one.highest, one.inside, one.covers_published)
            for one in run.twin.approximations
        ]
        held = [
            (
                one.subject[0],
                one.fact,
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
        wanted_checks = [check for check in run.outcome.checks if check.judged == validation.JUDGED_WINDOW]
        if [(one.fact, one.verdict) for one in approximate] != [
            (check.fact, check.verdict) for check in wanted_checks
        ]:
            found += ["(h) the approximate entries are not the checks judged against a window"]
        for one, check in zip(approximate, wanted_checks):
            measure = one.measures[0]
            inside = None if check.verdict == validation.WITHHELD else check.verdict != validation.MISSED
            if (measure.published, measure.achieved, measure.inside) != (check.published, check.achieved, inside):
                found += [f"(i) a carried measure of {check.fact} is not its check's"]
    # (i) each miss's text and rank values, one by one
    positions = _positions(run.folder, case.argv)
    for miss in misses:
        producer: typing.Any = None
        if run.outcome is not None:
            if 0 <= miss.arrival < len(run.outcome.checks):
                producer = run.outcome.checks[miss.arrival]
                if producer.verdict != validation.MISSED:
                    producer = None
            if producer is not None:
                text = (producer.published, producer.achieved, producer.note)
        elif run.twin is not None:
            if 0 <= miss.arrival < len(run.twin.deviations):
                producer = run.twin.deviations[miss.arrival]
                text = (producer.published, producer.achieved, (producer.note,) if producer.note else ())
        if producer is None:
            found += [f"(i) arrival {miss.arrival} names no missed check or deviation"]
            continue
        if producer.column != miss.column:
            found += [f"(i) arrival {miss.arrival} is another column's"]
        if (miss.published, miss.achieved, miss.note) != text:
            found += [f"(i) {miss.fact}'s text is not its producer's"]
        if miss.shown != bool(producer.achieved):
            found += [f"(i) {miss.fact} is shown where the producer keeps its measured side back, or the reverse"]
        wanted_place = positions.get(miss.column, 0) if miss.column else 0
        if miss.place != wanted_place:
            found += [f"(i) {miss.fact} at place {miss.place}, the description puts it at {wanted_place}"]
        if _expected_tier(expect, miss, producer.judged) != miss.tier:
            found += [f"(i) {miss.fact} [{miss.subcheck}] at tier {miss.tier}"]
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
    return found


def test_k_s5_01_a_corrupted_result_is_never_met(ran: Battery) -> None:
    """Each field corrupted alone leaves its case unmet, so the checker can fail."""
    for name, run, corrupted in _corruptions(ran):
        assert unmet(run, run.result) == [], name
        assert unmet(run, corrupted), f"the checker met a result with {name}"


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


def test_every_window_check_is_marked_where_it_is_made() -> None:
    """`_within`, `_within_clock`, `_within_instant` and `_tail_window_check` mark every check."""
    for name in ("_within", "_within_clock", "_within_instant", "_tail_window_check"):
        assert _returns_marked(name) == [], name
    # `_lesser_or_held`: the exact bar first (unmarked), then the corner's window.
    assert len(_returns_marked("_lesser_or_held")) == 3


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


def test_the_long_options_are_the_parser_s_in_its_order() -> None:
    """`cli._LONG_OPTIONS` is the parser's own list, so an ambiguous word names argparse's matches."""
    import argparse

    seen: "list[str]" = []
    original = argparse.ArgumentParser.parse_known_args

    def caught(self: argparse.ArgumentParser, *_given: object, **_named: object) -> object:
        seen.extend([option for option in self._option_string_actions if option.startswith("--")])
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
