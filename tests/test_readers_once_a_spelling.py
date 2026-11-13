"""Lane PRT-a: the describe's readers asked once a spelling (plan P4-D468).

Lane PRT-0 profiled the describe function by function at 200,000 rows
(planning-notes/work-2026-10/wave6/PRT-0-build.md): it made 520 to 838
Python calls per present cell although 80 to 97 per cent of the cells
repeat a spelling met before. Three of its proposals are built here,
every byte the describe writes and prints kept:

* A, THE MISSING WORDS: the seventeen folded members of
  `parsing.MISSING_TEXTS` are a constant made once (`is_missing_text`
  folded them all again for every cell), `_declared_spelling` folds no
  cell where nothing is declared, and `split_missing` asks
  `_missing_class` once a different spelling of its call;
* B, THE NUMBER READERS: the form, the core, the mark, the whole figures
  and the width after the point are held by the tally for the column's
  whole reading, keyed by the text each reads (`_Cells.read_once`), and
  the Safe Harbor walks and the questions' key walks read a spelling
  once, every memo bounded as lane S4d bounds one
  (`parsing.memo_takes`, with its note of texts met once), and the memo
  the census walks share never past the bound and
  `taxonomy._SHARED_MEMO_NOTES` notes, at any number of rows (the lane's
  repair 2, on Codex's review);
* P WITH C, THE DATE TRIALS: `_remainder_reading` answers None at once
  for a column none of whose cells writes 1900 or 9999 (every reading the
  pass can try is classed below by how it reads its year, so a new one
  fails until it is classed), and each walk asks a format once a
  spelling.

What is pinned: each answer is the reader's own; with every memo switched
off (`parsing.memo_takes` and `parsing.memo_notes` answering False, and
`parsing.SPELLING_MEMO_TEXTS` 0, so the memo the census walks share takes
nothing either) and the placeholder pass entered for every column, the
same describe writes and prints the same bytes; each walk's memo lives for
its own call and format, checked against the readers asked one by one;
each gate is red on its mutant.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import pathlib
import random
import typing

import pytest

from synthtwin import asking, cli, parsing, taxonomy

_SETTINGS = taxonomy.Settings()


def _memo_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every memo of one answer per spelling off, the census walks' shared memo too, and the placeholder pass entered for every column.

    A memo of one pass asks `parsing.memo_takes` and its note
    `parsing.memo_notes`; the memo the census walks share
    (`taxonomy._held_again`) reads the bound `parsing.SPELLING_MEMO_TEXTS`
    itself, so the bound is set to 0 here as well: with the note refusing
    every text, that memo takes nothing (skeptic 1 of lane PRT-a, item 1).
    """
    monkeypatch.setattr(parsing, "memo_takes", lambda held, answered: False)
    monkeypatch.setattr(parsing, "memo_notes", lambda noted: False)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 0)
    monkeypatch.setattr(taxonomy, "_writes_a_placeholder_year", lambda present: True)


def _small_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """The memos' bound and note made small, so a short column runs past both."""
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 4)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 2)


# -- A: the missing words ---------------------------------------------------------


def _folded_one_by_one(text: str) -> bool:
    """`is_missing_text` as it was before lane PRT-a: every member folded again for each cell."""
    if not isinstance(text, str):
        raise TypeError("not text")
    if text in parsing.MISSING_TEXTS_EXACT:
        return True
    body = parsing.folded(text)
    for member in parsing.MISSING_TEXTS:
        if body == parsing.folded(member):
            return True
    return False


_SPELLINGS: "list[str]" = []
for _member in parsing.MISSING_TEXTS:
    _SPELLINGS += [_member, _member.upper(), _member.title(), f"  {_member}\t", _member + "x", "x" + _member]
_SPELLINGS += [
    "NaT", "nat", " NaT", "NaT ", "NAT", "Nan", "NAN", " n/A ", "N.A.", "unknown", "missing", "0", "-0",
    "", " ", " ", "　NA", "ＮＡ", "#n/a", "#N/A ", "#Value!", "nULL", "İ", "ß", "ss",
]


def _every_member_is_no_value(missing: "typing.Callable[[str], bool]") -> bool:
    """Whether a reader of the vocabulary reads every member, in any case and spacing, and `NaT` only as written."""
    for member in parsing.MISSING_TEXTS:
        for spelling in (member, member.upper(), f" {member} "):
            if not missing(spelling):
                return False
    return missing("NaT") and not missing("nat") and not missing(" NaT")


def test_the_vocabulary_is_folded_once_and_answers_as_the_loop_did() -> None:
    assert len(parsing.MISSING_TEXTS) == 17
    assert parsing._FOLDED_MISSING_TEXTS == frozenset(parsing.folded(member) for member in parsing.MISSING_TEXTS)
    assert "nat" not in parsing._FOLDED_MISSING_TEXTS
    for spelling in _SPELLINGS:
        assert parsing.is_missing_text(spelling) == _folded_one_by_one(spelling), spelling
    with pytest.raises(TypeError):
        parsing.is_missing_text(None)  # type: ignore[arg-type]
    assert _every_member_is_no_value(parsing.is_missing_text)


def test_the_vocabulary_check_is_red_on_a_set_that_drops_a_member(monkeypatch: pytest.MonkeyPatch) -> None:
    whole = parsing._FOLDED_MISSING_TEXTS
    for member in parsing.MISSING_TEXTS:
        monkeypatch.setattr(parsing, "_FOLDED_MISSING_TEXTS", whole - {parsing.folded(member)})
        assert not _every_member_is_no_value(parsing.is_missing_text), member
    monkeypatch.setattr(parsing, "_FOLDED_MISSING_TEXTS", whole | {"nat"})
    assert not _every_member_is_no_value(parsing.is_missing_text)


def _split_one_by_one(values: "list[str]", settings: taxonomy.Settings, comma: bool) -> "tuple[list[str], list[tuple[str, str]]]":
    """`split_missing` as it was before lane PRT-a: `_missing_class` asked of every row."""
    kept = taxonomy._declarations(settings.kept_values, comma)
    declared = taxonomy._declarations(settings.declared_missing_values, comma)
    present: "list[str]" = []
    missing: "list[tuple[str, str]]" = []
    for value in values:
        named = taxonomy._missing_class(value, kept, declared)
        if named:
            missing += [(value, named)]
        else:
            present += [value]
    return present, missing


_DECLARED = taxonomy.Settings(kept_values=("nat", "NA"), declared_missing_values=("UNKNOWN", "-999", "1,5", "NaT "))
_COLUMN_WORDS = [
    "NaT", "nat", "NA", "na", " N/A ", "", " ", "UNKNOWN", "unknown", "-999", "-999.0", "(999)", "1,5", "1.5",
    "12", "x", "#N/A", "null", " none", "NaN", "?", "--", "1,234", "abc ", " ",
]


def _words(rows: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [draw.choice(_COLUMN_WORDS) for _ in range(rows)]


@pytest.mark.parametrize("settings", [_SETTINGS, _DECLARED])
@pytest.mark.parametrize("comma", [False, True])
def test_split_missing_asks_once_a_spelling_and_answers_as_every_row_did(
    settings: taxonomy.Settings, comma: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    values = _words(3_000, 7) + [f"{n}" for n in range(40)] + _words(500, 8)
    assert taxonomy.split_missing(values, settings, comma) == _split_one_by_one(values, settings, comma)
    asked: "list[str]" = []
    original = taxonomy._missing_class

    def counted(value: str, kept: "list[object]", declared: "list[object]") -> str:
        nonlocal asked
        asked += [value]
        return original(value, kept, declared)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_missing_class", counted)
    taxonomy.split_missing(values, settings, comma)
    assert len(asked) == len(set(values))
    # Past the bound and its note, a text met again answers as before.
    _small_bound(monkeypatch)
    assert taxonomy.split_missing(values, settings, comma) == _split_one_by_one(values, settings, comma)


def test_split_missing_is_red_on_a_memo_that_never_answers_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """The once-a-spelling count is what the test above reads: with the memo off every row asks."""
    values = _words(2_000, 9)
    expected = _split_one_by_one(values, _DECLARED, False)
    asked: "list[str]" = []
    original = taxonomy._missing_class

    def counted(value: str, kept: "list[object]", declared: "list[object]") -> str:
        nonlocal asked
        asked += [value]
        return original(value, kept, declared)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_missing_class", counted)
    _memo_off(monkeypatch)
    assert taxonomy.split_missing(values, _DECLARED, False) == expected
    assert len(asked) == len(values) > len(set(values))


def test_no_cell_is_folded_where_nothing_is_declared(monkeypatch: pytest.MonkeyPatch) -> None:
    declarations = taxonomy._declarations(("na", "-999"))
    assert taxonomy._declared_spelling(" NA ", declarations) is True
    assert taxonomy._declared_spelling("nb", declarations) is False
    with pytest.raises(TypeError):
        taxonomy._declared_spelling(None, [])  # type: ignore[arg-type]

    def refused(text: str) -> str:
        raise AssertionError(f"folded {text!r}")

    monkeypatch.setattr(parsing, "folded", refused)
    assert taxonomy._declared_spelling(" NA ", []) is False
    with pytest.raises(AssertionError):
        taxonomy._declared_spelling(" NA ", declarations)


# -- B: the number readers --------------------------------------------------------


_NUMBERS = [
    "1,234.56", "(1,234.50)", "+12.5", "007", "7", "1e3", "1E3", "12 345", "−3", "3-", "0.250", "12'345.6",
    "1,234", "1.234,5", "12,25", "1.000", "-0.5", "+7", "000", "123456789012345678", "12.000", " 42 ", "1 234,56",
    "9007199254740993", "-9007199254740993", "1.5e-3", "(7)", "0", "12,345,678.9", "2 198.92",
]


def _numbers_tally(values: "list[str]", comma: bool = False) -> "taxonomy._Cells":
    return taxonomy._tally(taxonomy._classify_all(values, comma), len(values), _SETTINGS, comma)


def _written(cell: "taxonomy._Cell", comma: bool) -> str:
    return taxonomy._marks_exchanged(cell.text) if comma else cell.text


def _answers_right(cells: "taxonomy._Cells", comma: bool) -> bool:
    """Whether every memo of the tally answers each numeric cell as asking its reader again does."""
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        style = taxonomy._style_once(cells, cell)
        if style != taxonomy.numeric_style(cell.numeric_text):
            return False
        if taxonomy._core_once(cells, cell) != parsing.number_core(cell.numeric_text):
            return False
        # The width of every number cell, whatever its form (`fraction_width` answers 0 where no point is
        # written), so a memo keyed by the file's spelling shows under a declared decimal comma: `1.000`
        # writes three figures after its point to an undeclared column and is `1000` to a declared one.
        if taxonomy._width_once(cells, cell) != taxonomy.fraction_width(cell.numeric_text):
            return False
        written = _written(cell, comma)
        if taxonomy._mark_once(cells, written) != parsing.thousands_mark(written):
            return False
        if taxonomy._figures_once(cells, written) != taxonomy._whole_figures(written):
            return False
    return True


@pytest.mark.parametrize("comma", [False, True])
def test_each_number_reader_answers_as_asking_it_again(comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    draw = random.Random(3)
    values = [draw.choice(_NUMBERS) for _ in range(800)] + _NUMBERS
    cells = _numbers_tally(values, comma)
    assert _answers_right(cells, comma)
    assert _answers_right(cells, comma)  # the second walk reads what the first held
    assert len(cells.read_once.styles) == len({cell.numeric_text for cell in cells.classified if cell.kind == parsing.NUMBER})
    _small_bound(monkeypatch)
    small = _numbers_tally(values, comma)
    assert _answers_right(small, comma) and _answers_right(small, comma)


def test_the_key_carries_the_declared_comma() -> None:
    """One memo read under both declarations answers each its own: the key is the text the rules read.

    The census walks key the mark and the whole figures by the text they
    read: a declared column reads `1.234.567` as `1,234,567`, so that is
    the key its walk adds, and the file's own spelling is a key of neither
    (skeptic 1 of lane PRT-a, item 2: a mark keyed by the file's spelling
    moved no cell's grouping evidence on the 400 spellings, of 1,908
    tried, read as numbers under both declarations, so the key itself is
    what is pinned).
    """
    values = ["1,234", "12,25", "1.000", "7", "1.234,5", "1.234.567"] * 4
    undeclared = _numbers_tally(values, False)
    declared = dataclasses.replace(_numbers_tally(values, True), read_once=undeclared.read_once)
    fresh = _numbers_tally(values, True)
    censuses = [(taxonomy._group_separator(cells), taxonomy._thousands_marks(cells)) for cells in (undeclared, declared)]
    assert censuses[1] == (taxonomy._group_separator(fresh), taxonomy._thousands_marks(fresh))
    assert "1,234,567" in declared.read_once.marks and "1,234,567" in declared.read_once.figures
    assert "1.234.567" not in declared.read_once.marks and "1.234.567" not in declared.read_once.figures
    assert _answers_right(undeclared, False) and _answers_right(declared, True)
    assert "1,234" in undeclared.read_once.styles and "1.234" in undeclared.read_once.styles


def test_the_key_check_is_red_on_a_memo_keyed_by_the_files_spelling(monkeypatch: pytest.MonkeyPatch) -> None:
    def keyed_by_the_file(cells: "taxonomy._Cells", cell: "taxonomy._Cell") -> str:
        once = cells.read_once
        if cell.text in once.styles:
            return once.styles[cell.text]
        style = taxonomy.numeric_style(cell.numeric_text)
        once.styles[cell.text] = style
        return style

    monkeypatch.setattr(taxonomy, "_style_once", keyed_by_the_file)
    values = ["1,234", "12,25", "1.000", "7", "1.234,5"] * 4
    undeclared = _numbers_tally(values, False)
    declared = dataclasses.replace(_numbers_tally(values, True), read_once=undeclared.read_once)
    assert not (_answers_right(undeclared, False) and _answers_right(declared, True))


def _held_to_the_bound(cells: "taxonomy._Cells", distinct: int) -> bool:
    """After one walk over spellings that never repeat, the memo holds the bound and its note no more than the note's."""
    once = cells.read_once
    asked = once.styles_asked
    return (
        len(once.styles) == min(distinct, parsing.SPELLING_MEMO_TEXTS)
        and len(asked.noted) <= parsing.SPELLING_MEMO_NOTED
        and len(asked.older) <= parsing.SPELLING_MEMO_NOTED
    )


def test_a_column_whose_spellings_pass_the_bound_holds_the_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 8)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 3)
    values = [f"{n}.5" for n in range(100)]
    cells = _numbers_tally(values)
    tallied = taxonomy._form_tally(cells)
    assert tallied == {parsing.STYLE_DECIMAL: 100}
    assert _held_to_the_bound(cells, 100)
    # ...a spelling its note holds is taken, met again; one it does not is not.
    noted = list(cells.read_once.styles_asked.noted) + list(cells.read_once.styles_asked.older)
    assert noted and noted[0] not in cells.read_once.styles
    record = next(cell for cell in cells.classified if cell.numeric_text == noted[0])
    assert taxonomy._style_once(cells, record) == parsing.STYLE_DECIMAL
    assert noted[0] in cells.read_once.styles
    # The second walk answers every row as the first did, from what is held or asked again.
    assert taxonomy._form_tally(cells) == tallied
    assert _answers_right(cells, False)


def test_the_bound_check_is_red_on_a_memo_that_takes_every_spelling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 8)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 3)
    monkeypatch.setattr(taxonomy, "_held_again", lambda asked, held, text: True)
    values = [f"{n}.5" for n in range(100)]
    cells = _numbers_tally(values)
    taxonomy._form_tally(cells)
    assert not _held_to_the_bound(cells, 100)


def _the_cap() -> int:
    """The most texts a memo the census walks share holds: the bound and `taxonomy._SHARED_MEMO_NOTES` notes."""
    return parsing.SPELLING_MEMO_TEXTS + taxonomy._SHARED_MEMO_NOTES * parsing.SPELLING_MEMO_NOTED


def _flat_over_the_walks(walks: int) -> bool:
    """Whether the shared memo of a column whose 100 spellings never repeat holds no more than its cap after the walks."""
    cells = _numbers_tally([f"{n}.5" for n in range(100)])
    for _walk in range(walks):
        taxonomy._form_tally(cells)
    return len(cells.read_once.styles) <= _the_cap() < 100


def test_the_shared_memo_does_not_grow_with_the_walks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every walk answers every text the memo holds again, so the growth clause of a memo of one pass is not read."""
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 8)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 3)
    assert _flat_over_the_walks(10)
    # ...red on the growth clause read as a memo of one pass reads it: by the
    # fourth walk it has answered as many rows as it holds, and takes every text.
    answered = {"rows": 0}
    original = taxonomy._style_once

    def counted(cells: "taxonomy._Cells", cell: "taxonomy._Cell") -> str:
        if cell.numeric_text in cells.read_once.styles:
            answered["rows"] = answered["rows"] + 1
        return original(cells, cell)

    monkeypatch.setattr(taxonomy, "_style_once", counted)
    monkeypatch.setattr(taxonomy, "_held_again", lambda asked, held, text: parsing.memo_takes(held, answered["rows"]))
    assert not _flat_over_the_walks(10)


def _censuses(values: "list[str]", comma: bool) -> "tuple[object, ...]":
    """Every census of a numeric column that walks its cells through the tally's memo."""
    cells = _numbers_tally(values, comma)
    styles = taxonomy._numeric_styles(cells)
    return (
        taxonomy._padded_cells(cells),
        styles,
        taxonomy._numeric_styles(cells),
        taxonomy._width_censuses(cells, styles),
        taxonomy._group_separator(cells),
        taxonomy._thousands_marks(cells),
        taxonomy._decimal_plus(cells, styles),
        taxonomy._fraction_widths(cells, styles),
        taxonomy._wide_runs(cells, styles),
        taxonomy._negative_notations(cells),
    )


@pytest.mark.parametrize("seed", [1, 2])
@pytest.mark.parametrize("comma", [False, True])
def test_the_censuses_count_as_they_did_with_every_memo_off(seed: int, comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    draw = random.Random(seed)
    columns = [
        [draw.choice(_NUMBERS) for _ in range(600)],
        [f"{draw.gauss(40, 9):.{draw.choice([1, 1, 2])}f}" for _ in range(600)],
        [f"{draw.randrange(1, 10**7):,}" for _ in range(600)],
        [f"{draw.randrange(0, 999):05d}" for _ in range(600)],
        [f"{draw.randrange(10**16, 10**19)}" for _ in range(300)] + ["12"] * 300,
    ]
    on = [_censuses(values, comma) for values in columns]
    _memo_off(monkeypatch)
    assert [_censuses(values, comma) for values in columns] == on


def _pairs(spellings: int, comma: bool) -> "list[str]":
    """Codex's column: each spelling written twice in a row, `1000.00, 1000.00, 1000.01, 1000.01, ...`."""
    point = "," if comma else "."
    return [f"{1000 + n // 100}{point}{n % 100:02d}" for n in range(spellings) for _row in range(2)]


_SHARED_MEMOS = ("styles", "cores", "widths", "marks", "figures")


def _held_after_every_census_walk(values: "list[str]", comma: bool, monkeypatch: pytest.MonkeyPatch) -> "tuple[dict[str, int], int]":
    """How many texts each memo the census walks share holds after three rounds of every walk, and how often a note turned over."""
    turned = {"over": 0}
    noting = parsing.memo_notes

    def counted(noted: int) -> bool:
        room = noting(noted)
        turned["over"] = turned["over"] + (0 if room else 1)
        return room

    monkeypatch.setattr(parsing, "memo_notes", counted)
    cells = _numbers_tally(values, comma)
    for _round in range(3):
        styles = taxonomy._numeric_styles(cells)
        taxonomy._padded_cells(cells)
        taxonomy._width_censuses(cells, styles)
        taxonomy._group_separator(cells)
        taxonomy._thousands_marks(cells)
        taxonomy._decimal_plus(cells, styles)
        taxonomy._fraction_widths(cells, styles)
        taxonomy._wide_runs(cells, styles)
        taxonomy._negative_notations(cells)
    assert _answers_right(cells, comma)
    return ({name: len(getattr(cells.read_once, name)) for name in _SHARED_MEMOS}, turned["over"])


def _held_without_a_cap(asked: "taxonomy._Asked", held: int, text: str) -> bool:
    """`taxonomy._held_again` as the lane's build wrote it, before its cap: past the bound the note's admissions had none."""
    if text in asked.noted or text in asked.older:
        return True
    if held < parsing.SPELLING_MEMO_TEXTS:
        return True
    if parsing.memo_notes(len(asked.noted)):
        asked.noted[text] = True
    else:
        asked.older = asked.noted
        asked.noted = {}
    return False


@pytest.mark.parametrize("comma", [False, True])
def test_spellings_met_twice_in_a_row_fill_the_shared_memo_to_its_cap_and_no_further(comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review of lane PRT-a, item 1 (LANE PRT-a RULINGS 4 (2)).

    Past the bound the shared memo takes a text its note holds when it is
    met again, and a column writing each spelling twice in a row meets
    every spelling again while the note holds it: each of the five memos
    took every spelling, 499,947 texts at 1,000,000 rows, growing with the
    rows. At the shipped sizes the cap is 229,376 texts a memo, the number
    the plan decision's bytes are measured at. At a bound of 4 and a note
    of 2, a cap of 44 texts, 150 spellings written twice in a row turn the
    notes over again and again through three rounds of every census walk,
    the declared decimal comma's readings included, and each of the five
    memos fills to the cap and no further, each reader answering as asking
    it again.
    """
    assert _the_cap() == 229_376
    _small_bound(monkeypatch)
    held, turned = _held_after_every_census_walk(_pairs(150, comma), comma, monkeypatch)
    assert set(held.values()) == {_the_cap()} and _the_cap() < 150, held
    assert turned >= 10, turned


@pytest.mark.parametrize("comma", [False, True])
def test_the_cap_check_is_red_on_the_note_admitting_without_a_cap(comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    _small_bound(monkeypatch)
    monkeypatch.setattr(taxonomy, "_held_again", _held_without_a_cap)
    held, _turned = _held_after_every_census_walk(_pairs(150, comma), comma, monkeypatch)
    assert max(held.values()) > _the_cap(), held


_TALLY_READERS = (
    (taxonomy, "numeric_style"),
    (parsing, "number_core"),
    (taxonomy, "fraction_width"),
    (parsing, "thousands_mark"),
    (taxonomy, "_whole_figures"),
)


def _asked_by_the_census_walks(values: "list[str]") -> "dict[str, int]":
    """How many times two rounds of every census walk over one column ask each number reader of the tally."""
    asked = {name: 0 for _module, name in _TALLY_READERS}
    cells = _numbers_tally(values)
    with pytest.MonkeyPatch.context() as counting:
        for module, name in _TALLY_READERS:
            original = getattr(module, name)

            def counted(*arguments: typing.Any, _name: str = name, _original: typing.Any = original) -> typing.Any:
                asked[_name] = asked[_name] + 1
                return _original(*arguments)

            counting.setattr(module, name, counted)
        for _round in range(2):
            styles = taxonomy._numeric_styles(cells)
            taxonomy._padded_cells(cells)
            taxonomy._width_censuses(cells, styles)
            taxonomy._group_separator(cells)
            taxonomy._thousands_marks(cells)
            taxonomy._decimal_plus(cells, styles)
            taxonomy._fraction_widths(cells, styles)
            taxonomy._wide_runs(cells, styles)
    return asked


def test_with_every_memo_off_the_census_walks_ask_every_reader_again(monkeypatch: pytest.MonkeyPatch) -> None:
    """The memo-off comparisons above compare the readers asked again, not the shared memo with itself.

    Skeptic 1 of lane PRT-a, item 1: with only `parsing.memo_takes` and
    `parsing.memo_notes` switched off, the census walks still read the
    shared memo, which reads the bound itself, so each reader was asked
    7 times for 7 spellings either way. Red on `_memo_off` without its
    bound line.
    """
    values = [f"{place % 7 + 1},234.5" for place in range(140)]
    on = _asked_by_the_census_walks(values)
    _memo_off(monkeypatch)
    off = _asked_by_the_census_walks(values)
    for name in on:
        # ...with the memos on, once a spelling (the core is read inside the form too);
        # with every memo off, at least once a row in each of the two rounds.
        assert 0 < on[name] <= 4 * 7 and off[name] >= 2 * len(values), (name, on[name], off[name])


# -- B: the Safe Harbor walks and the questions' key walks -----------------------------


_AGES = [
    "95", "92 years", "100 y/o", "92-year-old", "999", "-1", "", "NA", "45", "089", "1100 months", "35.5", "90.00",
    "abc", "52240", "52240-1234", "1,234.00", "0123", "104Y", "006M", "+95", "130", "89.9999", "94,8", "3 d", "90",
]


def _harbor(cells: "list[str]", comma: bool) -> "tuple[object, ...]":
    absent = frozenset({"", "NA"})
    years = [f"{1900 + (len(cell) * 7) % 120}" for cell in cells]
    places = [f"{(len(cell) * 13) % 180 - 90}.{len(cell) * 4711 % 100000:05d}" for cell in cells]
    return (
        taxonomy.ages_written_with_units(cells, comma, absent),
        taxonomy.safe_harbor_reach(cells, comma, absent, 11),
        taxonomy.safe_harbor_reach(cells, comma, absent, 2, True, True, 1080, True),
        taxonomy.age_placeholders_set_aside(cells, comma, absent, 11),
        taxonomy._padded_widths(cells, comma, absent),
        taxonomy._padded_widths(cells, comma, absent, False),
        taxonomy.top_coded_cells_before_sh3(cells, comma, absent),
        taxonomy.top_coded_cells(cells, comma, absent),
        taxonomy.top_coded_cells(cells, comma, absent, 1080),
        taxonomy.top_category_pooled(cells, comma, absent, 11),
        taxonomy.top_category_pooled(cells, comma, absent, 10_000, 1080),
        taxonomy.top_category_pooled(cells, comma, absent, 3, 90, [[f"p{place % 4}" for place in range(len(cells))]]),
        taxonomy._year_census(years, comma, absent, 11, 2027),
        taxonomy.year_top_coded_cells(years, comma, absent, 1937),
        taxonomy.coordinate_reading(places, comma, absent),
    )


@pytest.mark.parametrize("comma", [False, True])
def test_the_safe_harbor_walks_read_as_they_did_with_every_memo_off(comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    draw = random.Random(5)
    cells = [draw.choice(_AGES) for _ in range(1_500)] + [f"{draw.randrange(18, 105)}" for _ in range(1_500)]
    on = _harbor(cells, comma)
    _small_bound(monkeypatch)
    assert _harbor(cells, comma) == on
    _memo_off(monkeypatch)
    assert _harbor(cells, comma) == on


def test_the_pooled_top_category_reads_a_spelling_once(monkeypatch: pytest.MonkeyPatch) -> None:
    cells = ["95", "40", "92 years", "", "88"] * 400
    read: "list[str]" = []
    original = taxonomy.safe_harbor_number

    def counted(
        cell: str, comma: bool = False, affixes: bool = True, words: bool = False
    ) -> "taxonomy.SafeHarborNumber | None":
        nonlocal read
        read += [cell]
        return original(cell, comma, affixes, words)

    monkeypatch.setattr(taxonomy, "safe_harbor_number", counted)
    taxonomy.top_category_pooled(cells, False, frozenset({""}), 11)
    assert sorted(read) == sorted(set(cells) - {""})


_KEYS = [
    "100001", "-300001", "+300001", "00123", "123", "RPT000001", "ABC-12345", "A12-345678", "99999", "0", "-99",
    "UNKNOWN", "1,234,567", "123 456 789", "123.456.789", "100001.0", "41.3", "-0", "+", "-", "12a", "1.5",
]


def _key_walks(present: "list[str]", comma: bool) -> "tuple[object, ...]":
    return (
        asking._each_on_one_row_arm(present, comma),
        asking._each_on_one_row_arm(present, comma, "row_id"),
        asking._each_on_one_row_arm(present, comma, "", True),
        asking._a_key_of_figures_repeating(present),
        asking._a_key_of_figures_repeating(present, True),
    )


def _key_reading_one_by_one(
    value: str, comma: bool, affixed: bool = False
) -> "tuple[tuple[str, str, str], bool] | None":
    """The arm's reading of one value as it was written inline before lane PRT-a.

    With lane ID-ROOM2's reading between an affixed number's affixes
    (``affixed``, plan P4-D457), which the arm read inline on the
    integration line when batch 4r merged lane PRT-a.
    """
    figures: "str | None" = None
    opening = ""
    closing = ""
    if not comma or ("," not in value and "." not in value):
        figures = asking._key_figures(value)
        if figures is None and value[:1] in asking._SIGNS:
            figures = asking._key_figures(value[1:])
            if figures is not None and value[:1] == "-":
                opening = "-"
    if figures is None:
        lettered = asking._a_whole_number_after_letters(value)
        if lettered is None and affixed:
            lettered = asking._a_whole_number_between_affixes(value, comma)
        if lettered is None:
            return None
        opening, figures, closing = lettered
    return (opening, asking._without_leading_noughts(figures), closing), len(figures) >= asking._PREFIXED_FIGURES_AT_LEAST


@pytest.mark.parametrize("comma", [False, True])
def test_the_key_walks_read_as_they_did_with_every_memo_off(comma: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    for value in _KEYS + ["P200000Q4444", "ACC123456-2024", "12345mg"]:
        for affixed in (False, True):
            assert asking._key_reading(value, comma, affixed) == _key_reading_one_by_one(value, comma, affixed), value
    draw = random.Random(6)
    columns = [
        [draw.choice(_KEYS) for _ in range(2_000)],
        [f"{draw.randrange(10**5, 10**5 + 300)}" for _ in range(2_000)],
        [f"P{draw.randrange(1, 400):06d}" for _ in range(2_000)],
        [f"{draw.randrange(1, 400):06d}" for _ in range(1_990)] + ["UNKNOWN"] * 10,
        [f"P{draw.randrange(200_000, 200_300)}Q4444" for _ in range(2_000)],
    ]
    on = [_key_walks(present, comma) for present in columns]
    _small_bound(monkeypatch)
    assert [_key_walks(present, comma) for present in columns] == on
    _memo_off(monkeypatch)
    assert [_key_walks(present, comma) for present in columns] == on


def test_each_key_walk_reads_its_spellings_in_its_own_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """A key walk's memo lives for its own call, and so does the declaration it reads under.

    Skeptic 1 of lane PRT-a, item 2 (b): a memo that outlived its call
    would answer a later call from an earlier one's readings, whatever
    the comma each declared, and an answer with the memo off would read
    it too. So the arm and route four walk the same columns with no
    decimal comma declared and then with one: each call reads every
    spelling it meets itself, once, and each reading is the one-by-one
    reading under that call's declaration; the grouped keys are keys
    with no comma declared and strays with one, and the arm answers so.
    The arm stops reading once more than one present cell in a hundred
    is read by no arm (lane ID-ROOM2's stop, plan P4-D457, met at batch
    4r's merge): each call reads the spellings in the column's order up
    to where its own strays stop it, so the call that stops first has
    read, itself, the first of the spellings the other read, and the
    grouped keys with the comma declared stop it at their fourth row.
    """
    draw = random.Random(29)
    grouped = [f"{draw.randrange(100_000, 1_000_000):,}" for _ in range(300)]
    mixed = [draw.choice(_KEYS) for _ in range(2_000)] + [f"{draw.randrange(10**5, 10**5 + 300)}" for _ in range(2_000)]
    readings: "list[tuple[str, bool]]" = []
    figured: "list[str]" = []
    reading_original = asking._key_reading
    figures_original = asking._key_figures

    def reading(
        value: str, comma: bool, affixed: bool = False, present: "list[str] | None" = None,
        held: "dict[str, bool] | None" = None,
    ) -> "tuple[tuple[str, str, str], bool] | None":
        nonlocal readings
        readings += [(value, comma)]
        found = reading_original(value, comma, affixed, present, held)
        assert found == _key_reading_one_by_one(value, comma, affixed), (value, comma, affixed)
        return found

    def figures(value: str) -> "str | None":
        nonlocal figured
        figured += [value]
        return figures_original(value)

    monkeypatch.setattr(asking, "_key_reading", reading)
    for present in (grouped, mixed):
        met: "list[list[tuple[str, bool]]]" = []
        for comma in (False, True):
            readings = []
            arm = asking._each_on_one_row_arm(present, comma)
            assert readings and len(readings) == len(set(readings)), comma
            met += [[(value, comma) for value, _declared in readings]]
            assert [declared for _value, declared in readings] == [comma] * len(readings)
            if present is grouped:
                keys = [_key_reading_one_by_one(value, comma) for value in present]
                assert (arm == ("", False)) == all(key is None for key in keys), (comma, arm)
        first, second = ([value for value, _comma in one] for one in met)
        shorter, longer = sorted((first, second), key=len)
        assert shorter == longer[: len(shorter)]
        if present is grouped:
            assert first == list(dict.fromkeys(present))
            assert second == list(dict.fromkeys(present[: len(present) // asking._STRAY_SHARE + 1]))
    assert asking._each_on_one_row_arm(grouped, False)[0] != ""
    monkeypatch.setattr(asking, "_key_reading", reading_original)
    monkeypatch.setattr(asking, "_key_figures", figures)
    for present in (grouped, mixed):
        walked: "list[list[str]]" = []
        for _call in range(2):
            figured = []
            asking._a_key_of_figures_repeating(present)
            assert figured and len(figured) == len(set(figured))
            walked += [figured]
        assert walked[0] == walked[1]


def test_the_key_walks_hold_the_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each key walk's memo keeps lane S4d's bound, the memory bound of goal G4 (skeptic 1 of lane PRT-a, item 2).

    Over 100 spellings that never repeat, written twice, a walk answers
    from what it holds at most twice the bound and its note, so it reads
    the column's second half again: about 200 readings, where a memo
    taking every spelling reads 100.
    """
    _small_bound(monkeypatch)
    texts = [f"{100_000 + 7 * place}" for place in range(100)]
    column = texts + texts
    held_at_most = 2 * (parsing.SPELLING_MEMO_TEXTS + 2 * parsing.SPELLING_MEMO_NOTED)
    asked = {"_key_figures": 0, "_key_reading": 0}
    walks = (
        ("_key_figures", lambda: asking._a_key_of_figures_repeating(column)),
        ("_key_reading", lambda: asking._each_on_one_row_arm(column)),
    )
    for name, walk in walks:
        original = getattr(asking, name)

        def counted(*arguments: typing.Any, _name: str = name, _original: typing.Any = original) -> typing.Any:
            asked[_name] = asked[_name] + 1
            return _original(*arguments)

        with pytest.MonkeyPatch.context() as counting:
            counting.setattr(asking, name, counted)
            walk()
        assert len(column) - held_at_most <= asked[name] <= len(column), (name, asked[name])


# -- P with C: the date trials ----------------------------------------------------------


# HOW EACH READING THE PLACEHOLDER PASS CAN TRY READS ITS YEAR. A reading
# added to `parsing.DATE_FORMATS`, or a slashed pair, fails the first test
# below until it is classed here -- after its reader has been read for the
# one property `_remainder_reading`'s entry rests on: a day of
# `parsing.CALENDAR_PLACEHOLDERS` is denoted only by a cell writing its year.
_AS_WRITTEN = "its year's four figures exactly as the cell writes them"
_TWO_FIGURES = "a two-figure year, read 1969 to 2068"
_NO_DAY = "a month or a quarter, no day"
_YEAR_READINGS = {
    "iso-date": _AS_WRITTEN,
    "iso-datetime": _AS_WRITTEN,
    "slashed-iso-date": _AS_WRITTEN,
    "iso-month": _NO_DAY,
    "compact-date": _AS_WRITTEN,
    "month-first-date": _AS_WRITTEN,
    "day-first-date": _AS_WRITTEN,
    "textual-day-first-date": _AS_WRITTEN,
    "textual-month-first-date": _AS_WRITTEN,
    "dotted-month-first-date": _AS_WRITTEN,
    "dotted-day-first-date": _AS_WRITTEN,
    "two-digit-month-first-date": _TWO_FIGURES,
    "two-digit-day-first-date": _TWO_FIGURES,
    "dotted-two-digit-month-first-date": _TWO_FIGURES,
    "dotted-two-digit-day-first-date": _TWO_FIGURES,
    "month-first-datetime": _AS_WRITTEN,
    "day-first-datetime": _AS_WRITTEN,
    "slashed-iso-datetime": _AS_WRITTEN,
    "year-quarter": _NO_DAY,
    "iso-mixed": _AS_WRITTEN,
}
# Each placeholder day written in each reading that writes a day, the year
# shown as `{year}`.
_PLACEHOLDER_SPELLINGS = {
    "iso-date": ("{year}-01-01", "{year}-12-31"),
    "iso-datetime": ("{year}-01-01 00:00:00", "{year}-12-31T23:59:59Z", "{year}-01-01t12:00:00+05:00"),
    "slashed-iso-date": ("{year}/01/01", "{year}/12/31"),
    "compact-date": ("{year}0101", "{year}1231"),
    "month-first-date": ("01/01/{year}", "1/1/{year}", "12/31/{year}"),
    "day-first-date": ("01/01/{year}", "31/12/{year}", "1/1/{year}"),
    "textual-day-first-date": ("1 Jan {year}", "31-Dec-{year}", "01 January {year}"),
    "textual-month-first-date": ("Jan 1, {year}", "December 31, {year}"),
    "dotted-month-first-date": ("01.01.{year}", "12.31.{year}"),
    "dotted-day-first-date": ("01.01.{year}", "31.12.{year}"),
    "month-first-datetime": ("01/01/{year} 00:00", "12/31/{year} 11:59 PM"),
    "day-first-datetime": ("01/01/{year} 00:00", "31/12/{year} 23:59"),
    "slashed-iso-datetime": ("{year}/01/01 00:00", "{year}/12/31 23:59"),
    "iso-mixed": ("{year}-01-01", "{year}-12-31 00:00:00"),
}


def _readings_the_pass_tries() -> "set[str]":
    tried = set(parsing.DATE_FORMATS)
    for pair in taxonomy.SLASHED_PAIRS:
        tried |= set(pair)
    return tried


def test_every_reading_the_pass_tries_is_classed() -> None:
    assert _readings_the_pass_tries() == set(_YEAR_READINGS)
    assert set(_PLACEHOLDER_SPELLINGS) == {name for name in _YEAR_READINGS if _YEAR_READINGS[name] == _AS_WRITTEN}
    for name in _readings_the_pass_tries():
        assert not name.startswith(parsing.LAYOUT_PREFIX), name
    assert taxonomy._PLACEHOLDER_YEARS == ("1900", "9999")
    assert tuple(day[:4] for day in parsing.CALENDAR_PLACEHOLDERS) == taxonomy._PLACEHOLDER_YEARS


def test_a_placeholder_day_is_written_with_its_year_in_every_reading() -> None:
    for name, spellings in _PLACEHOLDER_SPELLINGS.items():
        # ...each reading names both placeholder days, each with its year written,
        named: "set[str]" = set()
        for shape in spellings:
            for day in parsing.CALENDAR_PLACEHOLDERS:
                spelling = shape.format(year=day[:4])
                found = parsing.placeholder_day_of(spelling, name)
                if found is not None:
                    assert found[:4] in spelling, (name, spelling)
                    named |= {found}
        assert named == set(parsing.CALENDAR_PLACEHOLDERS), name
        # ...and no day under a neighbouring year.
        for shape in spellings:
            for neighbour in ("1899", "1901", "9998", "1990", "0900", "2900"):
                assert parsing.placeholder_day_of(shape.format(year=neighbour), name) is None, (name, shape, neighbour)
    for figures in range(100):
        assert parsing.year_of_two_figures(f"{figures:02d}") not in taxonomy._PLACEHOLDER_YEARS
    for name in _YEAR_READINGS:
        if _YEAR_READINGS[name] == _TWO_FIGURES:
            dotted = name.startswith("dotted-")
            for spelling in ("01/01/00", "12/31/99", "31/12/99", "01/01/19", "01.01.00", "31.12.99", "12.31.99"):
                if ("." in spelling) == dotted:
                    assert parsing.placeholder_day_of(spelling, name) is None, (name, spelling)
        if _YEAR_READINGS[name] == _NO_DAY:
            for spelling in ("1900-01", "9999-12", "1900-Q1", "9999-Q4", "1900-q1"):
                assert parsing.placeholder_day_of(spelling, name) is None, (name, spelling)


def test_no_spelling_without_the_year_names_a_placeholder_day() -> None:
    """Mutations of every placeholder spelling, in every reading: a placeholder day found is a year written."""
    draw = random.Random(17)
    alphabet = "0123456789/-.: TZtz+,JanDecQq "
    seeds: "list[str]" = []
    for spellings in _PLACEHOLDER_SPELLINGS.values():
        for shape in spellings:
            for day in parsing.CALENDAR_PLACEHOLDERS:
                seeds += [shape.format(year=day[:4])]
    for name in _readings_the_pass_tries():
        for seed in seeds:
            for _ in range(40):
                text = seed
                for _edit in range(draw.randrange(1, 4)):
                    place = draw.randrange(len(text) + 1)
                    kind = draw.randrange(3)
                    if kind == 0 and text:
                        text = text[:place] + text[place + 1 :]
                    elif kind == 1:
                        text = text[:place] + draw.choice(alphabet) + text[place:]
                    elif text:
                        text = text[:place] + draw.choice(alphabet) + text[place + 1 :]
                if parsing.placeholder_day_of(text, name) is not None:
                    assert any(year in text for year in taxonomy._PLACEHOLDER_YEARS), (name, text)


def _remainder(present: "list[str]", day_first: bool = False) -> "str | None":
    return taxonomy._remainder_reading(present, dataclasses.replace(_SETTINGS, day_first=day_first))


def _placeholders_found() -> bool:
    """Whether the pass still reads every placeholder column it read before the entry."""
    return (
        _remainder(["2024-01-05", "2023-02-11"] * 150 + ["9999-12-31"] * 20) == "iso-date"
        and _remainder(["2024-01-05", "2023-02-11"] * 150 + ["1900-01-01"] * 20) == "iso-date"
        and _remainder(["17/03/2024", "25/12/2023"] * 150 + ["31/12/9999"] * 20) == "day-first-date"
        and _remainder(["03/17/2024 14:05", "12/25/2023 09:30"] * 150 + ["12/31/9999 00:00"] * 20)
        == "month-first-datetime"
        and _remainder(["20240105", "20230211"] * 150 + ["19000101"] * 20) == "compact-date"
    )


def test_a_column_writing_no_placeholder_year_is_answered_before_any_trial(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _placeholders_found()
    present = ["2024-01-05", "2023-12-31", "1999-07-04", "17/03/2024", "N/A", "19:00"] * 50

    def refused(text: str, format_name: str) -> object:
        raise AssertionError("a trial was run")

    monkeypatch.setattr(parsing, "placeholder_day_of", refused)
    monkeypatch.setattr(parsing, "parse_datetime", refused)
    assert _remainder(present) is None
    assert _remainder([]) is None


def test_the_entry_is_red_where_it_forgets_a_year(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_PLACEHOLDER_YEARS", ("1900",))
    assert not _placeholders_found()


def _date_walks(present: "list[str]") -> "tuple[object, ...]":
    return (
        taxonomy._reads(present, "day-first-date"),
        taxonomy._reads_within(present, "month-first-date", len(present) // 3),
        taxonomy._reads_rest(present, "iso-date", taxonomy._reads_within(present, "iso-date", 3)[0]),
        taxonomy._slashed_evidence(present, ("month-first-date", "day-first-date"), False, _SETTINGS),
        taxonomy._slashed_evidence(present, ("month-first-datetime", "day-first-datetime"), True, _SETTINGS, 40),
        taxonomy._best_date_reading(present),
        _remainder(present),
        _remainder(present, True),
        taxonomy._reads_rest(present, "day-first-date", taxonomy._reads_within(present, "day-first-date", 3)[0]),
    )


def _parsed_one_by_one(present: "list[str]", format_name: str) -> "list[bool]":
    """Which cells one reading parses, every cell asked again."""
    return [parsing.parse_datetime(value, format_name) is not None for value in present]


def _best_date_reading_one_by_one(present: "list[str]") -> "tuple[str, int]":
    """`_best_date_reading` as it was before lane PRT-a: the first format of `parsing.DATE_FORMATS` that parses the most cells, and how many."""
    best_name = parsing.DATE_FORMATS[0]
    best_count = 0
    for format_name in parsing.DATE_FORMATS:
        parsed = _parsed_one_by_one(present, format_name).count(True)
        if parsed > best_count:
            best_name = format_name
            best_count = parsed
    return best_name, best_count


def _within_one_by_one(present: "list[str]", format_name: str, room: int) -> "tuple[list[bool], bool]":
    """`_reads_within` as it was before lane PRT-a: the walk stops once more than ``room`` cells have failed."""
    answers: "list[bool]" = []
    missed = 0
    for found in _parsed_one_by_one(present, format_name):
        answers += [found]
        if not found:
            missed = missed + 1
            if missed > room:
                return answers, True
    return answers, False


def _remainder_one_by_one(present: "list[str]", settings: taxonomy.Settings) -> "str | None":
    """`_remainder_reading` as it was before lane PRT-a, with no entry test: every cell asked again under every format."""
    for format_name in parsing.DATE_FORMATS:
        reading = format_name
        for pair in taxonomy.SLASHED_PAIRS:
            if format_name != pair[0]:
                continue
            weighed = taxonomy._slashed_evidence(present, pair, settings.day_first, settings)
            if weighed is not None and (settings.day_first or weighed.day_parsed > weighed.month_parsed):
                reading = weighed.used
        remainder = [value for value in present if parsing.placeholder_day_of(value, reading) is None]
        if len(remainder) == len(present):
            continue
        needed = taxonomy._needed(settings.minimum_parse_rate, len(remainder))
        pairs: "list[tuple[str, str]]" = []
        sources: "list[str]" = []
        for value in remainder:
            found = parsing.parse_datetime(value, reading)
            if found is not None:
                pairs += [found]
                sources += [value]
        if reading in parsing.SLASHED_STAMPS and sources:
            pairs, sources, _clock = taxonomy._stamp_clocks(pairs, sources, settings)
        if len(sources) >= needed and sources:
            return reading
    return None


def _date_walks_one_by_one(present: "list[str]") -> "tuple[object, ...]":
    """What `_date_walks` reads, the slashed evidence aside, each cell asked of each format again."""
    started = _within_one_by_one(present, "iso-date", 3)[0]
    begun = _within_one_by_one(present, "day-first-date", 3)[0]
    return (
        _parsed_one_by_one(present, "day-first-date"),
        _within_one_by_one(present, "month-first-date", len(present) // 3),
        started + _parsed_one_by_one(present[len(started) :], "iso-date"),
        _best_date_reading_one_by_one(present),
        _remainder_one_by_one(present, _SETTINGS),
        _remainder_one_by_one(present, dataclasses.replace(_SETTINGS, day_first=True)),
        begun + _parsed_one_by_one(present[len(begun) :], "day-first-date"),
    )


def test_the_date_walks_read_as_they_did_with_every_memo_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each date walk's memo lives for its own call and its own format.

    The walks are read against the readers asked one by one as well as
    with every memo off (skeptic 1 of lane PRT-a, item 2 (a)): a memo
    that outlived its format or its call would answer the memo-off walk
    too, from what it already held.
    """
    draw = random.Random(11)
    days = [f"{draw.randrange(1, 29):02d}/{draw.randrange(1, 13):02d}/{draw.randrange(1990, 2025)}" for _ in range(60)]
    columns = [
        [draw.choice(days) for _ in range(1_500)] + ["31/12/9999"] * 30 + ["01/01/1900"] * 3,
        [draw.choice(days) for _ in range(1_500)],
        [f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/2024 {draw.randrange(0, 24):02d}:{draw.choice(['00', '30'])}" for _ in range(900)]
        + ["12/31/9999 00:00"] * 15,
        [draw.choice(["2024-01-05", "2023-02-11", "9999-12-31", "N/A", "2024-01-05 10:00:00"]) for _ in range(1_000)],
        # ...placeholders written two ways: the ISO reading finds its own and fails on the rest, and the
        # slashed reading after it must read the rest itself.
        [f"{draw.randrange(1, 13):02d}/{draw.randrange(13, 29):02d}/{draw.randrange(1990, 2025)}" for _ in range(1_000)]
        + ["9999-12-31"] * 10
        + ["12/31/9999"] * 10,
    ]
    on = [_date_walks(present) for present in columns]
    assert [walked[6] for walked in on] == ["day-first-date", None, "month-first-datetime", None, "month-first-date"]
    for present, walked in zip(columns, on):
        one_by_one = _date_walks_one_by_one(present)
        assert (walked[0], walked[1], walked[2], walked[5], walked[6], walked[7], walked[8]) == one_by_one
    _small_bound(monkeypatch)
    assert [_date_walks(present) for present in columns] == on
    _memo_off(monkeypatch)
    assert [_date_walks(present) for present in columns] == on


def test_a_walk_asks_a_format_once_a_spelling(monkeypatch: pytest.MonkeyPatch) -> None:
    present = ["17/03/2024", "25/12/2023", "N/A", "1/2/2024"] * 500
    asked: "list[tuple[str, str]]" = []
    original = parsing.parse_datetime

    def counted(text: str, format_name: str) -> "tuple[str, str] | None":
        nonlocal asked
        asked += [(text, format_name)]
        return original(text, format_name)

    monkeypatch.setattr(parsing, "parse_datetime", counted)
    taxonomy._reads(present, "day-first-date")
    assert len(asked) == len(set(present))


# -- the whole describe: every byte, with the memos on and off -------------------------------


def _table(path: pathlib.Path, rows: int = 600, seed: int = 21) -> pathlib.Path:
    """A table that reaches every reader built here: dates with placeholder days, stamps, marks, a decimal comma, ages, keys, words of no value."""
    draw = random.Random(seed)
    header = ["visit", "seen_on", "check_at", "charge", "eu_charge", "count", "age", "code", "key", "flag", "note"]
    lines = [",".join(header)]
    for row in range(rows):
        visit = draw.choice(["9999-12-31", "1900-01-01"]) if draw.random() < 0.05 else f"2024-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}"
        seen = f"{draw.randrange(13, 29):02d}/{draw.randrange(1, 13):02d}/{draw.randrange(2020, 2025)}"
        check = f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/2024 {draw.randrange(1, 13)}:{draw.choice(['05', '30'])} {draw.choice(['AM', 'PM'])}"
        amount = draw.randrange(100, 900000) / 100
        charge = f'"({amount:,.2f})"' if draw.random() < 0.1 else f'"{amount:,.2f}"'
        eu = f'"{amount:,.2f}"'.replace(",", "_").replace(".", ",").replace("_", ".")
        count = draw.choice(["7", "007", "+12", "12", "3", "0", "1e3", "-3"]) if draw.random() < 0.3 else f"{draw.randrange(0, 40)}"
        age = draw.choice(["92 years", "100 y/o", "999", "95", "-1"]) if draw.random() < 0.05 else f"{draw.randrange(18, 105)}"
        code = f"R{draw.randrange(1, 300):07d}"
        key = f"{draw.randrange(100000, 100400)}"
        flag = draw.choice(["NA", "n/a", "NaT", "nat", "", "#N/A", "Yes", "No", " NULL ", "UNKNOWN"])
        note = " ".join(draw.choice(["seen", "follow", "up", "stable", "pain", "none"]) for _ in range(draw.randrange(1, 4)))
        lines += [",".join([visit, seen, check, charge, eu, count, age, code, key, flag, note])]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _profiled(table: pathlib.Path, out: pathlib.Path) -> "tuple[int, str, dict[str, bytes]]":
    out.mkdir(exist_ok=True)
    said = io.StringIO()
    argv = [
        "profile", str(table), "--out-dir", str(out), "--replace", "--decimal-comma", "eu_charge",
        "--keep-value", "nat", "--missing-value", "UNKNOWN",
    ]
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv, small_tables_refused=False)
    written = {path.name: path.read_bytes() for path in sorted(out.iterdir()) if path.is_file()}
    return code, said.getvalue(), written


def test_the_describe_writes_and_prints_the_same_bytes_with_every_memo_off(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    table = _table(tmp_path / "clinic.csv")
    on = _profiled(table, tmp_path / "out")
    assert on[0] == 0 and len(on[2]) >= 3
    _memo_off(monkeypatch)
    assert _profiled(table, tmp_path / "out") == on
