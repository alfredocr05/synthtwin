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

from synthtwin import cli


def every_reading_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """Somebody is there, and every answer they type is Enter."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda *_given: "")
