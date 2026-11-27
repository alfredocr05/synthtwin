"""Gate file of lane LEDGER: a column the description publishes nothing of leaves no row empty that the real filled.

The patient layer empties the block of a repeated column no row family carries, so the description's twin writes
it blank and the relations zone draws it from the record (`inside_relations.draw_columns`' branch for such a column).
A row drawn into the rest past the record's listed spellings (each unlisted spelling held by fewer rows than the
floor, or past `OTHERS_CAP`) was written EMPTY, because nothing fills such a column later: measured on the data-type
zoo's clinical table at 20,000 rows, a blood pressure written with its unit held 4,940 empty cells, an ISO duration
896, a coma score's parts 233 and a gestational age 28, where the real columns held none.

WHAT IT HOLDS (each clause red on its mutant):

* Drawn with `spill`, no rest row is None: the overflow takes the listed spellings (mutant: `spill` not read).
* The overflow is spread over the listed rows by their counts, three to one here (mutant: the row's place read
  straight into the listed rows, which crowds the overflow onto the rarer spellings).
* A row inside the listed share is the same cell with or without `spill`, and without it the rows past the listed
  spellings are None, as before, for the description's twin to fill (mutant: `spill` on by default).
"""

from __future__ import annotations

from synthtwin import inside_relations

_MASK = (1 << 64) - 1
ENTRY = {
    "levels": ["A"], "rest": 1000, "carried": True, "others": [["b", 300], ["c", 100]],
    "value": {"terms": [], "coefficients": [[], []]},
}
ROWS = 4000
WORDS = [((at + 1) * 0x9E3779B97F4A7C15) & _MASK for at in range(ROWS)]


def _drawn(spill: bool) -> "list[str | None]":
    return list(inside_relations.draw_label(ENTRY, {}, ROWS, WORDS, {"A"}, None, spill=spill).cells)


def test_a_rest_row_past_the_listed_spellings_takes_one_of_them() -> None:
    cells = _drawn(True)
    assert None not in cells
    assert set(cells) == {"A", "b", "c"}


def test_the_overflow_is_spread_over_the_listed_rows_by_their_counts() -> None:
    before = _drawn(False)
    after = _drawn(True)
    overflow = [after[row] for row in range(ROWS) if before[row] is None]
    assert len(overflow) > 600
    share_b = len([cell for cell in overflow if cell == "b"]) / len(overflow)
    assert 0.70 <= share_b <= 0.80, share_b


def test_without_spill_the_rows_past_the_listed_spellings_wait_to_be_filled() -> None:
    before = _drawn(False)
    after = _drawn(True)
    assert None in before
    for row in range(ROWS):
        if before[row] is not None:
            assert after[row] == before[row]
    assert inside_relations.draw_label(ENTRY, {}, ROWS, WORDS, {"A"}).cells == before
