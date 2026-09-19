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
    board holds 20 to 30 of them.

Whether a pinned node is COLLECTED, and not merely defined, is what the
runner checks when it runs: it exits 2 on a node pytest did not collect.
The mutation tests at the bottom prove each check can fail.
"""

from __future__ import annotations

import copy
import json
import pathlib

import kpi_rules

LEDGER = kpi_rules.load_ledger()


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
        # Seconds are left out: a recorded value may come from a loaded
        # machine, and the rule judges seconds only where they are taken.
        verdict = kpi_rules.judge(entry, value, seconds_count=False, partial=True)
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
