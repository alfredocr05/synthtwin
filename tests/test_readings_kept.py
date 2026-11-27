"""The readings kept by their texts (lane SCALE).

`parsing.parse_number` and `parsing.classify_number` keep each answer by
the text it was read from, so a column of two million cells written in
about a thousand spellings is read about a thousand times, not two
million times over for each of the twenty readings the twin's writer and
the validator make of a numeric cell. These cases hold: every kept answer
is the reading's own (`number_read`, `number_class`) for every text --
the same text again, a text of `taxonomy.Note`, a text met after the
kept answers were let go -- and the kept answers never pass their bound.
"""

import pytest

from synthtwin import parsing, taxonomy

TEXTS = [
    "42", "-42", "+42", "0", "-0", "0.0", " 7.5 ", "1,234.50", "(1,234.50)", "1,483.65-", "−6.09",
    "1e5", "1E-400", "1e400", "(-5)", "(+5)", "(-a)", "nan", "inf", "", "  ", "abc", "12a", "0012", ".5", "5.",
    "1 234", "١٢", "-", "+", "1,2,3", "12,34", "007", "3.14159265358979323846",
]


def _fresh(monkeypatch: pytest.MonkeyPatch, most: int = parsing._KEPT_MOST) -> None:
    monkeypatch.setattr(parsing._Kept, "numbers", {})
    monkeypatch.setattr(parsing._Kept, "classes", {})
    monkeypatch.setattr(parsing, "_KEPT_MOST", most)


def test_every_kept_answer_is_the_readings_own(monkeypatch):
    _fresh(monkeypatch)
    for _round in range(3):
        for text in TEXTS:
            assert parsing.parse_number(text) == parsing.number_read(text) or (
                parsing.parse_number(text) is None and parsing.number_read(text) is None)
            assert parsing.classify_number(text) == parsing.number_class(text)
            note = taxonomy.Note(text)
            assert parsing.parse_number(note) == parsing.number_read(text) or parsing.number_read(text) is None
            assert parsing.classify_number(note) == parsing.number_class(text)


def test_the_two_readings_keep_their_own_answers(monkeypatch):
    """A text read as a number and classed keeps a value under one and a class under the other."""
    _fresh(monkeypatch)
    assert parsing.classify_number("12.5") == parsing.NUMBER
    assert parsing.parse_number("12.5") == 12.5
    assert parsing.classify_number("x") == parsing.NOT_A_NUMBER
    assert parsing.parse_number("x") is None
    assert parsing.parse_number("12.5") == 12.5 and parsing.classify_number("12.5") == parsing.NUMBER


def test_the_kept_answers_never_pass_their_bound_and_stay_right_after_letting_go(monkeypatch):
    _fresh(monkeypatch, most=8)
    texts = [f"{k}.5" for k in range(40)]
    for text in texts + texts:
        assert parsing.parse_number(text) == float(text)
        assert parsing.classify_number(text) == parsing.NUMBER
        assert len(parsing._Kept.numbers) <= 8 and len(parsing._Kept.classes) <= 8


def test_a_text_that_is_not_text_is_refused_as_before():
    with pytest.raises(TypeError):
        parsing.parse_number(5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parsing.classify_number(None)  # type: ignore[arg-type]


def test_a_long_text_is_read_afresh_and_never_kept(monkeypatch):
    """A note of many characters is no number a column repeats: it is read, never held by the kept answers."""
    _fresh(monkeypatch)
    note = "1" * (parsing._KEPT_LONGEST + 1)
    assert parsing.parse_number(note) == parsing.number_read(note)
    assert parsing.classify_number(note) == parsing.number_class(note)
    assert note not in parsing._Kept.numbers and note not in parsing._Kept.classes
    short = "1" * parsing._KEPT_LONGEST
    parsing.parse_number(short)
    parsing.classify_number(short)
    assert short in parsing._Kept.numbers and short in parsing._Kept.classes
