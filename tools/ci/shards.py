#!/usr/bin/env python3
"""Split the collected suite across CI jobs, by file, and in a fixed order.

WHY THIS EXISTS. The suite is 7,087 cases and, measured on the
reference machine in one process, 54 min 42 s. Almost all of that is
serial CPU, so a two-core runner takes an hour and a half to three
hours, and every stage from here is gated by that run. Nothing here
makes a test cheaper: it makes the WALL CLOCK of one CI cell the cost
of the heaviest SHARD instead of the cost of the whole suite, by giving
each job a disjoint list of test FILES and running them in parallel
jobs.

WHY BY FILE, AND NOT BY CASE. Several files here build one large
module-scoped fixture and then read it from many cases -- the
presence-split battery is two thousand whole `validate` runs, built
once and read by three cases, and the entry table's red battery is
another eleven hundred read by four. Splitting by case would rebuild
that fixture in every shard that took one of its cases, so a
"balanced" split by case costs more in total than no split at all. A
file is the unit the shared cost belongs to, so a file is the unit
that moves.

WHAT MAKES THE SPLIT SAFE. Every file is in EXACTLY ONE shard, the
union is EXACTLY the set pytest collects, and `--prove` is the job that
says so against pytest's own collection rather than against this file's
idea of it. A file that appears in no shard would be a test silently
dropped, which is the one failure a speed change must not be able to
buy, and a file in two shards would be paid for twice.

HOW THE ASSIGNMENT IS MADE. Longest-processing-time first: the files
are ordered by their recorded seconds, heaviest first, ties broken by
name, and each one goes to the shard carrying the least so far, ties
broken by the lower shard number. The recorded seconds live in
`shard_weights.py` beside this file; a file with no record weighs
`DEFAULT_SECONDS`. The weights only DECIDE THE PACKING -- a stale
weight makes a shard uneven, never wrong -- so they are a convenience
and never a correctness surface. The order is a pure function of the
file names and that table, so two runs of this tool, on any platform
and any Python, produce the same plan.

USAGE

    python tools/ci/shards.py --of 5 --shard 3      # that shard's files
    python tools/ci/shards.py --of 5 --plan         # every shard, with
                                                    # its projected seconds
    python -m pytest --collect-only -q > collected.txt
    python tools/ci/shards.py --of 5 --prove --collected collected.txt

No network and no subprocess: it reads the test folder, the weight
table beside it, and -- for `--prove` -- the file pytest's own
collection was written to.
"""

import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TESTS = ROOT / "tests"
sys.path.insert(0, str(HERE))

import shard_weights

# What pytest collects under `testpaths = ["tests"]` with the default
# `python_files`. Written out rather than imported from pytest, so that
# `--prove` compares two independent readings of the same set.
PATTERNS = ("test_*.py", "*_test.py")

# The state page's own record of how many cases the suite collects, and
# the line of pytest's collection that says how many it just found.
STATE_PAGE = ROOT / "docs" / "STATE.md"
_STATED = re.compile(r"\|\s*suite\s*\|\s*([\d,]+)\s+collected")
_COLLECTED = re.compile(r"([\d,]+) tests? collected")


def collected_test_files(tests=TESTS):
    """Every test file, as a repository-relative POSIX path, sorted.

    Not named `test_*`: this module is loaded by a test, and a function
    whose name begins that way is one pytest would try to collect.
    """
    found = set()
    for pattern in PATTERNS:
        for path in tests.rglob(pattern):
            if path.is_file():
                found.add(path.relative_to(tests.parent).as_posix())
    return sorted(found)


def load_weights():
    """The recorded seconds per file, and the default for a file with none."""
    return shard_weights.SECONDS, shard_weights.DEFAULT_SECONDS


def plan(files, seconds, default, count):
    """``count`` disjoint lists of files whose union is ``files``.

    Longest-processing-time first, which is the classic greedy packing:
    within a factor of 4/3 of the best possible split, and a pure
    function of its arguments.
    """
    if count < 1:
        raise ValueError("a suite is split across one job or more")
    weighed = [(float(seconds[name]) if name in seconds else default, name) for name in files]
    order = sorted(weighed, key=lambda pair: (-pair[0], pair[1]))
    shards = [[] for _ in range(count)]
    load = [0.0] * count
    for weight, name in order:
        lightest = min(range(count), key=lambda index: (load[index], index))
        shards[lightest] = shards[lightest] + [name]
        load[lightest] = load[lightest] + weight
    return [sorted(shard) for shard in shards]


def projected(shard, seconds, default):
    """The seconds one shard is expected to take, from the recorded table."""
    total = 0.0
    for name in shard:
        total = total + (float(seconds[name]) if name in seconds else default)
    return total


def files_in(collected_text):
    """The test files named by `pytest --collect-only -q` output."""
    found = set()
    for line in collected_text.splitlines():
        entry = line.strip()
        if "::" in entry:
            found.add(entry.split("::")[0].replace("\\", "/"))
    return sorted(found)


def coverage_problems(shards, collected):
    """Every way the shards fail to be a partition of ``collected``, named."""
    problems = []
    seen = {}
    for index, shard in enumerate(shards):
        for name in shard:
            if name in seen:
                problems = problems + [
                    f"{name} is in shard {seen[name] + 1} and in shard {index + 1}: "
                    "a file is paid for twice"
                ]
            else:
                seen[name] = index
    wanted = set(collected)
    for name in sorted(wanted - set(seen)):
        problems = problems + [
            f"{name} is collected by pytest and is in no shard: it would not run"
        ]
    for name in sorted(set(seen) - wanted):
        problems = problems + [
            f"{name} is in shard {seen[name] + 1} but pytest collects nothing from it"
        ]
    if not any(shard for shard in shards):
        problems = problems + ["every shard is empty: nothing would run at all"]
    return problems


def cases_in(collected_text):
    """How many cases `pytest --collect-only -q` says it found, or None."""
    found = _COLLECTED.findall(collected_text)
    if not found:
        return None
    return int(found[len(found) - 1].replace(",", ""))


def state_page_problems(collected_text, page_text):
    """Whether the state page's stated suite size is this suite's size.

    WHY THIS LIVES HERE (landing D). `docs/STATE.md` states the number
    of cases the suite collects, and
    `tests/test_claim_inventory.py::test_the_state_page_states_the_suite_size_it_was_written_against`
    holds it -- but only on a WHOLE-SUITE run, because a subset
    collects fewer and would fail for a reason that is not a defect.
    Every sharded CI job is a subset, so that case stands down in all
    of them, and the split would otherwise have quietly taken the one
    mechanically enforced half of the page's own rule out of CI
    altogether. This job is the whole-suite collection, so it is where
    the check belongs now.
    """
    counted = cases_in(collected_text)
    if counted is None:
        return ["the collection names no case count, so nothing can be compared"]
    stated = _STATED.search(page_text)
    if stated is None:
        return [
            "docs/STATE.md no longer states its suite size as "
            "'| suite | N collected / ... |', which is the one shape this "
            "check can read"
        ]
    written = int(stated.group(1).replace(",", ""))
    if written != counted:
        return [
            f"docs/STATE.md says {written:,} cases and this suite collects "
            f"{counted:,}. The page moves in the same commit as the work it "
            "describes -- update the page rather than this check."
        ]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--of", type=int, required=True, help="how many shards")
    parser.add_argument("--shard", type=int, help="print this shard's files (1-based)")
    parser.add_argument("--plan", action="store_true", help="print every shard")
    parser.add_argument(
        "--prove",
        action="store_true",
        help="check the shards are exactly the collected set, once each",
    )
    parser.add_argument(
        "--collected",
        help="the output of `pytest --collect-only -q`, for --prove",
    )
    arguments = parser.parse_args(argv)
    seconds, default = load_weights()
    files = collected_test_files()
    shards = plan(files, seconds, default, arguments.of)

    if arguments.prove:
        if not arguments.collected:
            print("--prove needs --collected: the file pytest's own collection was written to")
            return 2
        text = pathlib.Path(arguments.collected).read_text(encoding="utf-8")
        collected = files_in(text)
        if not collected:
            print(
                f"{arguments.collected} names no test file. It must hold the output of "
                "`python -m pytest --collect-only -q`, whose lines are node ids."
            )
            return 2
        problems = coverage_problems(shards, collected)
        if problems:
            print(f"the {arguments.of} shards are not a partition of the collected suite:")
            for entry in problems:
                print(" -", entry)
            print("Fix tools/ci/shards.py or the shard count in .github/workflows/ci.yml.")
            return 1
        print(
            f"{len(collected)} collected test files, {arguments.of} shards, "
            "every file in exactly one"
        )
        stale = state_page_problems(
            text, STATE_PAGE.read_text(encoding="utf-8")
        )
        if stale:
            for entry in stale:
                print(" -", entry)
            return 1
        print(f"docs/STATE.md states this suite's size: {cases_in(text):,} cases")
        return 0

    if arguments.plan:
        for index, shard in enumerate(shards):
            print(
                f"shard {index + 1}/{arguments.of}: {len(shard)} files, "
                f"{projected(shard, seconds, default):.1f} s projected"
            )
            for name in shard:
                print(f"    {name}")
        return 0

    if arguments.shard is None:
        print("say --shard N, --plan, or --prove")
        return 2
    if not 1 <= arguments.shard <= arguments.of:
        print(f"shard {arguments.shard} is outside 1..{arguments.of}")
        return 2
    for name in shards[arguments.shard - 1]:
        print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
