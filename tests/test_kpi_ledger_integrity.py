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
