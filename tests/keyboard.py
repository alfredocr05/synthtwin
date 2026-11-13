"""A person at the keyboard who keeps every reading synthtwin made, by answering (plan P4-D401).

Where nobody is at the keyboard, a column put a question offering
`identifier` is described as record numbers until the question is
answered (lane HX). A test about something else -- how a long tail writes
its stand-ins, how a padded number is spelled -- whose column such a
question reaches takes the reading the rules made by answering every
question with that reading, which is what a person who knows the columns
are read right does: the description is the one a scripted run wrote
before lane HX, byte for byte, since that answer keeps every reading and
declares nothing. Enter is no such answer since lane TT's repair (the
orchestrator's LANE TT RULINGS 2 (1)): it leaves the question open, as a
run with nobody at the keyboard leaves it.
"""

from __future__ import annotations

import pytest

from synthtwin import cli, taxonomy


def every_reading_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Somebody is there, and every answer they give keeps the reading and declares nothing.

    The reader hands back a word no key reaches and no question names,
    which the prompt takes as an answer that declares nothing (Enter's
    own word, `cli._LEFT_OPEN`, leaves the question open instead).
    """
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


def identifier_forms_answered_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """The person answers `no` to every Safe Harbor question the identifier forms put (plan P4-D445).

    A test about something else -- how a padded key of nineteen figures is
    spelled, how a column named `lot` pools its held-back codes -- whose
    column the identifier forms' hold takes (whole numbers of fifteen
    figures or more, a name that says a device's lot) takes the
    description `no` gives back, byte for byte: the one written before
    lane CZ-A, the hold then reaching nothing. Lane SH2's own holds are
    untouched.
    """
    monkeypatch.setattr(taxonomy, "identifier_form_hold", lambda *_given, **_named: "")
    monkeypatch.setattr(taxonomy, "named_as_device_numbers", lambda *_given, **_named: False)


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


def dates_in_disguise_answered_no(monkeypatch: pytest.MonkeyPatch) -> None:
    """The person answers `no` to every Safe Harbor question about dates in disguise (plan P4-D446).

    A test about something else -- how a number's widths, marks, styles,
    censuses or windows come back -- whose column holds five-figure numbers
    in a day-counting band (`12,345`, an income of 45,000), nine or ten
    figures in a seconds band, or a date as text beside its other values,
    takes the description `no` gives back, byte for byte: the one written
    before lane CZ-H, the value rule then holding nothing. The hold itself is
    pinned by `tests/test_zoo_dates_in_disguise.py` and K-HZ-16.
    """
    from synthtwin import date_counts

    monkeypatch.setattr(date_counts, "dated_values_blanked", lambda cells, *held: None)
