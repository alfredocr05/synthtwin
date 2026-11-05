"""A person at the keyboard who presses Enter at every question (plan P4-D401).

Where nobody is at the keyboard, a column put a question offering
`identifier` is described as record numbers until the question is
answered (lane HX). A test about something else -- how a long tail writes
its stand-ins, how a padded number is spelled -- whose column such a
question reaches takes the reading the rules made by answering every
question with Enter, which is what a person who presses through does:
the description is the one a scripted run wrote before lane HX, byte for
byte, since Enter keeps every reading and declares nothing.
"""

from __future__ import annotations

import pytest

from synthtwin import cli, taxonomy


def every_reading_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Somebody is there, and every answer they type is Enter."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda *_given: "")


def safe_harbor_answered_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """The person answers `no` to every Safe Harbor question (plan P4-D427).

    A test about something else -- how a number's widths, marks, styles
    or windows come back -- whose column the Safe Harbor reach takes
    (amounts from 100.00 to 103.87, weights in kilograms, counts of five
    figures written as ZIP codes are) takes the description `no` gives
    back, byte for byte: the one written before lane SH, the reach then
    reaching nothing. The questions put to the column are those the rules
    put; the answer is the person's.
    """
    monkeypatch.setattr(taxonomy, "safe_harbor_reach", lambda *_given, **_named: "")
    # ...and to lane SH2's (plan P4-D434): every Safe Harbor question.
    sh2_answered_no(monkeypatch)


def sh2_answered_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """The person answers `no` to every Safe Harbor question lane SH2 puts (plan P4-D434).

    A test about something else -- how counted days crossing 1900 come
    back, how a placeholder day is judged, how dates of a few patients
    are pooled in people -- whose column lane SH2's reach takes (dates of
    1890 to 1935, a column named `address`) takes the description `no`
    gives back, byte for byte: the one written before lane SH2, the reach
    then reaching nothing. Lane SH's own reach is untouched.
    """
    monkeypatch.setattr(taxonomy, "safe_harbor_years", lambda *_given, **_named: False)
    monkeypatch.setattr(taxonomy, "safe_harbor_hold", lambda *_given, **_named: "")
    # ...and the pairs of coordinates read from their cells (its close round).
    monkeypatch.setattr(taxonomy, "coordinates_held", lambda *_given, **_named: [])
