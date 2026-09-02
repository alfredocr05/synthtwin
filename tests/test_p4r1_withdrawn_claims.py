"""No shipped surface may still describe behaviour that was withdrawn.

REVIEW ROUND 1 OF LANDING L7, ITEM 5. Four passages of `generation.py`
went on describing the walk and the layout as they were BEFORE that
landing: two view docstrings saying the grain defect was unrepaired, a
comment saying the spelling budgets take the grain's count, and
`_joined_content` saying only the pairs the last position is in are
moved. Every one of them was true when it was written and false when
it was read, and a second implementation following them would rebuild
the behaviour this repository withdrew -- which is the whole reason
these files are written for a reader at all.

WHY A TEXT GUARD AND NOT A REVIEW NOTE. The stale passages survived a
landing, an adversarial round and a merge. What no reviewer can do
reliably is notice a sentence that is merely OLD, so the sentences that
must not come back are listed here by their own words, and the suite
turns red on them.

WHAT THIS IS NOT. It is not a style rule and it does not forbid
DESCRIBING the old behaviour: every entry below is a claim in the
present tense about what the code does. A passage saying "the walk
moved the last position and no other until landing L7" is history and
is wanted; one saying it "moves the last position and no other" is a
false description of shipped code.
"""
import pathlib
import re

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]

# Each entry is (phrase, what it would tell a reader that is not true).
WITHDRAWN = (
    (
        "IS STILL THE CELL'S, WHICH IS",
        "a grain inside a role is divided by the count of different "
        "CELLS around it -- withdrawn by landing L7, which hands each "
        "grain its own n_distinct_values for the division",
    ),
    (
        "THE SPELLING BUDGETS TAKE THE GRAIN'S COUNT",
        "the spelling budgets take the grain's count of numbers -- "
        "withdrawn by review round 1 item 1, which put them back on "
        "the block's counts so a grain can write every spelling its "
        "cells wear",
    ),
    (
        "on the pairs it does not move",
        "some pair of positions is moved by nothing -- withdrawn by "
        "landing L7, which moves every position but the first",
    ),
    (
        "moves the LAST position and no other",
        "the pairing walk moves one position and no other -- withdrawn "
        "by landing L7, which moves every position but the first",
    ),
)

# TWO MORE WERE DRAFTED AND DROPPED, and the reason is worth keeping:
# "moves the last position and no other" and "moves only the last
# position" read like the withdrawn claim and were never in the shipped
# file -- they were this author's paraphrase of it. The provenance
# check below caught both. A guard listing a phrase nobody wrote is a
# guard that cannot fail, dressed as one that can.

# The shipped package and the oracle that implements the method beside
# it. The plan and this page's own history are NOT walked: a residual
# register exists to record what a thing used to do.
WALKED = (
    "src/synthtwin",
    "tools/reference",
)


def _flattened(text: str) -> str:
    """The text with every run of whitespace collapsed to one space.

    WHY THE COMPARISON IS MADE THIS WAY. These files wrap at seventy-odd
    characters, so a sentence is broken across lines wherever it
    happens to fall and the same claim reads differently after a
    re-wrap. Collapsing first means the guard matches the WORDS, and a
    paragraph re-flowed by an editor neither hides a claim nor invents
    one.

    It is also what lets the list below hold PRESENT-tense claims only:
    "moves the LAST position and no other" is a description of shipped
    code and is refused, while "moved the LAST position and no other
    until landing L7" is history and is wanted. One letter separates
    them and no line-based search can see it.
    """
    return re.sub(r"\s+", " ", text)


def _shipped_files() -> "list[pathlib.Path]":
    found: "list[pathlib.Path]" = []
    for where in WALKED:
        for path in sorted((REPOSITORY / where).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            found = found + [path]
    return found


def test_the_walk_is_walking_something() -> None:
    """A guard over no files is a guard that cannot fail."""
    files = _shipped_files()
    assert len(files) >= 10, [f"{path}" for path in files]
    names = {path.name for path in files}
    assert "generation.py" in names, sorted(names)
    assert "make_generation_reference_vectors.py" in names, sorted(names)


@pytest.mark.parametrize("phrase,meaning", WITHDRAWN)
def test_no_shipped_file_still_claims_withdrawn_behaviour(
    phrase: str, meaning: str
) -> None:
    """Goes red when a withdrawn description comes back into the code."""
    guilty: "list[str]" = []
    for path in _shipped_files():
        text = _flattened(path.read_text(encoding="utf-8"))
        if phrase in text:
            guilty = guilty + [f"{path.relative_to(REPOSITORY)}"]
    assert not guilty, (
        f"{guilty} still say {phrase!r}, which tells a reader that "
        f"{meaning}"
    )


def test_the_phrases_are_the_ones_that_were_really_there() -> None:
    """The list is not arbitrary: each phrase was in the shipped code.

    Held against the two commits this branch has already shipped from
    -- the tree landing L7 branched from, and L7 as it was merged -- so
    a phrase nobody ever wrote cannot be added here to make the guard
    look wider than it is. Every phrase must have been in ONE of them:
    two of these were written by the landing under review and withdrawn
    by its own first round, and a check against the earlier commit
    alone would call those imaginary. Skipped where neither commit is
    reachable, which is the one thing a worktree cannot promise.
    """
    import subprocess

    shipped: "list[str]" = []
    for commit in ("21fe8c4", "80f0ea7"):
        try:
            shipped = shipped + [subprocess.run(
                ["git", "show", f"{commit}:src/synthtwin/generation.py"],
                cwd=REPOSITORY, capture_output=True, text=True, check=True,
            ).stdout]
        except Exception:  # noqa: BLE001 - the commit may be unreachable
            continue
    if not shipped:
        pytest.skip("neither shipped commit is reachable from here")
    shipped = [_flattened(text) for text in shipped]
    for phrase, _meaning in WITHDRAWN:
        assert any(phrase in text for text in shipped), (
            f"{phrase!r} was never in the shipped code, so guarding "
            "against it guards against nothing"
        )
