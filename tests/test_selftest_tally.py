"""Gate file of lane STATS-A (batch 4zz): the chain's self-test lets each estimate go once it is scored.

THE DEFECT (K-HZ on the shipped route, every tree since the self-test was built): the health zoo's wide export, 300
questionnaire items as labels beside a person and a date, 302 columns at 20,000 rows. F1's level part reads each
level of every label column as an outcome in each band of every other column, about 2.7 million estimates there, and
F9 about half a million more; `judge_one` held every one of them, an object of about a kilobyte, until the run's end,
and the answered round's private report reached the laptop's 1.9 GB guard in `_label_rate_estimates` (1.43 -> 1.90 GB
in its last minutes), so K-HZ could not be stamped on the shipped route.

WHAT IT HOLDS: `judge_one` scores each estimate as its producer hands it over and counts it into its family's tally
(`chain_selftest.Tally`), keeping only the correlations (F2) the pairs' words read again; so at no time are more
estimates alive than one producer's batch, the correlations and the pairs' own (measured on the analyst battery's ST4
at 5,000 rows: at most 118 alive of 1,473 scored, against all of them before). Mutant: every estimate kept to the
run's end, as before (`_taken` keeping every family's).

The words are the list's: `word_of` and `family_word` read a tally built from the scored estimates by the same rule
(`tally_of`), and the self-test's own gate file (`test_stage6_selftest_reports.py`) pins them on its vectors.
"""

from __future__ import annotations

import pathlib
import weakref

import analyst_tables
import chain_twins
from synthtwin import chain, chain_selftest, profile, reading, taxonomy


def test_the_self_test_lets_each_estimate_go_once_it_is_scored(tmp_path: pathlib.Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "ST4.csv"
    path.write_text(analyst_tables.text("ST4", 5000, 1), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    table = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings,
                             chain.ChainSwitch("ST4-5000", chain_twins.oc.TEST_KEY, rows_per_person=chain.ROWS_UNASKED))
    assert chained.selftest is not None and chained.statistical is not None
    alive: "list[weakref.ref[chain_selftest.Estimate]]" = []
    most = [0]
    scored_by_family: "dict[str, int]" = {}
    largest_batch = [0]
    scored = chain_selftest.score

    def spy(estimate: chain_selftest.Estimate, sample: int, rows: int, floor: int) -> chain_selftest.Scored:
        scored_by_family[estimate.family] = scored_by_family.get(estimate.family, 0) + 1
        alive.append(weakref.ref(estimate))
        alive[:] = [ref for ref in alive if ref() is not None]
        most[0] = max(most[0], len(alive))
        return scored(estimate, sample, rows, floor)

    for producer in ("_label_rate_estimates", "_rate_estimates"):
        made = getattr(chain_selftest, producer)

        def batch(*arguments: object, _made: object = made, **options: object) -> "list[chain_selftest.Estimate]":
            found = _made(*arguments, **options)  # type: ignore[operator]
            largest_batch[0] = max(largest_batch[0], len(found))
            return found  # type: ignore[no-any-return]

        monkeypatch.setattr(chain_selftest, producer, batch)
    monkeypatch.setattr(chain_selftest, "score", spy)
    judged = chain_selftest.judge_one(chained.selftest, chained.statistical["words"], settings.small_cell_floor,
                                      chain_selftest.SELFTEST_CONSTANT)
    total = sum(scored_by_family.values())
    assert scored_by_family.get("F1", 0) >= 1000, scored_by_family
    kept_whole = scored_by_family.get("F2", 0) + scored_by_family.get("pair", 0)
    assert most[0] <= largest_batch[0] + kept_whole, (
        f"{most[0]} estimates alive at once of {total} scored; the largest batch {largest_batch[0]}, "
        f"the correlations and the pairs' {kept_whole}")
    words = {family.family: family for family in judged.families}
    assert words["F1"].supported == scored_by_family["F1"]
