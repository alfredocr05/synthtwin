"""The KPI ledger's honesty guard.

A ledger that names a test nobody runs is a board that shows green over
nothing. So every rule `tests/kpi/ledger.json` depends on is checked
here, in the ordinary suite, by `kpi_rules.integrity_problems` -- the same
function `tools/measurements/kpi_run.py` refuses to run without:

(a) every PINNED node exists: the named file is parsed and the function
    found, or the check names the node that is gone;
(b) every KPI measured by a test of its own has exactly one
    `test_k_<id>` in `tests/test_kpi_ledger.py`, and that file has no
    `test_k_` function the ledger does not name;
(c) every driver the ledger names exists under `tools/measurements/` and
    has a row in that folder's README;
(d) ids are unique and well formed, and every closed field holds one of
    its members;
(e) every phase or stage and every category has a headline, and the
    board holds 20 to 30 of them;
(f) every entry with pinned nodes in the fast tier names how many of
    their cases must be collected AND RUN (`nodes_min_collected`), so a
    parametrize list that shrinks is seen.

Whether a pinned node is COLLECTED, and not merely defined, is what the
runner checks when it runs: it exits 2 on a node pytest did not collect,
on fewer cases run than the entry's floor, and on a pinned case that was
SKIPPED -- a skip measures nothing, so a headline measured only by
pinned nodes could otherwise stay green over a regression. The runner's
judging is a pure function (`kpi_run.judge_rows`), and the tests at the
bottom feed it made-up pytest outcomes to prove each of those can fail,
beside the mutation tests of the ledger checks.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

import pytest

import kpi_rules

LEDGER = kpi_rules.load_ledger()
ENTRIES = kpi_rules.entries_by_id(LEDGER)


def _runner() -> object:
    """tools/measurements/kpi_run.py loaded as a module (it runs nothing on import)."""
    spec = importlib.util.spec_from_file_location(
        "kpi_run_under_test", kpi_rules.MEASUREMENTS / "kpi_run.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = _runner()


def test_the_ledger_passes_its_own_integrity_check() -> None:
    problems = kpi_rules.integrity_problems(LEDGER)
    assert problems == [], "\n".join(problems)


def test_the_ledger_is_the_size_and_shape_it_was_built_to() -> None:
    """The board's counts, stated where a change to them is seen."""
    entries = LEDGER["entries"]
    assert len(entries) >= 143, len(entries)
    headlines = [e["id"] for e in entries if e["headline"]]
    assert kpi_rules.HEADLINES_AT_LEAST <= len(headlines) <= kpi_rules.HEADLINES_AT_MOST
    for entry in entries:
        if entry["status"] == "OPEN":
            assert entry.get("target") is not None, f"{entry['id']}: an OPEN entry names its target"
        assert entry["value_at"]["commit"], entry["id"]


def test_every_document_binding_of_the_oracle_is_pinned_by_the_ledger() -> None:
    """Round-2 ledger item 3: coverage read off the binding registry, not a case count.

    K-P2-01 promises every frozen case and K-2B-39 each document
    binding, and neither pinned `written_form_classes`,
    `withheld_line_marks` or `delimiter_reading`. MEASURED at 05e7d89:
    `dialect.cell_class("NaT")` moved from absent to text left all 103
    pinned cases of those two entries green -- 98 column cases, four
    workbook cases, the case-count checks and the three document pins --
    while the unpinned `written_form_classes` binding failed at once.
    The set the ledger must pin is `DOCUMENT_BINDINGS`, so a transform
    added with no pin is red here rather than silently uncovered.
    """
    import test_generation_reference as reference

    pinned = {node for entry in LEDGER["entries"] for node in entry.get("nodes", [])}
    unpinned = sorted(
        f"{case} -> {node}"
        for case, node in reference.DOCUMENT_BINDINGS.items()
        if node not in pinned
    )
    assert unpinned == [], (
        "these whole-document transforms of the oracle are bound by a test that no "
        "ledger entry pins, so the binding can be withdrawn with every KPI green: "
        + "; ".join(unpinned)
    )


def test_every_entry_s_expected_value_is_judged_true_of_itself() -> None:
    """A bound that its own recorded value breaks is a ledger that lies about today.

    Every entry whose recorded value is a keyed number is judged against
    its own rule; a GREEN entry's recorded value may be RED only where the
    ledger says, in `evidence`, that the value is red on its base commit.
    """
    for entry in LEDGER["entries"]:
        value = entry["value_at"]["value"]
        if not isinstance(value, dict):
            continue
        # Seconds are judged too: every recorded value was taken on the
        # reference machine, so one that breaks its seconds rule -- even
        # under load -- must say RED in its evidence, not pass unseen.
        verdict = kpi_rules.judge(entry, value, seconds_count=True, partial=True)
        if verdict.is_drop:
            assert "RED" in entry.get("evidence", ""), (
                f"{entry['id']}: its recorded value {value!r} fails its own rule "
                f"({verdict.message}) and the ledger does not say it is red"
            )


# -- the fields the ledger states ABOUT its own numbers ------------------
#
# Repair pass of the round-2 ledger, points 2 and 4 of it: three fields were
# written in this pass and read by nothing -- `report_only`,
# `coverage_elsewhere`, and the `measurement_note` sentence that names
# which entries were re-measured off the base commit. A field no code
# reads can go on saying something untrue with every KPI green, and one
# of them already did: K-2B-47 carried six keys its stamped commit's
# driver could not emit, while the note written in the same commit said
# that entry had been re-stamped.


def _report_only_bounds() -> "list[tuple[str, str, object, object]]":
    """(entry id, key, its bound, its recorded value) for every report-only key."""
    out = []
    for entry in LEDGER["entries"]:
        for key in entry.get("report_only", []):
            out.append(
                (
                    entry["id"],
                    key,
                    entry["expected"].get(key, _ABSENT),
                    entry["value_at"]["value"].get(key, _ABSENT),
                )
            )
    return out


_ABSENT = object()


def test_a_report_only_key_is_a_bound_its_own_shape_already_saturates() -> None:
    """Finding 4: `report_only` is a claim about a number, so it is checked like one.

    An entry says a key is REPORT-ONLY when its shape cannot produce a
    larger value, so the bound records a ceiling rather than leaving
    room to fall: `read_floor_unchecked` is `int(a != b)` against at most
    1, and `fortran_d_cells_respelled` is 1,200 of 1,200 cells. Both are
    therefore named in `expected` AND recorded AT their bound. A key
    whose bound leaves slack can turn red and is a measured bound, not a
    report-only indicator, and saying otherwise in the ledger is what
    this fails on.
    """
    listed = _report_only_bounds()
    assert listed, "no entry declares a report-only key; this guard has nothing to hold"
    wrong = []
    for entry_id, key, bound, recorded in listed:
        if bound is _ABSENT:
            wrong.append(f"{entry_id}: {key} is declared report-only and its rule does not bound it")
        elif recorded is _ABSENT:
            wrong.append(f"{entry_id}: {key} is declared report-only and no value is recorded for it")
        elif recorded != bound:
            wrong.append(
                f"{entry_id}: {key} is declared report-only but its bound {bound!r} leaves room "
                f"above the recorded {recorded!r}, so it CAN turn red and is a measured bound"
            )
    assert wrong == [], "; ".join(wrong)


def test_a_coverage_elsewhere_field_names_a_live_entry_and_a_key_it_measures() -> None:
    """Finding 4: an entry that hands coverage to another names one that carries it.

    K-2B-47 says the two unmirrored generator passes are counted by
    `K-P4-23 (uncovered)`. If that entry were deleted, renamed, or
    stopped measuring `uncovered`, the sentence would go on standing
    while nothing measured the thing at all.
    """
    named = [
        (entry["id"], what, where)
        for entry in LEDGER["entries"]
        for what, where in entry.get("coverage_elsewhere", {}).items()
    ]
    assert named, "no entry hands coverage elsewhere; this guard has nothing to hold"
    wrong = []
    for entry_id, what, where in named:
        holder = sorted(other for other in ENTRIES if other in where)
        if not holder:
            wrong.append(f"{entry_id}: {where!r} for {what!r} names no entry of this ledger")
            continue
        for other in holder:
            keys = [key for key in ENTRIES[other]["expected"] if key in where]
            if not keys:
                wrong.append(
                    f"{entry_id}: {where!r} names {other}, which measures "
                    f"{sorted(ENTRIES[other]['expected'])} and not the key named there"
                )
    assert wrong == [], "; ".join(wrong)


def _ids_named_in(sentence: str) -> "set[str]":
    """The entry ids this ledger's prose names."""
    return {entry_id for entry_id in ENTRIES if entry_id in sentence}


def test_the_measurement_note_names_exactly_the_entries_measured_off_the_base_commit() -> None:
    """Finding 2: a value_at re-stamped, or not re-stamped, is what the note says it is.

    Every value_at was taken on `base_commit` except the ones a later
    pass re-measured, and the note names those. MEASURED on the tree of
    the round-2 ledger pass: the note named four entries and only three
    carried another commit -- K-2B-47 still stamped caf3079 while its
    value had gained six keys (fortran_d_*, read_floor_facts_differing)
    that caf3079's driver could not emit. Nothing read the note, so
    nothing said so.
    """
    base = LEDGER["base_commit"]
    off_base = {
        entry["id"]: entry["value_at"]["commit"]
        for entry in LEDGER["entries"]
        if entry["value_at"]["commit"] != base
    }
    note = LEDGER["measurement_note"]
    assert base in note, "the note does not name the commit every other value was taken on"
    named = _ids_named_in(note)
    assert named == set(off_base), (
        "the measurement note names "
        + (", ".join(sorted(named)) or "no entry")
        + " and the entries whose value_at is not "
        + base
        + " are "
        + (", ".join(sorted(off_base)) or "none")
    )
    for entry_id, commit in sorted(off_base.items()):
        assert commit in note, f"{entry_id} was measured on {commit}, which the note does not name"
        # A re-measured entry says which driver or run took it, so a
        # value carrying keys an older driver could not emit is visible.
        assert ENTRIES[entry_id]["value_at"].get("measured_by"), (
            f"{entry_id}: re-measured off {base} and does not say what measured it"
        )


def test_a_re_measured_entry_records_every_key_its_rule_bounds() -> None:
    """Finding 2, the other half: a stamp is only as good as the value under it.

    A value_at that has gained keys since it was stamped is a value
    taken by a driver that did not exist at that commit. Every key the
    rule bounds must be one the recorded value carries, so a rule
    extended without a re-measurement is red here.
    """
    missing = []
    for entry in LEDGER["entries"]:
        expected = entry["expected"]
        value = entry["value_at"]["value"]
        if not isinstance(expected, dict) or not isinstance(value, dict):
            continue
        gone = sorted(k for k in expected if k not in value and k != "pinned_nodes_failing")
        if gone:
            missing.append(f"{entry['id']}: {', '.join(gone)}")
    assert missing == [], (
        "these entries bound a key their recorded value does not carry, so the rule was "
        "extended and the value was not re-measured: " + "; ".join(missing)
    )



def test_a_carried_shape_measured_over_fewer_runs_is_a_drop() -> None:
    """Finding 3: a ceiling held over less evidence is not the same ceiling.

    K-2B-47's Fortran D shape is 400 cells over seeds 4, 0 and 1.
    MEASURED: cutting the driver's loop to one seed leaves
    `fortran_d_missed_checks` at 0 (inside at most 0) and
    `fortran_d_cells_respelled` at 400 (inside at most 1,200), so the
    entry stayed green over a third of the runs and two thirds of the
    chances to see a miss vanished -- K-2B-50 and K-2B-51 bound their
    run counts and this one did not. The run and cell counts are
    at_least bounds now, so the same cut is a drop.
    """
    entry = ENTRIES["K-2B-47"]
    recorded = dict(entry["value_at"]["value"])
    assert not kpi_rules.judge(entry, recorded).is_drop, recorded
    one_seed = dict(
        recorded,
        fortran_d_runs=1,
        fortran_d_cells_respelled=400,
        fortran_d_missed_checks=0,
    )
    verdict = kpi_rules.judge(entry, one_seed)
    assert verdict.is_drop and "fortran_d_runs" in verdict.message, verdict
    shorter = dict(recorded, fortran_d_cells=399)
    verdict = kpi_rules.judge(entry, shorter)
    assert verdict.is_drop and "fortran_d_cells" in verdict.message, verdict


def test_every_entry_with_pinned_nodes_bounds_how_many_may_fail() -> None:
    """Repair pass: a pin the rule does not bound is decoration.

    `kpi_run.judge_rows` merges `pinned_nodes_failing` into an entry's
    value, and `kpi_rules.judge` judges only the keys the rule names --
    so an entry that pins tests and does not bound that key reads held
    while a pinned test fails. MEASURED on the tree of the round-2
    ledger pass: 127 entries carried pinned nodes, 124 bound them, and
    the three that did not were exactly the three that pass touched
    (K-2B-47 and the two new ceilings K-2B-50 and K-2B-51), whose pins
    were therefore measuring nothing.
    """
    loose = [
        entry["id"]
        for entry in LEDGER["entries"]
        if entry.get("nodes")
        and isinstance(entry["expected"], dict)
        and "pinned_nodes_failing" not in entry["expected"]
    ]
    assert loose == [], (
        "these entries pin tests whose failure their rule does not judge: " + ", ".join(loose)
    )
    for entry_id in ("K-2B-47", "K-2B-50", "K-2B-51"):
        entry = ENTRIES[entry_id]
        recorded = dict(entry["value_at"]["value"])
        assert not kpi_rules.judge(entry, recorded).is_drop, entry_id
        verdict = kpi_rules.judge(entry, dict(recorded, pinned_nodes_failing=1))
        assert verdict.is_drop and "pinned_nodes_failing" in verdict.message, (entry_id, verdict)


# -- the checks can fail -------------------------------------------------


def _problems_after(change: "object") -> "list[str]":
    ledger = copy.deepcopy(LEDGER)
    change(ledger)  # type: ignore[operator]
    return kpi_rules.integrity_problems(ledger)


def _first_with(field: str, ledger: "dict") -> "dict":
    return next(e for e in ledger["entries"] if e.get(field))


def test_a_renamed_pinned_node_is_named() -> None:
    """(a) can fail: one node renamed in a copy of the ledger is reported."""

    def rename(ledger: "dict") -> None:
        entry = _first_with("nodes", ledger)
        entry["nodes"][0] = entry["nodes"][0] + "_renamed_away"

    problems = _problems_after(rename)
    assert any("pinned node" in p and "_renamed_away" in p for p in problems), problems


def test_a_pinned_file_that_is_gone_is_named() -> None:
    def move(ledger: "dict") -> None:
        entry = _first_with("nodes", ledger)
        entry["nodes"][0] = "tests/test_no_such_file.py::test_anything"

    assert any("does not exist" in p for p in _problems_after(move))


def test_a_kpi_test_the_ledger_does_not_name_is_named() -> None:
    """(b) can fail both ways: a test with no entry, and an entry with no test."""

    def orphan(ledger: "dict") -> None:
        entry = _first_with("test", ledger)
        entry["test"] = None
        entry["nodes"] = entry.get("nodes") or ["tests/test_socket_guard.py::test_socket_creation_is_blocked"]

    problems = _problems_after(orphan)
    assert any("no ledger entry names" in p for p in problems), problems

    def missing(ledger: "dict") -> None:
        entry = _first_with("test", ledger)
        entry["id"] = entry["id"][:-2] + "99"
        entry["test"] = "tests/test_kpi_ledger.py::" + kpi_rules.owned_test_name(entry["id"])

    problems = _problems_after(missing)
    assert any("not defined" in p for p in problems), problems


def test_a_driver_with_no_readme_row_or_no_file_is_named() -> None:
    """(c) can fail."""

    def gone(ledger: "dict") -> None:
        _first_with("driver", ledger)["driver"] = "tools/measurements/kpi_not_there.py --kpi"

    assert any("does not exist" in p for p in _problems_after(gone))

    def outside(ledger: "dict") -> None:
        _first_with("driver", ledger)["driver"] = "tools/reference/make_generation_reference_vectors.py"

    assert any("not under tools/measurements" in p for p in _problems_after(outside))


def test_ids_and_closed_fields_are_held() -> None:
    """(d) can fail: a duplicate id, a malformed id and an unknown category."""

    def duplicate(ledger: "dict") -> None:
        ledger["entries"][1]["id"] = ledger["entries"][0]["id"]

    assert any("more than once" in p for p in _problems_after(duplicate))

    def malformed(ledger: "dict") -> None:
        ledger["entries"][0]["id"] = "KPI-7"

    assert any("not K-<phase or stage>-nn" in p for p in _problems_after(malformed))

    def category(ledger: "dict") -> None:
        ledger["entries"][0]["category"] = "MISC"

    assert any("category 'MISC'" in p for p in _problems_after(category))


def test_the_headline_board_is_held() -> None:
    """(e) can fail: too many headlines, and a phase left with none."""

    def everything(ledger: "dict") -> None:
        for entry in ledger["entries"]:
            entry["headline"] = True

    assert any("headlines: the board holds" in p for p in _problems_after(everything))

    def lose_phase_zero(ledger: "dict") -> None:
        for entry in ledger["entries"]:
            if entry["id"].startswith("K-P0-"):
                entry["headline"] = False

    assert any("phase or stage P0 has no headline" in p for p in _problems_after(lose_phase_zero))


def test_the_rules_judge_a_value_the_way_the_ledger_states() -> None:
    """The verdict words, on a made-up entry of each status."""
    entry = {"rule_kind": "at_most", "expected": {"n": 4}, "status": "GREEN"}
    assert kpi_rules.judge(entry, {"n": 4}).word == kpi_rules.PASS
    assert kpi_rules.judge(entry, {"n": 5}).word == kpi_rules.FAIL
    assert kpi_rules.judge(entry, {}).word == kpi_rules.FAIL
    assert kpi_rules.judge(entry, {}, partial=True).word == kpi_rules.PASS
    held = dict(entry, status="OPEN", target={"n": 0})
    assert kpi_rules.judge(held, {"n": 3}).word == kpi_rules.OPEN_HELD
    assert kpi_rules.judge(held, {"n": 5}).word == kpi_rules.OPEN_WORSE
    assert kpi_rules.judge(held, {"n": 0}).word == kpi_rules.IMPROVED
    accepted = dict(entry, status="ACCEPTED_LIMIT")
    assert kpi_rules.judge(accepted, {"n": 5}).word == kpi_rules.ACCEPTED_WORSE
    timed = {"rule_kind": "seconds_below", "expected": {"s": 1.0}, "status": "GREEN"}
    assert kpi_rules.judge(timed, {"s": 9.0}, seconds_count=True).word == kpi_rules.FAIL
    assert kpi_rules.judge(timed, {"s": 9.0}, seconds_count=False).word == kpi_rules.PASS
    drifting = dict(entry, drift={"rule_kind": "at_least", "expected": {"exact": 2}})
    assert kpi_rules.judge(drifting, {"n": 1, "exact": 1}).word == kpi_rules.PASS_DRIFT


def test_the_ledger_file_is_canonical_json() -> None:
    """One key per member, UTF-8, and a trailing newline, so a diff shows one change."""
    text = kpi_rules.LEDGER_PATH.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert json.loads(text) == LEDGER
    assert pathlib.Path(kpi_rules.LEDGER_PATH).stat().st_size < 250_000


def test_a_fast_pinned_entry_with_no_collection_floor_is_named() -> None:
    """(f) can fail: an entry that drops its floor, or allows a skip of a node it does not pin."""

    def drop(ledger: "dict") -> None:
        for entry in ledger["entries"]:
            if entry["id"] == "K-P0-01":
                del entry["nodes_min_collected"]

    assert any("K-P0-01: nodes_min_collected" in p for p in _problems_after(drop))

    def stray(ledger: "dict") -> None:
        for entry in ledger["entries"]:
            if entry["id"] == "K-P0-01":
                entry["allowed_skips"] = ["tests/test_socket_guard.py::test_not_pinned_here"]

    assert any("allowed skip" in p for p in _problems_after(stray))


# -- the runner's judging can fail (kpi_run.judge_rows, fed made-up outcomes) --


def _cases(entry: "dict", outcome: str, per_node: int = 1) -> "dict[str, list[dict]]":
    return {node: [{"outcome": outcome, "kpi": None}] * per_node for node in entry["nodes"]}


def _row(entry: "dict", cases: "dict[str, list[dict]]") -> "dict":
    rows = RUNNER.judge_rows(  # type: ignore[attr-defined]
        [entry], LEDGER, False, cases, {}, False
    )
    assert len(rows) == 1
    return rows[0]


def test_a_skipped_pinned_case_never_reads_as_a_pass() -> None:
    """The skeptic's reproduction: K-P0-01's only pinned test skipped over a real regression.

    K-P0-01 is a headline measured only by pinned nodes. With every case
    passing it is PASS; with its cases SKIPPED it must be an integrity
    fault (exit 2), never PASS -- and a skip the entry allows by name is
    left out of the count, which still has to reach the entry's floor.
    """
    entry = ENTRIES["K-P0-01"]
    floor = entry["nodes_min_collected"]
    passed = _row(entry, _cases(entry, "passed", floor))
    assert passed["verdict"] == kpi_rules.PASS and passed["pass"]
    skipped = _row(entry, _cases(entry, "skipped", floor))
    assert skipped["verdict"] == "INTEGRITY" and not skipped["pass"], skipped
    assert "SKIPPED" in skipped["message"]
    one_skip = _cases(entry, "passed", floor)
    first = entry["nodes"][0]
    one_skip[first] = one_skip[first] + [{"outcome": "skipped", "kpi": None}]
    assert _row(entry, one_skip)["verdict"] == "INTEGRITY"
    allowed = dict(entry, allowed_skips=[first])
    assert _row(allowed, one_skip)["verdict"] == kpi_rules.PASS
    only_skips = {node: [{"outcome": "skipped", "kpi": None}] for node in entry["nodes"]}
    assert _row(dict(entry, allowed_skips=list(entry["nodes"])), only_skips)["verdict"] == "INTEGRITY"


def test_a_shrinking_parametrize_list_is_an_integrity_fault() -> None:
    """Fewer pinned cases collected and run than the entry's floor: exit 2, never PASS.

    K-S2-01 pins one parametrized node over the stage-2 shapes; the
    same node with one shape fewer is the shrinking list.
    """
    entry = ENTRIES["K-S2-01"]
    floor = entry["nodes_min_collected"]
    assert len(entry["nodes"]) == 1 and floor >= 19
    node = entry["nodes"][0]
    recorded = {"id": "K-S2-01", "value": {"shapes": 19}, "detail": ""}
    full = {node: [{"outcome": "passed", "kpi": None}] * floor,
            entry["test"]: [{"outcome": "passed", "kpi": recorded}]}
    assert _row(entry, full)["verdict"] == kpi_rules.PASS
    shrunk = dict(full, **{node: full[node][1:]})
    row = _row(entry, shrunk)
    assert row["verdict"] == "INTEGRITY" and "fewer than" in row["message"], row


def test_a_kpi_test_that_fails_before_recording_is_a_drop() -> None:
    """A product exception or an assertion before the value is recorded: FAIL (exit 1), not INTEGRITY.

    K-2B-28 stands in as an OPEN entry its own KPI test measures (K-2B-46,
    which stood here, turned GREEN with the g-sentinel repair).
    """
    entry = ENTRIES["K-2B-28"]
    row = _row(entry, {entry["test"]: [{"outcome": "failed", "kpi": None}]})
    assert row["verdict"] == kpi_rules.FAIL and not row["pass"], row
    recorded = {"id": "K-2B-28", "value": entry["value_at"]["value"], "detail": ""}
    row = _row(entry, {entry["test"]: [{"outcome": "failed", "kpi": recorded}]})
    assert row["verdict"] == kpi_rules.FAIL, row
    row = _row(entry, {entry["test"]: [{"outcome": "passed", "kpi": recorded}]})
    assert row["verdict"] == kpi_rules.OPEN_HELD, row


def test_a_driver_that_died_after_printing_its_value_is_a_drop() -> None:
    """The round-2 ledger item 5, reproduced: K-2B-14's record beside exit 1.

    `_run_drivers` printed the driver's exit status and threw it away, so
    a driver that emitted a valid KPI line and then failed an assertion
    produced verdict PASS, pass True, partial False -- the runner green
    over a measurement that never finished. The status is carried beside
    the records now: the same records with exit 0 still PASS, and with
    exit 1 the entry FAILS and names the status.
    """
    entry = ENTRIES["K-2B-14"]
    records = {entry["id"]: [{"id": entry["id"], "value": entry["value_at"]["value"],
                              "detail": ""}]}

    def row(exits: "dict[str, int]") -> "dict":
        rows = RUNNER.judge_rows(  # type: ignore[attr-defined]
            [entry], LEDGER, True, {}, records, True, exits
        )
        return rows[0]

    finished = row({entry["driver"]: 0})
    assert finished["verdict"] == kpi_rules.PASS and finished["pass"], finished
    died = row({entry["driver"]: 1})
    assert died["verdict"] == kpi_rules.FAIL and not died["pass"], died
    assert "exited 1" in died["message"], died
    # A command nobody ran here says nothing about the entry.
    assert row({})["verdict"] == kpi_rules.PASS


def test_the_runner_carries_every_driver_s_exit_status() -> None:
    """`_run_drivers` returns the status beside the records, for two drivers at once."""

    class Done:
        def __init__(self, stdout: str, code: int) -> None:
            self.stdout = stdout
            self.stderr = ""
            self.returncode = code

    answers = {
        "tools/measurements/one.py --kpi": Done(
            'KPI {"id": "K-2B-14", "value": {"a": 1}, "detail": ""}\n', 0),
        "tools/measurements/two.py --kpi": Done(
            'KPI {"id": "K-2B-47", "value": {"b": 2}, "detail": ""}\nboom\n', 1),
    }
    commands = sorted(answers)
    calls: "list[str]" = []

    def fake_run(argv: "list[str]", **_rest: object) -> object:
        command = " ".join(argv[1:])
        calls.append(command)
        return answers[command]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(RUNNER.subprocess, "run", fake_run)  # type: ignore[attr-defined]
        found, exits = RUNNER._run_drivers(commands)  # type: ignore[attr-defined]
    assert calls == commands
    assert sorted(found) == ["K-2B-14", "K-2B-47"]
    assert exits == {commands[0]: 0, commands[1]: 1}


def test_an_open_seconds_target_is_never_improved_where_seconds_are_not_judged() -> None:
    """K-S1-06: its target is in seconds; off the quiet reference machine it can fail, never improve."""
    entry = ENTRIES["K-S1-06"]
    met = {"ratio_4x_rows": 4.0, "seconds_100k_x20": 300.0, "seconds_2m_x50": 1000.0}
    assert kpi_rules.judge(entry, met, seconds_count=False).word == kpi_rules.OPEN_HELD
    assert kpi_rules.judge(entry, met, seconds_count=True).word == kpi_rules.IMPROVED
    worse = dict(met, ratio_4x_rows=9.0)
    assert kpi_rules.judge(entry, worse, seconds_count=False).word == kpi_rules.OPEN_WORSE
    slow = dict(met, seconds_100k_x20=1000.0)
    assert kpi_rules.judge(entry, slow, seconds_count=True).word == kpi_rules.OPEN_WORSE
    assert kpi_rules.judge(entry, slow, seconds_count=False).word == kpi_rules.OPEN_HELD


def test_seconds_are_judged_only_on_the_quiet_reference_machine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(kpi_rules, "on_reference_machine", lambda ledger: True)
    monkeypatch.setattr(kpi_rules, "load_average", lambda: 0.5)
    assert kpi_rules.seconds_judged_here(LEDGER) == (True, "")
    monkeypatch.setattr(kpi_rules, "load_average", lambda: 18.0)
    judged, why = kpi_rules.seconds_judged_here(LEDGER)
    assert not judged and "loaded" in why
    monkeypatch.setattr(kpi_rules, "on_reference_machine", lambda ledger: False)
    monkeypatch.setattr(kpi_rules, "load_average", lambda: 0.5)
    judged, why = kpi_rules.seconds_judged_here(LEDGER)
    assert not judged and "not the reference machine" in why


def test_a_kpi_test_judges_every_key_it_measures() -> None:
    """A key the test stops recording fails in the suite, not only in the runner (K-P4-11)."""
    entry = kpi_rules.test_part(ENTRIES["K-P4-11"])
    assert "pinned_nodes_failing" not in entry["expected"]
    value = {k: v for k, v in ENTRIES["K-P4-11"]["value_at"]["value"].items()
             if k != "pinned_nodes_failing"}
    assert kpi_rules.judge(entry, value, partial=False).word == kpi_rules.PASS
    lost = {k: v for k, v in value.items() if k != "shapes_equal"}
    verdict = kpi_rules.judge(entry, lost, partial=False)
    assert verdict.word == kpi_rules.FAIL and "shapes_equal: not measured" in verdict.message
    assert kpi_rules.judge(entry, dict(value, shapes_equal=17), partial=False).word == kpi_rules.FAIL


def test_a_run_against_another_checkout_refuses_with_exit_2(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path,
) -> None:
    """Both guards refuse with the integrity exit code, 2, not the drop code, 1."""
    monkeypatch.setattr(kpi_rules, "REPO_ROOT", tmp_path)
    with pytest.raises(SystemExit) as refused:
        kpi_rules.guard_this_tree()
    assert refused.value.code == kpi_rules.REFUSED_EXIT == 2
    monkeypatch.setattr(RUNNER, "SOURCE", tmp_path / "src")
    with pytest.raises(SystemExit) as refused:
        RUNNER._refuse_unless_this_tree()  # type: ignore[attr-defined]
    assert refused.value.code == 2
