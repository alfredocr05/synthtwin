"""P4-D493 (lane CZ-G): the value readers' residuals that close by a narrow, priced extension of an existing reader; HIPAA first.

THE ITEMS (each read by a reader the line already has, widened):
(1) the band reader: a strict bound after a band's join (`90-<95`, `90 to
<95`) ends one below its age (`taxonomy.an_age_band`); rule A3b reads adult
age groups no chain opens where the age reach leaves them to the band reader
(`_age_shaped_groups`: their stray cells past one in twenty); rule D* (a
closed band of a measure whose last figures pass 125 read as no age) is
WITHDRAWN (the orchestrator's LANE CZ-G RULINGS 7 (1): one stray cell past
125 beside an age chain unread its top), so the measures and every top
written with a placeholder bound past 125 keep the base's reading, the
amounts pooled until `no`; (2) the coordinate reader: hemisphere
letters as their own words (`_a_lettered_pair`); (3) the identifier words: an
age of 90 or more in a phrase of the age vocabulary inside a remark
(`_an_age_past_89_in_words`, one linear pass; a percentile after the number
and a flag's `Y/N` -- `y`, then `/n` with no letter after it -- are none,
while a trailing letter after the slash and a unit of hours or minutes, at
the end of the text too, keep the age: RULINGS 7 (2) and (3)), a
column the top-code covers left to the top-code; (4) a labelled record
number in two groups with a run of spaces, a dash after its label or in
brackets (`asking._record_number_groups`; five figures in all withdrawn after
its price); (5)
telephone groups parted by ` . ` or `_`, a character that prints nothing
inside a run of figures, and age names after a person's word or before
`cls` or `decade`; (6) the bands of five other languages, a closed list of
their unit words, joins and open words (`_BAND_UNITS_ABROAD`); (9) the
further readings of a cell holding the soft hyphen or a character that
prints nothing, each such character set aside and each soft hyphen read as
a dash, in each reader of the lane (`_marks_readings`; LANE CZ-G RULINGS 3,
X1: `90<U+00AD>94`), and a tab at either end of two groups set aside.

THE GATE: each item's GENERATED family, from a grammar written here and
never from a reader's own list, read in full where the base reads part of it
(each expectation built from the family's own numbers); the families of
measures, odd tops and placeholder tops read no more and no less than the
base reads them (the base's reads written here; the measures and the odd
tops as the line reads them since batch 4t's merge of the lane, batch 4s's
fix round, item 4, leaving bands alone to the band reader's own decision); each condition of rule A3b
pinned by a case red on its mutant, and the base's reading of the tops and
the amounts red on the withdrawn rule D*; the near-miss controls of
each reader unread; the marks check (every reader over the owed spaces,
format characters, dashes and the soft hyphen in every owed position and
inside the first word, against its control written with the ordinary mark);
and ONE 20,000-row case through the commands a person types (THE SUITE'S
TIME rule). Every kind in every mode at 20,000 rows, and
the price over the whole zoo, are K-HZ-41's (`tools/measurements/
kpi_value_reader_residuals.py`, `kpi_run --slow`).
"""

from __future__ import annotations

import random

import pytest

import value_reader_residual_forms as residual
import value_readers_forms as readers
from synthtwin import taxonomy

FLOOR = 11


def _reached(cells: "list[str]", named: bool = False) -> bool:
    return taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, False, False, taxonomy.TOP_CODE, named) == (
        taxonomy.SAFE_HARBOR_AGES
    )


# -- (1) THE AGE GROUPS: a family of my own, the expectation by construction --------------------
_POPULATIONS = (
    list(range(25, 105)), list(range(18, 105)), list(range(65, 105)), list(range(18, 45)) + list(range(65, 105)),
    list(range(18, 90)) + list(range(95, 105)), list(range(30, 113)), list(range(40, 121)),
)
_TOPS = (
    ((90, 94), (95, 99), (100, None)), ((90, 94), (95, None)), ((90, 99), (100, None)),
    ((90, 94), (95, 99), (100, 104), (105, None)), ((90, 99), (100, 109), (110, None)), ((95, None),),
)
_SPELLINGS = (("{}-{}", "{}+"), ("{} to {}", "{} and over"), ("{}-{}", ">={}"))
_STRAYS = ("see note 3", "code 00", "18-24 (est)", "grp 7", "unk (999)")


def _lower_schemes() -> "list[tuple[tuple[int, int], ...]]":
    """Bands below 90: chains from many first ages in widths of 3 to 20 years, the last band ending at 89, and unequal adults' groups."""
    found: "list[tuple[tuple[int, int], ...]]" = []
    for start in (16, 18, 21, 22, 25, 30, 40, 50, 60, 65, 70):
        for width in (3, 4, 6, 7, 8, 10, 15, 20):
            bands: "list[tuple[int, int]]" = []
            low = start
            while low <= 89:
                bands += [(low, min(low + width - 1, 89))]
                low = min(low + width - 1, 89) + 1
            found += [tuple(bands)]
    found += [
        ((18, 44), (45, 64), (65, 89)), ((25, 44), (45, 64), (65, 89)), ((18, 64), (65, 89)),
        ((21, 39), (40, 59), (60, 74), (75, 89)), ((65, 79), (80, 89)), ((40, 64), (65, 79), (80, 89)),
    ]
    return found


def age_group_columns(strays: bool) -> "list[list[str]]":
    """Each scheme of `_lower_schemes` topped by each of `_TOPS`, in each spelling, over each population: the columns holding a band starting past 89 that is not the one `90+` alone, which the age reach pools when the name says age; with ``strays``, one cell in thirteen a stray holding figures but no age."""
    found: "list[list[str]]" = []
    index = 0
    for lower in _lower_schemes():
        for tops in _TOPS:
            for closed, opened in _SPELLINGS:
                labelled = [((low, high), closed.format(low, high)) for low, high in lower]
                labelled += [((low, high), closed.format(low, high) if high is not None else opened.format(low))
                             for low, high in tops]
                for population in _POPULATIONS:
                    cells: "list[str]" = []
                    past: "list[tuple[int, int | None]]" = []
                    for (low, high), label in labelled:
                        held = len([age for age in population if age >= low and (high is None or age <= high)])
                        cells += [label] * (3 * held)
                        if held and low >= 90:
                            past += [(low, high)]
                    if len(past) >= 2 or (len(past) == 1 and past[0] != (90, None)):
                        if strays:
                            cells += [_STRAYS[index % len(_STRAYS)]] * max(1, len(cells) // 12)
                        index += 1
                        found += [cells]
    return found


def test_every_generated_age_scheme_with_stray_cells_is_reached_and_pooled() -> None:
    """THE CLASS OF C1 (the orchestrator's LANE CZ-G RULINGS 1 (1) and 2 (1)): on the base the age reach reads every scheme through its numbers, but one stray cell in thirteen took it past the reach's one in twenty, and the band reader's spans read no group no chain opens (61,053 of the lane's 97,428 such columns read); every one is reached and pooled into one category past 89 by the independent reading."""
    columns = age_group_columns(True)
    assert len(columns) > 3000
    missed = [cells for cells in columns if not _reached(cells)]
    assert not missed, (len(missed), sorted(set(missed[0]))[:12])
    for cells in columns[::97]:
        labels = set(taxonomy.top_coded_cells(cells))
        assert len([label for label in labels if readers.label_reaches_90(label)]) <= 1, sorted(labels)


def test_the_age_schemes_are_red_without_rule_a3b(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant without rule A3b leaves most of the strayed schemes unread."""
    monkeypatch.setattr(taxonomy, "_age_shaped_groups", lambda spans: False)
    columns = age_group_columns(True)
    assert len([cells for cells in columns if not _reached(cells)]) > len(columns) // 4


_A3B_READ = {(25, 44): 9, (45, 64): 9, (65, 89): 9, (90, 94): 9, (95, -1): 9}


@pytest.mark.parametrize(("spans", "condition"), [
    ({(0, 59): 9, (60, 89): 9, (90, 100): 9, (101, -1): 9}, "(i) a band past 89 eleven years wide"),
    ({(0, 59): 9, (60, 89): 9, (91, 95): 9, (96, -1): 9}, "(i) a band past 89 not starting at a multiple of five"),
    ({(25, 44): 9, (45, 89): 9, (125, -1): 9}, "(i) an open band past 120"),
    ({(90, 94): 9, (95, -1): 9}, "(ii) no closed band before 90"),
    ({(25, 64): 9, (60, 89): 9, (90, 94): 9, (95, -1): 9}, "(iii) two closed bands overlapping"),
    ({(45, 64): 9, (65, 84): 9, (85, 104): 9, (105, -1): 9}, "(iv) a band holding 90 ending at 104"),
    ({(18, 49): 9, (50, 94): 9, (95, -1): 9}, "(iv) a band holding 90 starting before 60"),
    ({(0, 4): 9, (5, 84): 9, (85, 94): 9, (95, -1): 9}, "(v) a band from 5 eighty years wide"),
])
def test_each_condition_of_rule_a3b_keeps_its_measure_unread(spans: "dict[tuple[int, int], int]", condition: str) -> None:
    """Rule A3b's conditions (plan P4-D493): each spans shape breaks one condition and is no age's groups; the age groups beside them are. A mutant dropping a condition turns its case red."""
    assert taxonomy._age_shaped_groups(_A3B_READ)
    assert not taxonomy._age_shaped_groups(spans), condition


# The measures of the lane's family (none an age) the LINE reads through the
# age reach, a false alarm `no` frees: the head reads them as the line does,
# none more and none fewer (rule D* withdrawn: the orchestrator's LANE CZ-G
# RULINGS 7 (1)). The lane's base read seven, `rate`, `wt` and `min` too
# (lane CZ-E's join, step 9 of batch 4s, took every band among them for an
# age of the reach); batch 4s's fix round, item 4, reads a band as such an
# age only beside the column's own numbers, so bands alone keep the band
# reader's own decision and the line reads four (batch 4t's merge of the
# lane, step 4; LANE I4s RULINGS 1 (4)).
_MEASURES = {
    "rate": ["<60", "60-89", "90-100", ">100"], "sat": ["<85", "85-89", "90-94", "95-100"],
    "wt": ["45-64", "65-84", "85-104", "105+"], "amt": ["5-9", "10-24", "25-49", "50-99", "100-199"],
    "amt_top": ["5-9", "10-24", "25-49", "50-99", "100-199", "200+"], "cnt": ["0", "1-2", "3-5", "6-10", "11+"],
    "pct": ["<5", "5-84", "85-94", ">=95"], "dia": ["<80", "80-89", "90-99", "100-109", "110+"],
    "min": ["0-59", "60-119", "120+"], "glu": ["<70", "70-99", "100-125", "126-199", "200+"],
    "chol": ["<200", "200-239", "240+"], "score": ["0-4", "5-9", "10-14", "15-19", "20-27"],
}
_MEASURES_THE_LINE_READS = frozenset({"sat", "amt", "pct", "dia"})
# ...and those step 9's join read, every band an age of the reach whatever
# stands beside it: the fix round's mutant of its item 4 (`_every_band_a_number`).
_MEASURES_THE_JOIN_READS = frozenset({"rate", "sat", "wt", "amt", "pct", "dia", "min"})


def _measure_cells(labels: "list[str]", strays: bool) -> "list[str]":
    cells: "list[str]" = []
    for place, label in enumerate(labels):
        cells += [label] * (5 + 3 * place)
    return cells + (["see note 3"] * max(1, len(cells) // 12) if strays else [])


# Amounts weighted as such a measure's rows fall, most in the small bands, so
# the band reader's bulk reads them: with `200+` (a band whose first figures
# pass 125) and without it, each pooled until `no`, as on the base.
_AMOUNTS_WEIGHTED = (("5-9", 20), ("10-24", 20), ("25-49", 20), ("50-99", 20), ("100-199", 10), ("200+", 5))


def _weighted_cells(pairs: "tuple[tuple[str, int], ...]", soft: bool = False) -> "list[str]":
    cells: "list[str]" = []
    for label, weight in pairs:
        cells += [label.replace("-", "\xad") if soft else label] * weight
    return cells


def _a_closed_band_past_125(cell: str) -> bool:
    """The withdrawn rule D*'s band of a measure, written here: a closed band whose first number of one to three figures is 125 or less and whose last passes 125, its figures not all nines (`100-199`, `95 to 150`; never `95-999`)."""
    first, _join, last = cell.replace("\xad", "-").replace(" to ", "-").replace(" ", "").partition("-")
    return first.isdigit() and last.isdigit() and len(first) <= 3 and int(first) <= 125 < int(last) and set(last) != {"9"}


def _rule_d_star(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT, the withdrawn rule D* in every column (the orchestrator's LANE CZ-G RULINGS 7 (1)): a closed band whose last figures pass 125 (`_a_closed_band_past_125`) read as a measure's band, never as an age past 89 the band reader missed."""
    original = taxonomy._past_89_unread

    def unread(cell: str, comma: bool = False, mark: int = taxonomy.TOP_CODE) -> bool:
        return not _a_closed_band_past_125(cell) and original(cell, comma, mark)

    monkeypatch.setattr(taxonomy, "_past_89_unread", unread)


def _every_band_a_number(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE FIX ROUND'S MUTANT of its item 4 (batch 4s; `tests/test_merged_line_review_items.py`): every band read as an age of the reach whatever stands beside it, step 9's join unrestricted, its bands taken for numbers."""
    real = taxonomy._safe_harbor_kind

    # ...the kind's fifth argument since batch 4t's merge of lane HB3-a (step 6): the column's gender reading.
    def every_band(
        cell: str, comma: bool, mark: int = taxonomy.TOP_CODE, words: bool = True, genders: bool = False
    ) -> "tuple[int, int, float]":
        kind = real(cell, comma, mark, words, genders)
        band = taxonomy.a_band_cell(cell) if kind[0] == taxonomy._AGE_OTHER else None
        if band is not None:
            return (taxonomy._AGE_ABOVE if taxonomy._band_is_past_89(band, mark) else taxonomy._AGE_IN, kind[1], kind[2])
        return kind

    monkeypatch.setattr(taxonomy, "_safe_harbor_kind", every_band)


def test_the_measures_are_read_no_more_than_the_base_reads_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """The price of item 1 (the stopping rule's 3), the line's reading (rule D* withdrawn, the orchestrator's LANE CZ-G RULINGS 7 (1); batch 4s's fix round, item 4, measured at batch 4t's merge of the lane): no measure is newly reached and none is freed, with stray cells or none; the amounts weighted as such a measure's rows fall are pooled until `no` with `200+` and without it, as on the base (P4-D472 (c), P4-D493 (f)); RED on the fix round's mutant of its item 4 (step 9's join: `rate`, `wt` and `min` reached again) and on the withdrawn rule D*, which freed the amounts."""
    for strays in (False, True):
        read = {name for name, labels in _MEASURES.items() if _reached(_measure_cells(labels, strays))}
        assert read == _MEASURES_THE_LINE_READS - ({"amt"} if strays else set()), (strays, sorted(read))
    assert _reached(_weighted_cells(_AMOUNTS_WEIGHTED))
    assert _reached(_weighted_cells(_AMOUNTS_WEIGHTED[:-1]))
    with monkeypatch.context() as patch:
        _every_band_a_number(patch)
        joined = {name for name, labels in _MEASURES.items() if _reached(_measure_cells(labels, False))}
        assert joined == _MEASURES_THE_JOIN_READS, sorted(joined)
    _rule_d_star(monkeypatch)
    assert not _reached(_weighted_cells(_AMOUNTS_WEIGHTED))


def test_a_top_of_nines_and_a_top_bounded_past_125_keep_the_base_s_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    """The base's reading of a top (rule D* withdrawn, the orchestrator's LANE CZ-G RULINGS 7 (1)): a top written with an upper bound of all nines (`90-999`) and one written with a placeholder bound past 125 (`90-150`) each stay an age's band past 89, pooled, alone and beside a band past 125 (`150+`); RED on the withdrawn rule D*, which read the second as a measure's band beside `150+` and published it."""
    holder = _measure_cells(["0-17", "18-44", "45-64", "65-89", "90-999"], False)
    bounded = _measure_cells(["0-17", "18-44", "45-64", "65-89", "90-150"], False)
    for cells in (holder, holder + ["150+"], bounded, bounded + ["150+"]):
        assert _reached(cells), sorted(set(cells))
    assert _a_closed_band_past_125("100-199") and _a_closed_band_past_125("95 to 150")
    assert not [cell for cell in ("95-999", "90-94", "2019-2020", "200+", "126") if _a_closed_band_past_125(cell)]
    _rule_d_star(monkeypatch)
    assert _reached(holder + ["150+"])
    assert not _reached(bounded + ["150+"])


def test_a_measure_written_with_the_soft_hyphen_is_read_as_with_its_dash(monkeypatch: pytest.MonkeyPatch) -> None:
    """LANE CZ-G RULINGS 3 (1): each banded measure written with the soft hyphen for every dash is reached exactly where its `-` spelling is, with stray cells or none, and the amounts with `200+` are pooled until `no` as their dash spelling is (the base's reading: rule D* withdrawn, RULINGS 7 (1)); RED with no further reading of a cell (the soft hyphen read only as a space, the bands unread)."""
    def soft(labels: "list[str]") -> "list[str]":
        return [label.replace("-", "\xad") for label in labels]

    for strays in (False, True):
        for name, labels in _MEASURES.items():
            assert _reached(_measure_cells(soft(labels), strays)) is _reached(_measure_cells(labels, strays)), (name, strays)
    assert _reached(_weighted_cells(_AMOUNTS_WEIGHTED, True)) and _reached(_weighted_cells(_AMOUNTS_WEIGHTED))
    monkeypatch.setattr(taxonomy, "_marks_readings", lambda text: ())
    assert [name for name, labels in _MEASURES.items()
            if _reached(_measure_cells(soft(labels), False)) is not _reached(_measure_cells(labels, False))]


def test_age_groups_written_with_the_soft_hyphen_are_top_coded_as_their_dash_spelling() -> None:
    """LANE CZ-G RULINGS 3 (1) beside lane HB3-a's reading of a character that prints nothing (batch 4t's merge of lane HB3-a, step 6): every fifth generated age-group column with a hyphen (`age_group_columns`, 1,580 columns), each dash written as the soft hyphen, is reached exactly where its `-` spelling is, and every cell the band reader reads as a band is written by the top-code as its `-` spelling is: the younger bands as written, those past 89 into the one band. RED on the merge commit afe25081, whose number reader set the soft hyphen aside between a band's figures (`18<U+00AD>44` read 1,844 and written `90`: a younger band of each of the 1,580 columns, and 376 of them reached otherwise than their `-` spelling), and without `safe_harbor_number`'s band guard. A band of one age (`89<U+00AD>89`) is no band to the band reader: its figures are joined (8,989) and it is written `90` where its `-` spelling is kept, a stated limit (152 of the 1,580 columns; owner lane CZ-H)."""
    columns = [cells for cells in age_group_columns(False) if any("-" in cell for cell in cells)][::5]
    banded: "dict[str, bool]" = {}
    differ: "list[str]" = []
    for cells in columns:
        soft = [cell.replace("-", "\xad") for cell in cells]
        assert _reached(soft) is _reached(cells), sorted(set(cells))[:4]
        for cell, got, want in zip(soft, taxonomy.top_coded_cells(soft), taxonomy.top_coded_cells(cells)):
            if cell not in banded:
                banded[cell] = taxonomy.a_band_cell(cell) is not None
            if banded[cell] and got != want.replace("-", "\xad"):
                differ += [cell]
    assert differ == [] and len(columns) == 1580, (len(columns), sorted(set(differ))[:4])


def test_odd_tops_keep_the_base_s_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE HIPAA BAR (the stopping rule's 4), against the line (batch 4t's merge of the lane, step 4): the odd tops (`90-92`, `91+`, `90-104`) are reached wherever the line reaches them -- under a name that says age, all 15 columns; under a neutral name, exactly where the band reader's own decision reads them, the reach adding nothing to it for bands alone (batch 4s's fix round, item 4), and that decision reads none of these 15 (P4-D493 (e), restated at the merge: the lane's base reached all 15 through step 9's join, the line and the merged head none, as on the public head); RED on the fix round's mutant of its item 4 (every band an age of the reach), which reaches all 15 under a neutral name, the band reader reading none; the placeholder tops are the generated case below."""
    columns: "list[list[str]]" = []
    for lower in (((25, 44), (45, 64), (65, 89)), ((30, 59), (60, 89)), ((65, 74), (75, 89))):
        for tops in (("90-92", "93+"), ("90-100", "101+"), ("91+",), ("90-104", "105+"), ("92-99", "100+")):
            cells = _measure_cells([f"{low}-{high}" for low, high in lower] + list(tops), False)
            assert _reached(cells, True), cells[-1]
            assert _reached(cells) is taxonomy.age_bands_past_89(cells, frozenset(), False), cells[-1]
            columns += [cells]
    _every_band_a_number(monkeypatch)
    assert all(_reached(cells) and not taxonomy.age_bands_past_89(cells, frozenset(), False) for cells in columns)


# -- (1) THE PLACEHOLDER TOPS (lane CZ-G's repair 1; LANE CZ-G RULINGS 5 (1)): an age chain of four
# bands or more from 0, `<5` or `<18`, six bands too, topped by one band written with a placeholder
# bound past 125 -- a category past 89 the base pools, so each must be reached (the expectation is the
# base's reading, by construction: every column holds a band past 89 written as an age's top).
_CHAINS: "tuple[tuple[tuple[int, int, bool], ...], ...]" = (
    ((0, 17, False), (18, 44, False), (45, 64, False), (65, 89, False)),
    ((0, 17, False), (18, 44, False), (45, 64, False), (65, 94, False)),
    ((0, 17, False), (18, 44, False), (45, 64, False), (65, 99, False)),
    ((0, 17, True), (18, 44, False), (45, 64, False), (65, 89, False)),
    ((0, 17, True), (18, 44, False), (45, 64, False), (65, 94, False)),
    ((0, 17, True), (18, 44, False), (45, 64, False), (65, 99, False)),
    ((0, 4, True), (5, 17, False), (18, 44, False), (45, 64, False), (65, 84, False), (85, 94, False)),
    ((0, 4, False), (5, 17, False), (18, 44, False), (45, 64, False), (65, 84, False), (85, 99, False)),
    ((0, 4, True), (5, 17, False), (18, 44, False), (45, 64, False), (65, 89, False)),
)
_PLACEHOLDER_BOUNDS = (126, 130, 150, 199, 200, 250)
_JOINS = ("{}-{}", "{} - {}", "{} to {}")


def placeholder_top_columns(unit: str = "", extra: "tuple[str, ...]" = ()) -> "list[list[str]]":
    """Each chain of `_CHAINS` (an open-downward first band written `<5` or `<18`), each top from the next age at 90, 95, 100 or 105 or later to each bound of `_PLACEHOLDER_BOUNDS`, in each join; ``unit`` after each band below the top, ``extra`` cells beside (three each)."""
    found: "list[list[str]]" = []
    for chain in _CHAINS:
        end = chain[-1][1]
        for start in (90, 95, 100, 105):
            if start <= end:
                continue
            for bound in _PLACEHOLDER_BOUNDS:
                for join in _JOINS:
                    labels = [(f"<{high + 1}" if below else join.format(low, high)) + unit for low, high, below in chain]
                    labels += [join.format(start, bound)]
                    cells: "list[str]" = []
                    for place, label in enumerate(labels):
                        cells += [label] * (40 + 7 * place)
                    found += [cells + [cell for cell in extra for _ in range(3)]]
    return found


def test_every_placeholder_top_beside_an_age_chain_is_reached() -> None:
    """Item 1's HIPAA bar (skeptic 1's item 1, the orchestrator's LANE CZ-G RULINGS 5 (1) and 7 (1)): the build's rule D* unread 234 of skeptic 1's 648 such columns the base pooled, and at 20,000 rows three published their top with no question, 4,340 twin cells equal to a real cell past 89; each generated column is reached, alone and beside the cells `999`, `9999`, `150`, `-1` and `unknown`, as the base reaches it."""
    for extra in ((), ("999", "9999", "150", "-1", "unknown")):
        columns = placeholder_top_columns(extra=extra)
        assert len(columns) > 300
        missed = [sorted(set(cells))[-1] for cells in columns if not _reached(cells)]
        assert missed == [], (extra, len(missed), missed[:6])


def test_the_placeholder_tops_are_red_on_rule_d_star(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: the withdrawn rule D* in every column (the build's head, before repair 1) unreads most of the generated placeholder tops."""
    _rule_d_star(monkeypatch)
    columns = placeholder_top_columns()
    assert len([cells for cells in columns if not _reached(cells)]) > len(columns) // 2


# ONE stray cell whose first figures pass 125 (the lane's verify, BLOCKER 1): a
# year span, a number written with a dash, an open band, a closed band.
_STRAYS_PAST_125 = ("2019-2020", "555-0100", "150+", "200+", "126-199")


def test_every_placeholder_top_beside_one_stray_cell_past_125_is_reached(monkeypatch: pytest.MonkeyPatch) -> None:
    """BLOCKER 1 of the lane's verify (the orchestrator's LANE CZ-G RULINGS 7 (1)): repair 1's rule D* read ONE cell whose first figures pass 125 -- `2019-2020`, `555-0100`, `150+`, `200+` or `126-199` -- as a measure's band and unread every generated top written with a placeholder bound past 125 beside an age chain, which the base pools (at 20,000 rows one stray row published `95-150` with no question, 1,846 twin cells equal to a real cell past 89); rule D* is withdrawn, so each column is reached beside each stray under a neutral name, a name that says age and a unit word of years, as on the base; RED on repair 1's head and on the withdrawn rule's mutant."""
    columns = placeholder_top_columns()
    worded = placeholder_top_columns(unit=" yrs")
    assert len(columns) > 300
    for stray in _STRAYS_PAST_125:
        assert not [cells[-2] for cells in columns if not _reached(cells + [stray])], stray
        assert not [cells[-2] for cells in columns if not _reached(cells + [stray], True)], stray
        assert not [cells[-2] for cells in worded if not _reached(cells + [stray])], stray
    _rule_d_star(monkeypatch)
    assert len([cells for cells in columns if not _reached(cells + ["2019-2020"])]) > len(columns) // 2


# -- (1) RULE A3b'S CONDITION (iv), the HIPAA side (skeptic 1's item 2 (b)): a band holding 90 that
# starts at 60 or later and ends at 94 or 99, after adult groups no chain opens, topped by `95+`, `100+`
# or `95-99, 100+`, with stray cells or none: an age's groups, each reached.
_ADULT_OPENINGS = (((25, 44), (45, 64)), ((30, 59),), ((40, 64),), ((25, 59),), ((18, 44), (45, 64)), ((25, 49), (50, 64)))
_HOLDING_90 = ((60, 94), (65, 94), (65, 99), (70, 94), (75, 99), (80, 94), (85, 94), (85, 99), (80, 99))


def _age_cells(labels: "list[str]", strays: bool) -> "list[str]":
    """Each band on 40 rows and 7 more a band (every band at the floor), one cell in thirteen a stray holding a figure but no age."""
    cells: "list[str]" = []
    for place, label in enumerate(labels):
        cells += [label] * (40 + 7 * place)
    return cells + (["see note 3"] * max(1, len(cells) // 12) if strays else [])


def holding_90_columns() -> "list[list[str]]":
    found: "list[list[str]]" = []
    for lower in _ADULT_OPENINGS:
        for low, high in _HOLDING_90:
            if low <= lower[-1][1]:
                continue
            for top in ((("95+",), ("95-99", "100+")) if high == 94 else (("100+",),)):
                for strays in (False, True):
                    labels = [f"{first}-{last}" for first, last in lower] + [f"{low}-{high}", *top]
                    found += [_age_cells(labels, strays)]
    return found


def test_a_band_holding_90_after_adult_groups_is_reached_and_red_on_condition_iv_s_mutants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every generated column is reached; condition (iv) moved to start at 89 or 65, or to end at 94 only, unreads some (the base read 80 of skeptic 1's 152 such columns)."""
    columns = holding_90_columns()
    assert len(columns) > 100
    assert not [cells for cells in columns if not _reached(cells)]
    for name, value in (("_HOLDING_90_FROM", 89), ("_HOLDING_90_FROM", 65), ("_HOLDING_90_ENDS", (94,))):
        monkeypatch.setattr(taxonomy, name, value)
        assert [cells for cells in columns if not _reached(cells)], (name, value)
        monkeypatch.undo()


@pytest.mark.parametrize(("text", "start", "end"), [
    ("90-<95", 90, 94), ("90 to <95", 90, 94), ("25-<45", 25, 44), ("90 - < 95", 90, 94), ("90–<95", 90, 94),
    ("65 to < 90", 65, 89), ("90-<95 yrs", 90, 94), ("Age 90-<95", 90, 94),
])
def test_a_strict_bound_after_the_join_ends_one_below_its_age(text: str, start: int, end: int) -> None:
    """Item 1's strict bound (plan P4-D493): `90-<95` holds 90 to 94, as `<95` alone ends at 94; `90-<91` is no band."""
    band = taxonomy.an_age_band(text)
    assert band is not None and (band.start, band.end) == (start, end), text
    assert taxonomy.an_age_band("90-<91") is None and taxonomy.an_age_band("90-<=94") is None


def test_the_strict_schemes_are_reached_and_red_without_the_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """The strict schemes under a neutral name (`25-<45 ... 90-<95, 95+`, with a hyphen and with `to`): reached, one category past 89; the base published both bands past 89."""
    for joined in ("{}-<{}", "{} to <{}"):
        cells = _measure_cells([joined.format(low, high + 1) for low, high in ((25, 44), (45, 64), (65, 89), (90, 94))]
                               + ["95+"], False)
        assert _reached(cells)
        assert len([label for label in set(taxonomy.top_coded_cells(cells)) if readers.label_reaches_90(label)]) == 1


# -- (2) THE LETTERED PAIRS -------------------------------------------------------------------
def lettered_spellings() -> "list[tuple[str, bool]]":
    """A latitude and a longitude of three to six places, N or S and E or W (small letters one in five), the letters after or before their numbers or the longitude first, a degree mark glued, spaced or none, one or two spaces, a tab or a no-break space between; alone or among words (True)."""
    draw = random.Random(residual.SEED)
    found: "list[tuple[str, bool]]" = []
    for case in range(2400):
        places = 3 + case % 4
        lat = f"{draw.uniform(0.5, 89.9):.{places}f}"
        lon = f"{draw.uniform(0.5, 179.9):.{places}f}"
        north, east = draw.choice("NS"), draw.choice("EW")
        if case % 5 == 0:
            north, east = north.lower(), east.lower()
        degree = ("", "°", " °")[case % 3]
        gap = (" ", "  ", "\t", "\xa0")[(case // 3) % 4]
        order = (case // 12) % 3
        if order == 0:
            text = f"{lat}{degree} {north}{gap}{lon}{degree} {east}"
        elif order == 1:
            text = f"{north} {lat}{degree}{gap}{east} {lon}{degree}"
        else:
            text = f"{lon}{degree} {east}{gap}{lat}{degree} {north}"
        context = (case // 36) % 4
        found += [(text, False) if context == 0 else
                  (("home {}", "loc: {} per chart", "pt lives at {} today")[context - 1].format(text), True)]
    return found


def test_every_lettered_pair_is_read() -> None:
    """Item 2 (C2): every generated lettered pair is read, in a cell (`a_coordinate_pair`) and among words (`identifier_words_form`); the base read none."""
    missed = [text for text, words in lettered_spellings()
              if not (taxonomy.identifier_words_form(text) if words else taxonomy.a_coordinate_pair(text))]
    assert not missed, missed[:6]


@pytest.mark.parametrize("text", [
    "41.78396 N 42.11234 N", "86.59340 W 91.53210 E", "41.783 N", "9.807 N 1.234 N", "95.12345 N 86.59340 W",
    "12.345 S 13.333 S", "0.512 N 0.733 W", "100.123 N 45.123 E", "N 41.783 N 86.593", "41.78 N 86.59 W",
])
def test_the_lettered_near_misses_stay_unread(text: str) -> None:
    """Two latitude letters, two longitude letters, one number, gravity, a number past 90 under N, two shares, two places: no pair."""
    assert not taxonomy.a_coordinate_pair(text) and not taxonomy.identifier_words_form("loc " + text)


def test_the_lettered_pairs_are_red_without_the_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_a_lettered_pair", lambda pieces: False)
    assert not taxonomy.a_coordinate_pair("41.78396 N 86.5934 W")
    assert not taxonomy.identifier_words_form("home 41.78396 N 86.5934 W")


# -- (3) AN AGE OF 90 OR MORE INSIDE A REMARK ----------------------------------------------------
_AGE_PHRASES = ("{a} yo", "{a} y/o", "{a} y.o.", "{a}yo", "{a} year old", "{a}-year-old", "{a} years old", "{a} yr old",
                "aged {a}", "age {a}", "Age: {a}", "{a} YO", "AGE {a}", "{a}-yr-old", "{a} yrs old", "Aged\xa0{a}")
_FRAMES = ("{p} F, fall at home", "pt is a {p} male", "{p} with cough", "seen today, {p}, lives alone",
           "{p} M here with daughter", "note: {p}; ambulates with walker")


def test_every_age_past_89_inside_a_remark_is_read_and_younger_ones_are_not() -> None:
    """Item 3: every generated phrase of an age of 90 to 125 inside a remark is an identifier form; the same phrases of ages under 90 are none (an age under 90 is no Safe Harbor element)."""
    old = [frame.format(p=phrase.format(a=age)) for phrase in _AGE_PHRASES for frame in _FRAMES for age in range(90, 126, 7)]
    young = [frame.format(p=phrase.format(a=age)) for phrase in _AGE_PHRASES for frame in _FRAMES for age in (21, 67, 89)]
    assert not [text for text in old if taxonomy.identifier_words_form(text) != taxonomy.WORDS_AGE_PAST_89]
    assert not [text for text in young if taxonomy.identifier_words_form(text)]


@pytest.mark.parametrize("text", [
    "room 95 cleaned", "bed 102 ready", "glucose 105 mg/dL at noon", "weight 98 kg today", "age 100 days old",
    "age of wound 95 days", "95th percentile for weight", "score 99 of 100", "ward 91 transfer", "average 95 today",
    "page 95 of note", "1995 yrs ago noted", "dose 100 units given", "ages 95 and up",
])
def test_the_remark_controls_hold_no_age(text: str) -> None:
    """Scores, amounts with a unit, rooms, an infant's days, a percentile, `ages`, `average`, `page`: no age of 90 or more."""
    assert not taxonomy.identifier_words_form(text)


def _an_age_past_90_left(coded: str) -> bool:
    """Whether a cell the top-code wrote still holds an age past 90 by this lane's reader of an age inside a remark (`_an_age_past_89_in_words` from 91: the top-code writes every age of 90 or more as 90)."""
    return taxonomy._an_age_past_89_in_words(taxonomy._value_body(coded), taxonomy.TOP_CODE + 1)


def test_an_age_column_the_top_code_covers_is_left_to_the_top_code() -> None:
    """THE BOUNDARY (the orchestrator's LANE CZ-G RULINGS 1 (8)): `Age 18` to `Age 105`, `NN yo` and `Age NN, male` are reached and top-coded, never held; a remark column the top-code leaves an age past 90 in is held whole (the case below). SINCE BATCH 4t'S MERGE OF LANE HB3-a (step 6) the remark column of K-HZ-41's kind (`residual.remark_ages`, 20,000 rows) is one the top-code covers: the reach's reader of an age's phrase (`taxonomy._phrase_age`, plan P4-D482) top-codes every age of 90 or more in its remarks (`94 yo F, fall at home` is written `90 yo F, fall at home`), no cell the top-code writes holds an age past 90 by this lane's reader, and the column is reached and top-coded, never held (the line before the merge held it whole: the agreement case below)."""
    for written in ("Age {}", "{} yo", "Age {}, male"):
        cells = [written.format(age) for age in list(range(18, 90)) * 30 + list(range(90, 106)) * 12]
        assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), FLOOR) == ""
        assert _reached(cells)
    header, rows = residual.remark_ages(20000, residual.SEED)
    cells = [row[header.index("remark_age")] for row in rows]
    assert taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), FLOOR) == ""
    assert _reached(cells)
    assert not [cell for cell in set(taxonomy.top_coded_cells(cells)) if _an_age_past_90_left(cell)]


def test_the_remark_ages_are_red_without_the_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_an_age_past_89_in_words", lambda body, least=90: False)
    assert taxonomy.identifier_words_form("94 yo F, fall at home") == ""


# A remark the top-code leaves an age past 90 in, each on 30 rows of an age
# column the reach top-codes. Before batch 4t's merge of lane HB3-a (step 6)
# these were someone else's age or one not opening the cell
# (`_COVERED_SINCE_THE_MERGE`), which the reach's reader of an age's phrase
# top-codes since (`taxonomy._phrase_age`, plan P4-D482: every number of an
# age word's clause, and every number its age's unit follows, an age); on the
# merged line the top-code leaves such an age where a lone `D` or `W` follows
# an age word's number: that reader reads days or weeks, this lane's reader
# no unit (HIPAA first), so the column is held whole.
_COVERED_SINCE_THE_MERGE = ("Age 70, wife aged {a}", "Age 92, son aged {a}", "pt is a {a} year old male",
                            "{a} yo F, fall at home", "Age 95 ({a} per family)", "seen with mother, aged {a}",
                            "Age 60, father {a} yo")
_LEFT_AFTER_THE_TOP_CODE = ("Age {a} D", "Age {a} W", "aged {a} D", "Age: {a} D", "Pt age {a} W", "age {a} d",
                            "Age {a} D today", "AGE {a} W, lives alone")


def left_after_the_top_code_columns(ages: "tuple[int, ...]") -> "list[list[str]]":
    found: "list[list[str]]" = []
    for written in ("Age {}", "{} yo", "Age {}, male"):
        ages_column = [written.format(age) for age in list(range(18, 90)) * 30 + list(range(90, 106)) * 12]
        for template in _LEFT_AFTER_THE_TOP_CODE:
            for age in ages:
                found += [ages_column + [template.format(a=age)] * 30]
    return found


def test_a_remark_the_top_code_leaves_an_age_past_90_in_is_held_and_red_on_its_mutants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Item 3's branch beside the top-code (skeptic 1's item 2 (a), the orchestrator's LANE CZ-G RULINGS 1 (8)): an age column holding a remark whose age past 90 the top-code leaves, ages 91 to 125, is held whole (the base top-coded `pt is a 92 year old male` and `Age 70, wife aged 95` and published the remark, 1,000 real twin cells at 20,000 rows; since batch 4t's merge of lane HB3-a the top-code covers those and the branch is pinned on `Age 95 D` and `Age 95 W`, which it leaves); RED where that branch is never taken, and where it reads ages from 95 (91 to 94 released)."""
    def held(cells: "list[str]") -> bool:
        return taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, cells, frozenset(), FLOOR) == taxonomy.HELD_IDENTIFIER_WORDS

    columns = left_after_the_top_code_columns((91, 92, 93, 94, 96, 99, 104, 110, 125))
    assert not [cells[-1] for cells in columns if not held(cells)]
    monkeypatch.setattr(taxonomy, "_ages_left_after_the_top_code", lambda cells, absent, floor: False)
    assert not [cells[-1] for cells in columns if held(cells)]
    monkeypatch.undo()
    original = taxonomy._an_age_past_89_in_words
    monkeypatch.setattr(taxonomy, "_an_age_past_89_in_words", lambda body, least=90: original(body, 95 if least == 91 else least))
    assert len([cells for cells in left_after_the_top_code_columns((91, 92, 93, 94)) if not held(cells)]) > 50


# THE AGREEMENT OF THE TWO READERS (the orchestrator's LANE CZ-G RULINGS 1 (8) and 4 (2), owed at the second of
# the two merges: batch 4t's merge of lane HB3-a, step 6). Lane HB3-a's reader of an age's phrase top-codes
# (`taxonomy._phrase_age`, plan P4-D482) and this lane's reader of an age inside a remark holds
# (`_an_age_past_89_in_words`); on the same cells a column is never both. The grammar is written here: this lane's
# remarks (`_AGE_PHRASES` in `_FRAMES`), the remarks the top-code left before the merge, the ages beside a vital's
# label or a side letter and the specimens' ages (both below), the forms the top-code leaves, and lane HB3-a's
# phrases, written here and never read from its gate.
_PHRASES_OF_HB3A = ("Age at diagnosis: {a}", "Pt age: {a}", "Age (yrs): {a}", "Age {a} M", "{a} years 3 months",
                    "{a} y/o F", "A {a}-year-old woman", "Onset age 91, current age {a}", "Age {a} (onset 92)",
                    "Seen at age {a} today", "Age {a}, male", "Female, {a} years old")
_AGREEMENT_AGES = (90, 91, 94, 104, 125)
_AGES_BESIDE = [f"Age {age}" for age in range(18, 106) for _row in range(12)]


def agreement_families() -> "dict[str, tuple[str, ...]]":
    """The generated forms of an age of 90 to 125 years, by family (`{a}` the age)."""
    return {
        "remarks": tuple(frame.format(p=phrase) for phrase in _AGE_PHRASES for frame in _FRAMES),
        "covered since the merge": _COVERED_SINCE_THE_MERGE,
        "beside a label or a side": tuple(text.replace("{n}", "{a}") for text in _STILL_AGES),
        "specimens": tuple(text.replace("{n}", "{a}") for text in _SPECIMEN_AGES),
        "left by the top-code": _LEFT_AFTER_THE_TOP_CODE,
        "phrases of lane HB3-a": _PHRASES_OF_HB3A,
    }


def readers_agree(families: "dict[str, tuple[str, ...]]") -> "dict[str, list[str]]":
    """Each form of each family at each age of `_AGREEMENT_AGES`, on 30 rows beside `_AGES_BESIDE` (88 ages on 12 rows each), by what the two readers do: `covered`, the column left to the top-code and its cell written with no age past 90 this lane's reader reads; `held`, the column held whole where the top-code leaves one; `published`, left to the top-code with one left (never); `needless`, held, or held otherwise, where the top-code leaves none (never)."""
    found: "dict[str, list[str]]" = {"covered": [], "held": [], "published": [], "needless": []}
    for templates in families.values():
        for template in templates:
            for age in _AGREEMENT_AGES:
                cell = template.format(a=age)
                left = _an_age_past_90_left(taxonomy.top_coded_cells([cell])[0])
                hold = taxonomy.value_reader_hold(taxonomy.ROLE_CATEGORICAL, _AGES_BESIDE + [cell] * 30, frozenset(), FLOOR)
                if hold == "":
                    found["published" if left else "covered"] += [cell]
                else:
                    found["held" if left and hold == taxonomy.HELD_IDENTIFIER_WORDS else "needless"] += [cell]
    return found


def test_the_age_phrase_reader_and_the_remark_reader_agree_on_every_generated_cell(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE AGREEMENT (LANE CZ-G RULINGS 1 (8) and 4 (2); batch 4t's merge of lane HB3-a, step 6): on 720 generated cells of an age of 90 to 125 years (144 forms, five ages), each on 30 rows beside an age column the reach top-codes, a column is never both: it is held whole exactly where the top-code leaves an age past 90 this lane's reader reads, and left to the top-code, reached, everywhere else. Every remark of this lane's item 3, every remark the top-code left before the merge, every specimen's age and every phrase of lane HB3-a is covered (lane HB3-a's reader top-codes each age of 90 or more in it: item 3 leaves for them, as RULINGS 1 (8) foresaw); the forms the top-code leaves (`Age 95 D`, `Age 95 W`: days or weeks to the phrase reader, no unit to this lane's) are held, each age past 90. RED where the hold is never taken (`_ages_left_after_the_top_code` False: those forms published with their age) and where the age's phrase is not read (`_phrase_age` reading none: the remarks held again, the agreement's covered forms fewer)."""
    families = agreement_families()
    found = readers_agree(families)
    assert found["published"] == [] and found["needless"] == [], (found["published"][:5], found["needless"][:5])
    left = {template.format(a=age) for template in _LEFT_AFTER_THE_TOP_CODE + ("Age {a} D",) for age in _AGREEMENT_AGES
            if age > 90}
    assert set(found["held"]) == left, sorted(set(found["held"]) ^ left)[:5]
    cells = sum(len(templates) for templates in families.values()) * len(_AGREEMENT_AGES)
    assert len(found["covered"]) + len(found["held"]) == cells == 720, (len(found["covered"]), len(found["held"]))
    with monkeypatch.context() as patch:
        patch.setattr(taxonomy, "_ages_left_after_the_top_code", lambda cells, absent, floor: False)
        assert len(readers_agree({"left": _LEFT_AFTER_THE_TOP_CODE})["published"]) == 32
    with monkeypatch.context() as patch:
        patch.setattr(taxonomy, "_phrase_age", lambda head, rest, after, comma, genders=False: None)
        without = readers_agree({"remarks": families["remarks"], "covered": _COVERED_SINCE_THE_MERGE})
        assert without["published"] == [] and len(without["covered"]) < len(families["remarks"]) * len(_AGREEMENT_AGES)


# What after the age word's number says it is no person's age (lane CZ-G's repair 1, the statistics
# check's item 2): a growth chart's percentile; and what stays an age, HIPAA first: a vital's label,
# `h/o`, `min assist`, a side letter and a unit of hours or minutes after it, at the end of the text
# too (the orchestrator's LANE CZ-G RULINGS 6 (1) and 7 (3): a specimen's age in hours is held until
# `no`, the stated price, plan P4-D493 (k)).
_GROWTH_MEASURES = ("Weight", "Length", "Stature", "Head circumference", "Weight-for-length")
_GROWTH = ("{m}-for-age {p}{s} percentile", "{m}-for-age {p}{s} percentile or above", "{m} for age {p}{s} %ile",
           "{m}-for-age >= {p}{s} percentile", "{m}-for-age {p}-{q}{s2} percentile", "{m}-for-age above {p}{s} centile",
           "{m} for age {p}%", "{m} for age {p} pctl")
_SPECIMEN_AGES = ("postnatal age {n} h", "specimen age {n} h", "sample age {n} hrs", "unit age {n} h",
                  "post-dose age {n} min", "sample age {n} hours", "specimen age {n} minutes", "postnatal age {n} hr")
_STILL_AGES = ("Age {n} HR 88", "age {n} h/o CHF", "Age {n} min assist", "Age {n} D", "AGE {n} HR 72 RR 16",
               "aged {n} hr 110 bp 90/60", "Age: {n} h/o falls", "pt age {n} min A x1", "Age {n} hr: 64", "{n} y F",
               "{n} y/o F", "Age {n} yrs", "aged {n}, lives alone")


def _ordinal(number: int) -> str:
    return "th" if 10 <= number % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


def no_age_phrases() -> "list[str]":
    found = []
    for template in _GROWTH:
        for measure in _GROWTH_MEASURES:
            for number in range(90, 100):
                later = min(number + 2, 99)
                found += [template.format(m=measure, p=number, s=_ordinal(number), q=later, s2=_ordinal(later))]
    return found


def test_a_percentile_after_the_age_word_is_no_age() -> None:
    """The statistics check's item 2: the head read every growth chart's percentile after the age word as an age of 90 or more and held such a label column whole (20,000 of 20,000 twin cells off their level at 20,000 rows, where the base published them); none is read now, and every true age beside them still is."""
    assert not [text for text in no_age_phrases() if taxonomy.identifier_words_form(text)]
    still = [template.format(n=number) for template in _STILL_AGES for number in range(90, 126, 5)]
    assert not [text for text in still if taxonomy.identifier_words_form(text) != taxonomy.WORDS_AGE_PAST_89]


def test_the_no_age_phrases_are_red_without_their_words(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS: without the ordinal or the percentile's words, the phrases read as ages again."""
    for name, value in (("_ordinal_after", lambda small, place: False), ("_PERCENTILE_WORDS", ())):
        monkeypatch.setattr(taxonomy, name, value)
        assert [text for text in no_age_phrases() if taxonomy.identifier_words_form(text)], name
        monkeypatch.undo()


# A unit of hours or minutes after an age word's number (the lane's verify, CARRY C2): every phrase of
# this grammar, glued or spaced, ending the text or before more words, names an age of 90 to 125.
_AGE_WORD_PHRASES = ("Age {n}", "age {n}", "Pt age {n}", "AGE {n}", "aged {n}", "Age: {n}")
_HOURS_OR_MINUTES = ("H", "h", "hr", "Hr", "HR", "hrs", "hour", "hours", "min", "mins", "minute", "minutes")
_UNIT_ENDINGS = ("", ".", " noted", ", fall at home")


def unit_after_age_phrases() -> "list[str]":
    found = []
    for phrase in _AGE_WORD_PHRASES:
        for unit in _HOURS_OR_MINUTES:
            for glue in (" ", ""):
                for ending in _UNIT_ENDINGS:
                    found += [phrase.format(n=number) + glue + unit + ending for number in (90, 94, 97, 103, 110, 125)]
    return found


def test_a_unit_of_hours_or_minutes_after_an_age_word_s_number_keeps_the_age() -> None:
    """CARRY C2 of the lane's verify, HIPAA first (the orchestrator's LANE CZ-G RULINGS 6 (1) and 7 (3)): repair 1 read a unit of hours or minutes ending a remark after an age word's number as no age (`Age 94 H`, `age 94 hr`, `age 94 min`: 360 of the verify's 3,240 age texts, and at 20,000 rows `Pt age NN h` published 3 categories past 89, 6,060 twin cells), where the build read an age; every generated phrase reads as an age of 90 or more again, and so do a specimen's hours (`postnatal age 96 h`: the stated false alarm, held until `no`); RED on repair 1's head."""
    phrases = unit_after_age_phrases()
    assert len(phrases) > 3000
    assert not [text for text in phrases if taxonomy.identifier_words_form(text) != taxonomy.WORDS_AGE_PAST_89]
    specimens = [template.format(n=number) for template in _SPECIMEN_AGES for number in range(90, 126, 5)]
    assert not [text for text in specimens if taxonomy.identifier_words_form(text) != taxonomy.WORDS_AGE_PAST_89]


def test_a_flag_s_y_before_a_slash_is_no_year_and_a_lone_y_still_is() -> None:
    """Skeptic 1's item 4, priced first (P4-D493): a measure's flag `Y/N` after a value of 90 to 125 is no age (the head read it and held such a column whole); a lone `y` stays a year's letter, HIPAA first (`94 y F`; `sats 95 Y` is the stated price)."""
    for text in ("SpO2 96 Y/N", "sats 95 y/n", "FEV1 110 Y/N done", "HR 100 y/n"):
        assert taxonomy.identifier_words_form(text) == "", text
    for text in ("94 y F", "94 y/o F", "sats 95 Y", "pt 92 y, lives alone"):
        assert taxonomy.identifier_words_form(text) == taxonomy.WORDS_AGE_PAST_89, text


# A trailing letter after the slash (the lane's verify, CARRY C1): `y`, a slash and a letter other than
# `n` (or `o`, the unit `y/o`), or `n` with a letter after it (`NH`), glued or spaced, in a remark; and a
# measure's flag, `y` then `/n` with no letter after it, in each case.
_SLASHED_LETTERS = ("F", "M", "f", "m", "F/W", "M/B", "W", "B", "U", "X", "NH")
_SLASHED_FRAMES = ("{p}", "Pt {p}, fall at home", "seen today, {p} with cough", "{p} c/o SOB", "pt is {p}.")
_FLAG_FRAMES = ("SpO2 {n} {f}", "sats {n} {f}", "HR {n} {f} done", "FEV1 {n} {f}.", "score {n} {f}, rechecked")


def slashed_letter_phrases() -> "list[str]":
    found = []
    for letter in _SLASHED_LETTERS:
        for year in ("Y", "y"):
            for glue in (" ", ""):
                for frame in _SLASHED_FRAMES:
                    found += [frame.format(p=f"{number}{glue}{year}/{letter}") for number in (90, 94, 99, 104, 117, 125)]
    return found


def test_a_trailing_letter_after_a_slash_keeps_the_age_and_only_y_n_is_a_flag() -> None:
    """CARRY C1 of the lane's verify, HIPAA (the orchestrator's LANE CZ-G RULINGS 7 (2)): repair 1 read a lone `y` before ANY slash as no year, so an age past 89 with a trailing letter after the slash went unread (`94 Y/F`, `94y/m`: 504 of the verify's 3,240 age texts, and at 20,000 rows 18 categories past 89 shown on 3 columns, 18,180 twin cells equal to a real remark); the slash reads as a flag only before `n` with no letter after it: every generated phrase reads as an age of 90 or more, and every flag `Y/N` of each case reads as none; RED on repair 1's head."""
    phrases = slashed_letter_phrases()
    assert len(phrases) > 1000
    assert not [text for text in phrases if taxonomy.identifier_words_form(text) != taxonomy.WORDS_AGE_PAST_89]
    flags = [frame.format(n=number, f=flag) for frame in _FLAG_FRAMES for flag in ("Y/N", "y/n", "Y/n", "y/N")
             for number in (90, 95, 100, 110, 125)]
    assert not [text for text in flags if taxonomy.identifier_words_form(text)]


def _ages_in_words_whole(body: str, least: int = 90) -> bool:
    """The age words read on the whole rest of the text at each word opening (the reader before repair 1), the expectation of the window."""
    plain = taxonomy._age_plain(body)
    small = plain.lower()
    for place in range(len(small)):
        if place > 0 and (small[place - 1].isalnum() or small[place - 1] == "."):
            continue
        if small[place] == "a":
            start = taxonomy._age_word_at(plain[place:])
            if start >= 0:
                at = place + start
                if small[at: at + 1] in ("(", "["):
                    at = taxonomy._band_spaces(small, at + 1)
                if taxonomy._an_age_past_89_at(small, at, least):
                    return True
    return False


def test_the_age_word_s_window_reads_as_the_whole_rest_of_the_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skeptic 1's item 5 (G4): the age word is read on a window, one linear pass; every generated phrase -- a word, then runs of 0 to 40 spaces around a mark, a bracket, a sign and a point before the number -- reads as on the whole rest of the text; a window short of the five characters the word reader reads after its word is RED."""
    draw = random.Random(residual.SEED + 4)
    texts = []
    for case in range(1200):
        gaps = [" " * draw.choice((0, 1, 2, 9, 40)) for _ in range(4)]
        mark = draw.choice(("", ":", "=", "-"))
        bracket = draw.choice(("", "(", "["))
        number = draw.choice(("95", "-95", ".95", "102", "89", "+97", "9"))
        word = draw.choice(("age", "Aged", "AGE", "ages", "agent"))
        texts += [f"note {case}, {word}{gaps[0]}{mark}{gaps[1]}{bracket}{gaps[2]}{number}{gaps[3]} at home"]
    assert sum(_ages_in_words_whole(text) for text in texts) > 100
    assert not [text for text in texts if taxonomy._an_age_past_89_in_words(text) is not _ages_in_words_whole(text)]
    monkeypatch.setattr(taxonomy, "_AGE_WORD_SOLID", 2)
    assert [text for text in texts if taxonomy._an_age_past_89_in_words(text) is not _ages_in_words_whole(text)]


def test_the_question_of_a_column_held_for_an_age_in_words_names_it() -> None:
    """The statistics check's item 4 (G3): the Safe Harbor question of a column held for identifier words names an age of 90 or more written in words among what it saw."""
    from synthtwin import asking

    words = asking._value_reader_seen(asking.BECAUSE_SAFE_HARBOR_IDENTIFIER_WORDS)
    assert "an age of 90 or more written in words" in words
    question = asking._safe_harbor_question("c", "categorical", asking.BECAUSE_SAFE_HARBOR_IDENTIFIER_WORDS, 1937)
    assert "an age of 90 or more written in words" in question.shape


# -- (4) RECORD NUMBERS IN TWO GROUPS NO READER KNEW ---------------------------------------------
_RECORD_ROWS = 600
_RECORD_LABELS = ("MR", "AB", "#MR", "Q", "\u039c\u03a1")
_RECORD_SPELLINGS = {
    "two spaces": "{label}{a}  {b}", "three spaces": "{label}{a}   {b}", "a tab and a space": "{label}{a}\t {b}",
    "a dash after the label": "{label}-{a} {b}", "a dash and two spaces": "{label}-{a}  {b}",
    "round brackets": "({label}{a} {b})", "curly brackets": "{{{label}{a} {b}}}", "brackets and a dash": "({label}-{a} {b})",
}


def record_columns() -> "list[tuple[str, list[str], bool]]":
    """Each label of `_RECORD_LABELS`, seven figures split after two to five, each spelling of `_RECORD_SPELLINGS`, one a row and one a person (`labelled_records`' 1,000 people of 20 rows)."""
    import labelled_records as records

    found: "list[tuple[str, list[str], bool]]" = []
    for label in _RECORD_LABELS:
        for opening in (2, 3, 4, 5):
            for name, written in _RECORD_SPELLINGS.items():
                for one_a_person in (False, True):
                    units = [row // records.ROWS_A_PERSON if one_a_person else row for row in range(_RECORD_ROWS)]
                    cells = []
                    for unit in units:
                        figures = f"{records.NUMBER_FROM + unit}"
                        cells += [written.format(label=label, a=figures[:opening], b=figures[opening:])]
                    found += [(f"{label} {opening} {name} {one_a_person}", cells, one_a_person)]
    return found


def test_every_record_number_in_two_groups_of_the_widened_spellings_is_held() -> None:
    """Item 4 (LANE CZ-A2 RULINGS 11 (2), limit (n)): two spaces or more between the groups, a dash joining the label, the cell in round or curly brackets -- each label, split and spelling, one a row and one a person -- is held by a reader (`labelled_records.held_by_a_reader`); the base held none of them."""
    import labelled_records as records

    unheld = [label for label, cells, one_a_person in record_columns() if not records.held_by_a_reader(cells, one_a_person)]
    assert unheld == [], (len(unheld), unheld[:4])


def test_the_record_near_misses_and_the_stated_five_figures_stay_unread() -> None:
    """Lane CZ-A2's near-miss controls (quarters, fiscal years, versions, weeks, months, thousands parted by a space) stay unheld; five figures in all (limit (m), `MR10 000`) stays unread, as plan P4-D493 states; square brackets stay lane HX4's list."""
    import labelled_records as records

    for name, cells in records.NEAR_MISS_CONTROLS.items():
        column = (cells * (_RECORD_ROWS // len(cells) + 1))[:_RECORD_ROWS]
        assert not records.held_by_a_reader(column, False), name
    from synthtwin import asking

    assert asking._record_number_groups("MR10 000") is None and asking._record_number_groups("MR100 00") is None
    assert asking._record_number_groups("[MR100 0013]") is None
    assert asking._record_number_groups("MR-100  0013") == ("MR-", "100", "0013")


# -- (5) TELEPHONE MARKS, A MARK THAT PRINTS NOTHING, AGE NAMES ---------------------------------
def test_telephone_groups_parted_by_a_spaced_point_or_a_low_line_are_read() -> None:
    """Item 5: `319 . 555 . 0123` and `319_555_0123`, in every frame; the base read none of 900."""
    draw = random.Random(residual.SEED + 1)
    missed = []
    for case in range(400):
        area = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        exchange = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        line = f"{draw.randrange(10000):04d}"
        mark = (" . ", "_")[case % 2]
        text = ("call {}", "cb {} re results", "{}", "son {} after 5")[(case // 2) % 4].format(
            f"{area}{mark}{exchange}{mark}{line}")
        if taxonomy.identifier_words_form(text) != taxonomy.WORDS_TELEPHONE:
            missed += [text]
    assert not missed, missed[:4]


_PRINTS_NOTHING = ("​", "‌", "‍", "⁠", "﻿", "­", "‎", "‏")


def test_a_mark_that_prints_nothing_inside_a_run_of_figures_is_read_through() -> None:
    """Item 5: every character of the one definition that prints nothing, at every place inside a run of eight figures, in four frames; the base read 324 of 800."""
    draw = random.Random(residual.SEED + 2)
    missed = []
    for case in range(800):
        figures = f"{10000000 + draw.randrange(90000000)}"
        cut = 1 + case % 7
        text = ("ref {} on file", "acct {}", "chart no {} noted", "call {}")[(case // 8) % 4].format(
            figures[:cut] + _PRINTS_NOTHING[case % len(_PRINTS_NOTHING)] + figures[cut:])
        if not taxonomy.identifier_words_form(text):
            missed += [text]
    assert not missed, [repr(text) for text in missed[:4]]
    assert all(taxonomy._prints_nothing(character) for character in _PRINTS_NOTHING)


@pytest.mark.parametrize(("name", "aged"), [
    ("agecls", True), ("AGECLS", True), ("ptagegrp", True), ("PTAGEGRP", True), ("ptage", True), ("subjagegrp", True),
    ("agedecade", True), ("ptage_grp", True), ("mbrage", True), ("clientage", True), ("childage", True),
    ("stage", False), ("page", False), ("usage", False), ("dosage", False), ("voltage", False), ("postage", False),
    ("package", False), ("stagegrp", False), ("ptpage", False), ("average", False), ("agent", False), ("agenda", False),
])
def test_the_age_names_after_a_person_s_word_or_before_cls_or_decade(name: str, aged: bool) -> None:
    """Item 5: the age names the base left unread (7 of the planner's 26) are read; words that end in `age` are not."""
    assert taxonomy.named_as_an_age(name) is aged


# -- (6) BANDS IN FIVE OTHER LANGUAGES (a closed list) -------------------------------------------
_ABROAD = {
    "es": ("{a}-{b} a\u00f1os", "{a} a {b} a\u00f1os", "{a} al {b}", "{a} a\u00f1os y m\u00e1s", "{a} y m\u00e1s a\u00f1os", "{a} y mas anos"),
    "pt": ("{a}-{b} anos", "{a} a {b} anos", "{a} anos ou mais", "{a} anos e mais"),
    "fr": ("{a} \u00e0 {b} ans", "{a}-{b} ans", "{a} ans et plus", "{a} ans ou plus"),
    "de": ("{a}-{b} Jahre", "{a} bis {b} Jahre", "{a} Jahre und \u00e4lter", "{a} Jahre und mehr", "{a} Jahre und aelter"),
    "it": ("{a}-{b} anni", "{a} a {b} anni", "{a} anni e oltre", "{a} anni e pi\u00f9", "{a} anni e piu"),
}


def test_every_band_of_the_five_languages_is_read_with_its_ages() -> None:
    """Item 6: each language's closed bands (every join and unit word of the closed list) and open tops (every open word, the unit word before it or after it) read their ages, at every first age from 0 to 120."""
    missed = []
    for spellings in _ABROAD.values():
        for written in spellings:
            for first in range(0, 121, 5):
                text = written.format(a=first, b=first + 4)
                band = taxonomy.an_age_band(text)
                expected = (first, first + 4) if "{b}" in written else (first, -1)
                if band is None or (band.start, band.end) != expected:
                    missed += [text]
    assert not missed, missed[:6]


def test_age_groups_in_the_five_languages_are_reached_and_pooled() -> None:
    """Item 6 (the planner's table: each language's scheme published two bands past 89, 4,040 twin cells): each scheme under a neutral name is reached, one category past 89 left by the independent reading."""
    for spellings in _ABROAD.values():
        closed = [written for written in spellings if "{b}" in written][0]
        opened = [written for written in spellings if "{b}" not in written][0]
        labels = [closed.format(a=low, b=high) for low, high in ((25, 44), (45, 64), (65, 89), (90, 94))]
        cells = _measure_cells(labels + [opened.format(a=95)], False)
        assert _reached(cells), labels
        assert len([label for label in set(taxonomy.top_coded_cells(cells)) if readers.label_reaches_90(label)]) == 1


@pytest.mark.parametrize("text", ["1 \u00e0 2 fois par jour", "10 a 20 mg", "90 a day", "ans 90", "95 ans", "2 bis 3 Tabletten"])
def test_the_language_near_misses_are_no_band(text: str) -> None:
    """A dose's range with a unit no age is written in, a word between, a unit word before the age: no band."""
    assert taxonomy.an_age_band(text) is None


# -- (8) PRICED FIRST, BUILT AT NO FALSE ALARM: degrees, minutes and seconds; `IP` glued; a float's code
def test_a_pair_in_degrees_minutes_and_seconds_is_read() -> None:
    """Item 8: a latitude and a longitude in degrees, minutes and seconds with their letters, the seconds whole, with decimals or left out, spaces anywhere, a comma or a semicolon between, in a cell and among words; an angle with no letter, a single part, two latitudes, a latitude past 90 and minutes past 59 are no pair."""
    draw = random.Random(residual.SEED + 3)
    missed = []
    for case in range(600):
        lat, lon = draw.randint(0, 89), draw.randint(0, 179)
        minutes = (draw.randint(0, 59), draw.randint(0, 59))
        seconds = ("", "")
        if case % 3 == 1:
            seconds = (f"{draw.randint(0, 59):02d}\"", f"{draw.randint(0, 59):02d}\"")
        elif case % 3 == 2:
            seconds = (f"{draw.randint(0, 59):02d}.{draw.randint(0, 9)}\"", f"{draw.randint(0, 59):02d}.{draw.randint(0, 9)}\"")
        gap = (" ", "", ", ", "; ")[case % 4]
        spaced = case % 5 == 0
        parts = []
        for degrees, minute, second, letter in ((lat, minutes[0], seconds[0], "NS"[case % 2]), (lon, minutes[1], seconds[1], "EW"[case % 2])):
            parts += [f"{degrees}\u00b0 {minute:02d}' {second} {letter}" if spaced else f"{degrees}\u00b0{minute:02d}'{second}{letter}"]
        text = parts[0] + (gap or " ") + parts[1]
        if not taxonomy.a_coordinate_pair(text) or not taxonomy.identifier_words_form("home " + text):
            missed += [text]
    assert not missed, missed[:4]
    for text in ("flexion 45\u00b030' extension 10\u00b0", "angle 12\u00b030'15\" N", "41\u00b046'02\"N 42\u00b035'36\"N",
                 "95\u00b046'02\"N 86\u00b035'36\"W", "41\u00b066'02\"N 86\u00b035'36\"W", "temp 98.6\u00b0 F"):
        assert not taxonomy.a_coordinate_pair(text) and not taxonomy.identifier_words_form("loc " + text), text


@pytest.mark.parametrize(("text", "read"), [
    ("IP192.0.2.17", True), ("ip10.20.30.40 login", True), ("seen from IP192.0.2.17 today", True),
    ("VIP1.2.3.4", False), ("tip1.2.3.4", False), ("v1.2.3.4", False), ("ip1.2.3", False), ("IPv4 only", False),
])
def test_an_address_glued_to_ip_is_read_and_to_other_letters_is_not(text: str, read: bool) -> None:
    """Item 8: a dotted address glued to `IP`, in any case, is a network address among words; glued to other letters (a version, `v1.2.3.4`) it is none."""
    assert (taxonomy.identifier_words_form(text) == taxonomy.WORDS_NETWORK_ADDRESS) is read


def test_an_area_code_written_as_a_float_is_read_as_its_figures() -> None:
    """Item 8: a tract or block-group code a spreadsheet wrote as a float (`17031010100.0`) is read as its figures are; a provider's number or ten figures of state 1 so written stay none, as their figures do."""
    assert taxonomy.an_area_code("17031010100.0") and taxonomy.an_area_code("170310101001.0")
    assert taxonomy.an_area_code("6037201000.0") and taxonomy._value_forms_of_a_cell("17031010100.0") == 4
    assert not taxonomy.an_area_code("1234567890.0") and not taxonomy.an_area_code("17031010100.00")


def test_the_cell_forms_pre_checks_and_the_remark_ceiling() -> None:
    """Skeptic 1's item 3, each pinned (RED where the pre-check or the ceiling is dropped): a pair in degrees with no point is a pair of the cell forms (the degree mark's pre-check), a hardware address parted by soft hyphens is an address of them (the soft hyphen's pre-check), and an age past 125 in a remark is none while 125 is one."""
    assert taxonomy._value_forms_of_a_cell("41°46'02\"N 86°35'36\"W") & 2
    assert taxonomy._value_forms_of_a_cell("00\xad1a\xad2b\xad3c\xad4d\xad5e") & 1
    assert taxonomy.identifier_words_form("age 130 per chart") == ""
    assert taxonomy.identifier_words_form("age 125 per chart") == taxonomy.WORDS_AGE_PAST_89


# -- THE MARKS (LANE CZ-G RULINGS 3): the lane's readers over the owed marks and positions --------
# The 31 spaces and format characters of the owed list, the ten dashes other
# than `-`, and the soft hyphen, written out here (never read from the
# product's definition); the spaces among them a display draws as nothing.
OWED_SPACES = (
    "\t\n\r\x0c\x0b\x85\xa0            "
    "​‌‍‎‏    ⁠　﻿"
)
INVISIBLE = "​‌‍‎‏⁠﻿"
OWED_DASHES = "‐‑‒–—―−﹘﹣－"
SOFT_HYPHEN = "­"
# The owed positions against the first ordinary space (or dash) of a cell, or
# every one, or the cell's ends; and, beyond the owed list, inside the first
# word (priced: LANE CZ-G RULINGS 3 (2)).
SPACE_POSITIONS = ("all", "first", "doubled", "before", "after")
DASH_POSITIONS = ("all", "first", "doubled")
END_POSITIONS = ("leading", "trailing")


# ...the horizontal bar and the small em dash, which the identifier words also
# read as written (batch 4s's merge, step 9: `seen by<U+2015>Lanezon, A`, a word
# joined to a family name), so a remark opening with one may read where its
# control does not: the base's reading, kept apart from the false alarms.
DASHES_READ_AS_WRITTEN = "\u2015\ufe58"


def _controls(mark: str) -> "tuple[str, ...]":
    """The ordinary marks a mark is read as: a space; a space or nothing where it prints nothing; `-` for a dash; a space, nothing or `-` for the soft hyphen."""
    if mark == SOFT_HYPHEN:
        return (" ", "", "-")
    if mark in OWED_DASHES:
        return ("-",)
    return (" ", "") if mark in INVISIBLE else (" ",)


def _placed(cell: str, target: str, mark: str, position: str) -> "str | None":
    """``cell`` with ``mark`` placed at ``position`` against its first ``target`` (every one, for `all`), at an end, or inside its first word (after the first character of its first run of two letters or figures or more); None where the position finds no place."""
    if position == "leading":
        return mark + cell
    if position == "trailing":
        return cell + mark
    if position == "inside":
        for place in range(len(cell) - 1):
            if cell[place].isalnum() and cell[place + 1].isalnum():
                return cell[: place + 1] + mark + cell[place + 1:]
        return None
    at = cell.find(target)
    if at < 0:
        return None
    if position == "all":
        return cell.replace(target, mark)
    if position == "first":
        return cell[:at] + mark + cell[at + 1:]
    if position == "doubled":
        return cell[:at] + mark + mark + cell[at + 1:]
    if position == "before":
        return cell[:at] + mark + cell[at:]
    return cell[: at + 1] + mark + cell[at + 1:]


def _variants(cell: str) -> "list[tuple[str, str, str, list[str]]]":
    """Every variant of a cell over the marks and positions: (mark, position, variant, its controls)."""
    found: "list[tuple[str, str, str, list[str]]]" = []
    for mark in OWED_SPACES + OWED_DASHES + SOFT_HYPHEN:
        placings: "list[tuple[str, str]]" = []
        if mark in OWED_SPACES or mark == SOFT_HYPHEN:
            placings += [(" ", position) for position in SPACE_POSITIONS]
        if mark in OWED_DASHES or mark == SOFT_HYPHEN:
            placings += [("-", position) for position in DASH_POSITIONS]
        placings += [("", position) for position in END_POSITIONS]
        if mark in INVISIBLE or mark == SOFT_HYPHEN:
            placings += [("", "inside")]
        for target, position in placings:
            variant = _placed(cell, target, mark, position)
            if variant is None or variant == cell:
                continue
            controls = [_placed(cell, target, ordinary, position) for ordinary in _controls(mark)]
            found += [(mark, position, variant, [control for control in controls if control is not None])]
    return found


def _groups(cell: str) -> bool:
    """Item 4's reader with the labelled record number's (`_a_whole_number_after_letters`), which reads a cell whose groups a mark that prints nothing joins (`MR1000013`, batch 4s's merge, step 7)."""
    from synthtwin import asking

    return asking._record_number_groups(cell) is not None or asking._a_whole_number_after_letters(cell) is not None


# Each reader of the lane (item 4's with lane CZ-A2's labelled record
# number), a family of cells each reads written with ordinary marks, and
# near misses it reads in no control (each must stay unread in every variant).
MARK_READERS = {
    "band": (lambda cell: taxonomy.a_band_cell(cell) is not None, (
        "90-94", "90 - 94", "90 to 94", "90 to 94 years", "90-94 yrs", "95 and over", "100 and older", ">= 95 yrs",
        "Age 90-94", "age 95+", "[90, 95)", "90-<95", "90 to <95", "18-44 yrs", "95 años y más", "90 bis 94",
    ), ("100-199", "5-84 pct", "9 to 5 shift", "page 90 of 94")),
    "pair": (taxonomy.a_coordinate_pair, (
        "41.66123,-91.53210", "41.66123, -91.53210", "41.66123 -91.53210", "(41.66123, -91.53210)",
        "POINT(-91.53210 41.66123)", "N41.66123 W91.53210", "41.78396 N 86.5934 W", "N 41.78396 W 86.5934",
    ), ("12.5 13.75", "SG 1.012 1.025", "41.66123 95.1234 N", "1.234 2.345 3.456")),
    "address": (taxonomy.a_network_address, (
        "192.0.2.17", "198.51.100.7/24", "10.20.30.40:8080", "2001:db8::17", "00:1a:2b:3c:4d:5e", "00-1a-2b-3c-4d-5e",
    ), ("1.2.3", "v1.2.3.4 beta", "12:30:45", "300.1.2.3")),
    "serial": (taxonomy.a_serial_number, ("KX40291847", "Q7-4029-18", "AB-1234-5678", "40291847K"), (
        "ab-1234-5678", "KX 4029", "12345678", "Q7-40")),
    "area": (taxonomy.an_area_code, ("17031010100", "170310101001", "06037201000"), ("1234567890", "12345")),
    "words": (lambda cell: bool(taxonomy.identifier_words_form(cell)), (
        "call 319 555 0123 re results", "cb 319-555-0123 after 5", "call +44 20 7946 0958 today",
        "ref 44712093 on file", "login from 192.0.2.17 today", "home 41.66123,-91.53210 noted",
        "home 41.78396 N 86.5934 W noted", "seen by Dr Kukun today", "Lanezon, A seen today",
        "son Kukun Velegin called", "94 yo F, fall at home", "pt aged 97 lives alone",
    ), ("doing well today", "pain 9 of 10 today", "room 95 bed 2", "BP 120 over 80", "aged 45 lives alone")),
    "groups": (_groups, ("MR100 0013", "MR100  0013", "MR-100 0013", "(MR100 0013)", "AB1234 5678"), (
        "Q3 2024", "v10 12", "MR10 001", "MR1 000013")),
}


def marks_sweep(readers_of: "dict[str, tuple[object, tuple[str, ...], tuple[str, ...]]]") -> "dict[str, list[str]]":
    """The sweep: each reader's family and near misses through every variant (`_variants`); a MISS is a variant the reader reads in no reading where it reads a control, in the owed positions or inside the first word; a FALSE ALARM a variant it reads where it reads no control; and the family cells and near misses it reads otherwise than written."""
    found: "dict[str, list[str]]" = {"owed": [], "inside": [], "false_alarms": [], "as_written": [], "family": [], "variants": []}
    for name, (read, family, near) in readers_of.items():
        for cell, expected in [(cell, True) for cell in family] + [(cell, False) for cell in near]:
            if bool(read(cell)) is not expected:  # type: ignore[operator]
                found["family"] += [f"{name}: {cell!r}"]
            for mark, position, variant, controls in _variants(cell):
                found["variants"] += [name]
                controlled = any(read(control) for control in controls)  # type: ignore[operator]
                read_now = bool(read(variant))  # type: ignore[operator]
                where = "inside" if position == "inside" else "owed"
                if controlled and not read_now:
                    found[where] += [f"{name} {position} U+{ord(mark):04X}: {variant!r}"]
                if read_now and not controlled:
                    alarm = "as_written" if name == "words" and mark in DASHES_READ_AS_WRITTEN else "false_alarms"
                    found[alarm] += [f"{name} {position} U+{ord(mark):04X}: {variant!r}"]
    return found


def test_every_reader_reads_every_owed_mark_in_every_position_as_its_control() -> None:
    """LANE CZ-G RULINGS 3 (1) to (3): each reader's family over the 31 spaces and format characters, the ten dashes and the soft hyphen, in every owed position against its control written with the ordinary mark: no miss, and none inside the first word either (the class priced first: closed at no false alarm); no variant read where no control is read; the soft hyphen read as the dash of a band (`90<U+00AD>94`, X1), a serial's and an address's dash, and a character that prints nothing beside the space before a band's unit read through."""
    found = marks_sweep(MARK_READERS)
    assert found["family"] == [], found["family"]
    assert len(found["variants"]) > 15000
    assert found["owed"] == [], (len(found["owed"]), found["owed"][:6])
    assert found["inside"] == [], (len(found["inside"]), found["inside"][:6])
    assert found["false_alarms"] == [], (len(found["false_alarms"]), found["false_alarms"][:6])


def test_the_marks_sweep_is_red_without_the_further_readings(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS: with no further reading of a cell (`taxonomy._marks_readings`) the soft hyphen standing for a band's dash is missed (X1); with the two-groups reader's ends set aside as the base set them aside (no tab), two groups after a tab are missed."""
    from synthtwin import asking

    monkeypatch.setattr(taxonomy, "_marks_readings", lambda text: ())
    found = marks_sweep({"band": MARK_READERS["band"]})
    assert any("U+00AD: '90\\xad94'" in miss for miss in found["owed"]), found["owed"][:4]
    monkeypatch.undo()
    monkeypatch.setattr(asking, "_edges_and_tabs_set_aside", asking._edges_set_aside)
    found = marks_sweep({"groups": MARK_READERS["groups"]})
    assert any("leading U+0009: '\\tMR100 0013'" in miss for miss in found["owed"]), found["owed"][:4]


# -- ONE 20,000-row case through the commands ---------------------------------------------------
def test_the_lettered_homes_at_the_floor_publish_no_home(tmp_path: "object") -> None:
    """THE TABLE AT THE OWNER'S FLOOR (20,000 rows, 1,000 people's homes on 20 rows each, one row a case), unanswered: each lettered form is held with the Safe Harbor question, no home shown and no twin cell equal to one, where the base published 1,000 homes and wrote 20,000 equal twin cells."""
    import pathlib

    with residual.registered():
        seen = readers.measure(pathlib.Path(f"{tmp_path}") / "homes", residual.KIND_LETTERED_HOMES, 20000)
    assert (seen["profile"], seen["generate"]) == (0, 0)
    for column in residual.HELD[residual.KIND_LETTERED_HOMES]:
        entry = seen["columns"][column]  # type: ignore[index]
        assert entry["asked"], column
        for form in entry["forms"].values():
            assert (form["shown"], form["twin_equal"]) == (0, 0), (column, form)
