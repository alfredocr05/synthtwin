"""The counters of `K-HZ-35`'s phrase legs, read on their own (lane HB3-a, plan P4-D482).

What a leg's files and screen show and what its twin writes, counted by
linear counters that never read a cell through the product: a cell's age is
the largest run of figures it writes, over its unit's share of a year. Kept
apart from the driver (`tools/measurements/kpi_age_phrases_key_rooms.py`),
which sets the table floor off for its own process, so the gate
(`tests/test_age_phrases_and_key_rooms.py`) can show the counter reads every
file the bar names: the screen, the description and its summary, the
questions file, and since lane HB3-a's repair 1 (skeptic 1's item 8)
generate's twin report and validate's quality file; since its repair 2 a
spelling is looked for as written, as JSON writes it and as the product's
text files show a value (`parsing.visible`: a line feed inside a cell
written `\x0a`), so a phrase holding a line break is counted wherever it is
shown.
"""

from __future__ import annotations

import json
import pathlib
import re

from synthtwin import parsing

NUMBER = re.compile(r"[0-9]+")
# The files of one leg the counter reads beside its screen: the profile's in the
# leg's folder, generate's and validate's in its twin folder (`{stem}` the
# source's stem).
PROFILE_FILES = ("{stem}-profile.json", "{stem}-profile.txt", "{stem}-questions.json")
TWIN_FILES = ("{stem}-twin-report.txt", "{stem}-twin-quality.txt")


def texts_of(folder: pathlib.Path, twin_folder: pathlib.Path, stem: str, screen: str) -> "list[str]":
    """The screen and every file of one leg the bar names that exists, read whole."""
    texts = [screen]
    for name in PROFILE_FILES:
        path = folder / name.format(stem=stem)
        if path.is_file():
            texts += [path.read_text(encoding="utf-8")]
    for name in TWIN_FILES:
        path = twin_folder / name.format(stem=stem)
        if path.is_file():
            texts += [path.read_text(encoding="utf-8")]
    return texts


def years_of(cell: str, share: float = 1.0) -> float:
    """A cell's age in years as this counter reads it: its largest run of figures over ``share`` (the units a year holds), -1 where it writes none."""
    found = [int(figures) for figures in NUMBER.findall(cell)]
    return max(found) / share if found else -1.0


def shown(past: "set[str]", texts: "list[str]", top: bool, share: float = 1.0) -> "set[str]":
    """The real spellings past 89 any text shows, as written, as JSON writes them or as the text files show a value (`parsing.visible`); the top code's own spelling (90) aside where the column is top-coded."""
    found: "set[str]" = set()
    for spelling in past:
        if top and years_of(spelling, share) == 90:
            continue
        forms = (spelling, json.dumps(spelling)[1:-1], parsing.visible(spelling))
        for text in texts:
            if forms[0] in text or forms[1] in text or forms[2] in text:
                found.add(spelling)
                break
    return found
