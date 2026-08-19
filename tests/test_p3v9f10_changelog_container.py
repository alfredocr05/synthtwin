"""The changelog keeps a release container, so the release step can run.

REVIEW ITEM P3-V9-F10; plan amendment A-P3-38 clause 3.

WHAT WENT WRONG. The commit that landed contract version 5 wrote its
entry as a level-THREE heading at the top of the file and, in doing so,
replaced the `## [Unreleased]` line that had stood above every Phase 3
entry. Nothing failed. The file still read correctly to a human, every
test stayed green, and the loss was invisible until somebody counted
headings -- because a missing container looks exactly like a file whose
first section happens to start early.

WHY IT MATTERS, AND IT IS NOT TIDINESS. Two ratified sentences rest on
that heading. The plan's release step (P3-D5 decision 5, and the
migration table's third stage) says CHANGELOG's `[Unreleased]` converts
to `[0.1.0]` with the date -- an instruction with nothing to act on if
the section is gone -- and amendment A-P3-27's timing argument states as
fact that "the changelog has one `[Unreleased]` section". A release
carried out to the letter would have tagged a changelog whose newest
entries sat under no version at all, and every entry written since the
loss would have shipped as belonging to no release.

WHAT IS CHECKED, AND WHY IT IS NOT A STRING MATCH ON ONE LINE. Three
properties, each of which the defect broke:

1. the file has a level-two release container at all;
2. no level-three entry stands above the first container, which is the
   exact shape the defect left behind -- entries with no release;
3. while the shipped version is a pre-release, the newest container is
   `[Unreleased]`, and there is exactly one of it.

The third is tied to the SHIPPED VERSION rather than pinned, so this
guard does not have to be edited at the release: the day `0.1.0` ships,
`[Unreleased]` is expected to have become `[0.1.0]` and the third
property stands down of its own accord while the first two keep
holding. A guard a release has to defeat is a guard somebody deletes.

THE RED CHECK. `REINSTATE=P3-V9-F10` deletes the container line from the
text this file reads, which is precisely what the version 5 commit did,
and every assertion that depends on it goes red.
"""

import os
import pathlib
import re

import pytest

from synthtwin import profile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

# A level-two heading, which is what Keep a Changelog calls a release,
# and a level-three heading, which is what one entry of a release is.
_CONTAINER = re.compile(r"^## +(?P<name>.+?)\s*$")
_ENTRY = re.compile(r"^### +.+$")

_UNRELEASED = "[Unreleased]"


def _lines() -> "list[str]":
    """The changelog's lines, or the defect's own file when asked.

    The single door every check below reads through, so the red check
    can put the missing container back the way it went -- by taking the
    line out -- without touching the tree.
    """
    text = CHANGELOG.read_text(encoding="utf-8")
    if os.environ.get("REINSTATE") == "P3-V9-F10":
        text = "\n".join(
            line
            for line in text.split("\n")
            if _CONTAINER.match(line) is None
        )
    return text.split("\n")


def _containers() -> "list[tuple[int, str]]":
    """Every release container, as (line number, name)."""
    found = []
    for number, line in enumerate(_lines(), start=1):
        matched = _CONTAINER.match(line)
        if matched is not None:
            found.append((number, matched.group("name")))
    return found


def _is_a_prerelease() -> bool:
    """Whether the shipped version is one no release has happened for.

    Read from the installed package rather than from `pyproject.toml`,
    for the reason the claim inventory reads the wire version from the
    product: a file somebody has to remember to update is the thing
    every guard in this repository has been caught by.
    """
    return "dev" in profile._version()


def test_the_changelog_has_a_release_container() -> None:
    """Property 1: there is a level-two section for a release to become."""
    assert _containers(), (
        "CHANGELOG.md has no level-two release section. The ratified "
        "release step converts one into the dated version heading, so a "
        "changelog with none cannot be released as written: put "
        f"`## {_UNRELEASED}` back above the newest entry."
    )


def test_no_entry_stands_above_the_first_container() -> None:
    """Property 2: the exact shape the defect left behind.

    An entry above every container belongs to no release. This is what
    the version 5 commit produced, and it is why the first property on
    its own is not enough: a file could keep an old `## [0.1.0]` far
    below while new entries piled up above it.
    """
    lines = _lines()
    first = _containers()[0][0] if _containers() else len(lines) + 1
    orphans = [
        f"{number}: {line.strip()}"
        for number, line in enumerate(lines, start=1)
        if _ENTRY.match(line) is not None and number < first
    ]
    assert not orphans, (
        "These changelog entries stand above every release section, so "
        "they belong to no release:\n  "
        + "\n  ".join(orphans)
        + f"\n\nPut `## {_UNRELEASED}` above them."
    )


def test_the_newest_container_is_unreleased_until_something_is_released(
) -> None:
    """Property 3, and it stands down by itself at the release.

    While the shipped version is a pre-release there is nothing to have
    released, so the newest section is the one the release step renames.
    """
    if not _is_a_prerelease():
        pytest.skip(
            "a release has shipped, so the newest section is a dated "
            "version rather than the unreleased one"
        )
    named = [name for _number, name in _containers()]
    assert named, (
        "CHANGELOG.md has no level-two release section at all, so there "
        f"is nothing for `## {_UNRELEASED}` to be the newest of."
    )
    assert named[0] == _UNRELEASED, (
        f"The newest changelog section is {named[0]!r}, and the shipped "
        f"version {profile._version()} says nothing has been released. "
        f"The newest section is `## {_UNRELEASED}` until the release "
        "step renames it."
    )
    assert named.count(_UNRELEASED) == 1, (
        f"CHANGELOG.md has {named.count(_UNRELEASED)} `{_UNRELEASED}` "
        "sections. The plan's timing argument and its release step both "
        "say one."
    )


def test_the_plan_and_the_release_step_still_rest_on_this_heading() -> None:
    """The guard is bound to the sentences that need it, not to taste.

    If a later ruling withdraws the release step's instruction or the
    timing argument's claim, this test goes red and whoever withdrew it
    decides what the changelog owes -- rather than this file quietly
    enforcing a rule nothing asks for any more.
    """
    plan = (REPO_ROOT / "docs" / "plans" / "phase-3-product.md").read_text(
        encoding="utf-8"
    )
    assert f"CHANGELOG's `{_UNRELEASED}` converts" in plan, (
        "the release step no longer names the section this guard "
        "protects; re-read P3-D5 decision 5 before changing this file"
    )
    assert f"one `{_UNRELEASED}` section" in plan, (
        "the plan's timing argument no longer asserts the section "
        "exists; re-read amendment A-P3-27 before changing this file"
    )
