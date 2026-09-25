"""The CI shards are a partition of the suite, and the workflow agrees.

LANDING D (the suite's cost). The suite is 7,087 collected cases and,
in one process on the reference machine, 54 min 42 s of almost entirely
serial CPU; a two-core runner spends an hour and a half to three hours on
it, on every cell of the matrix, and every stage from here is gated by
that run. `tools/ci/shards.py` cuts the WALL CLOCK of a cell by giving
each CI job a disjoint list of test FILES.

WHAT THIS FILE IS FOR. A speed change may cost no test and no
assertion, so the one thing that must be impossible is a file that
quietly stops running. The tests below hold the split to being a
PARTITION -- every collected file in exactly one shard, nothing added,
nothing missing -- and hold the shard count written in the workflow
equal to the count the tool is asked for, because a workflow that runs
shards 1..4 of a five-way split drops a fifth of the suite and every
job still goes green.

THE REPRODUCTION, and it is the mutation check too. Set
`REINSTATE=D-CI-SHARDS-DROP` and the plan loses its last file: the
partition test names the file that would not run, and the prover
returns 1 instead of 0. That is the defect this file exists to catch,
made to happen on demand.

    REINSTATE=D-CI-SHARDS-DROP python -m pytest tests/test_ci_shards.py

THE SECOND REPRODUCTION, and it is the other way a shard can run no
test at all. The CI step redirects this tool into a file and hands the
words to pytest, so the BYTES of that file are part of the interface: a
stream that ends its lines the Windows way hands pytest twenty-five
jobs' worth of paths with a trailing carriage return, and every one is
"file or directory not found". Set `REINSTATE=D-SHARD-CRLF` and the
tool runs without the guard that settles it:

    REINSTATE=D-SHARD-CRLF python -m pytest tests/test_ci_shards.py

THE THIRD, and it is about what those steps leave behind rather than
what they run: the file each one redirects into the checkout root must
be named in `.gitignore`, or the next `git add -A` stages a generated
list into a repository that is otherwise strict about what enters it.

    REINSTATE=D-SHARD-ARTEFACTS python -m pytest tests/test_ci_shards.py

No table and no fixture data is involved: this file reads the test
folder, the workflow and one weight table.
"""

import importlib.util
import os
import pathlib
import random
import re
import subprocess
import sys
import typing

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"
IGNORED = REPO / ".gitignore"


def _load_tool(relative: str, name: str) -> object:
    """A script under tools/ loaded as a module, without adding tools/ to the path."""
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shards = _load_tool("tools/ci/shards.py", "ci_shards_under_test")
# The real packing, held before anything here can replace it, so the
# mutant below is a wrapper around it and not a call to itself.
_PLAN = shards.plan  # type: ignore[attr-defined]


def _one_file_dropped(
    files: "list[str]", seconds: "dict[str, float]", default: float, count: int
) -> "list[list[str]]":
    """The plan with its last file left out: the mutant this file catches.

    It is the shape of the mistake that matters, not the mechanism. A
    shard plan that is not a partition -- an off-by-one on a slice, a
    filter that drops a name, a workflow matrix one shorter than the
    split -- loses whole files while every job still exits 0, and the
    suite reports nothing at all.
    """
    built = _PLAN(files, seconds, default, count)
    for index in range(len(built) - 1, -1, -1):
        if built[index]:
            return built[:index] + [built[index][:-1]] + built[index + 1 :]
    return built


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("REINSTATE") == "D-CI-SHARDS-DROP":
        monkeypatch.setattr(shards, "plan", _one_file_dropped)


def _count_in_workflow() -> int:
    """The shard count the workflow declares, once, as `SHARD_COUNT`."""
    text = WORKFLOW.read_text(encoding="utf-8")
    found = re.findall(r"^\s*SHARD_COUNT:\s*\"(\d+)\"\s*$", text, flags=re.MULTILINE)
    assert len(found) == 1, (
        f".github/workflows/ci.yml declares SHARD_COUNT {len(found)} times; "
        "the split has one count and it is written once"
    )
    return int(found[0])


def _matrix_shard_lists() -> "list[list[int]]":
    """Every `shard: [...]` list the workflow's matrices name."""
    text = WORKFLOW.read_text(encoding="utf-8")
    return [
        [int(piece) for piece in re.findall(r"\d+", body)]
        for body in re.findall(r"^\s*shard:\s*\[([^\]]*)\]\s*$", text, flags=re.MULTILINE)
    ]


def _included_shards() -> "list[int]":
    """Every `shard: N` an `include` row names, as one sorted list.

    A matrix `include` adds ONE combination at a time, so the macOS cell
    is written out once per shard and those rows carry a bare number
    rather than a list. They are the half of the matrix a `shard: [...]`
    reading cannot see, and a split that grew by one would leave them a
    shard short with nothing saying so.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    return sorted(
        int(found)
        for found in re.findall(
            r"^\s*shard:\s*(\d+)\s*$", text, flags=re.MULTILINE
        )
    )


@pytest.fixture(scope="module")
def collected_files() -> "list[str]":
    """Every test file in the tree, read here and not through the tool.

    INDEPENDENT ON PURPOSE. If this list came from
    `tools/ci/shards.py`, the partition test below would be comparing
    the tool with itself and a tool that listed half the folder would
    pass. It is the same rule pytest is configured with -- `testpaths =
    ["tests"]`, the default `python_files` -- read off the folder here.
    """
    found: list[str] = []
    for path in sorted((REPO / "tests").rglob("*.py")):
        name = path.name
        if name.startswith("test_") or name.endswith("_test.py"):
            found = found + [path.relative_to(REPO).as_posix()]
    return found


def _plan(count: int, collected: "list[str]") -> "list[list[str]]":
    seconds, default = shards.load_weights()  # type: ignore[attr-defined]
    return shards.plan(collected, seconds, default, count)  # type: ignore[attr-defined]


# -- the partition ------------------------------------------------------


def test_every_collected_test_file_is_in_exactly_one_shard(
    collected_files: "list[str]",
) -> None:
    """No file runs twice, and -- the one that matters -- none runs nowhere."""
    count = _count_in_workflow()
    built = _plan(count, collected_files)
    placed: dict[str, int] = {}
    twice: list[str] = []
    for index, shard in enumerate(built):
        for name in shard:
            if name in placed:
                twice = twice + [f"{name}: shards {placed[name] + 1} and {index + 1}"]
            placed[name] = index
    assert not twice, "these files are in more than one shard:\n  " + "\n  ".join(twice)
    missing = sorted(set(collected_files) - set(placed))
    assert not missing, (
        "these test files are in no shard, so CI would not run them and "
        "every job would still be green:\n  " + "\n  ".join(missing)
    )
    assert not sorted(set(placed) - set(collected_files)), (
        "these shard entries are not test files in this tree"
    )


def test_the_prover_says_so_against_pytest_s_own_collection(
    collected_files: "list[str]",
) -> None:
    """The job CI runs: the shards against the node ids pytest prints.

    The collection text is built here in pytest's own `-q` shape --
    one node id per line -- so the prover is exercised on what it reads
    in CI, not on a list this file hands it directly.
    """
    count = _count_in_workflow()
    text = "".join(f"{name}::test_something\n" for name in collected_files)
    text = text + f"\n{len(collected_files)} tests collected in 12.34s\n"
    named = shards.files_in(text)  # type: ignore[attr-defined]
    assert named == sorted(collected_files)
    assert shards.coverage_problems(_plan(count, collected_files), named) == []  # type: ignore[attr-defined]


def test_a_file_left_out_of_every_shard_is_reported_by_name(
    collected_files: "list[str]",
) -> None:
    """The mutation check, asserted directly as well as through REINSTATE."""
    count = _count_in_workflow()
    built = _one_file_dropped(collected_files, *shards.load_weights(), count)  # type: ignore[attr-defined]
    problems = shards.coverage_problems(built, sorted(collected_files))  # type: ignore[attr-defined]
    assert len(problems) == 1 and "is in no shard" in problems[0]


def test_a_file_in_two_shards_is_reported_by_name(
    collected_files: "list[str]",
) -> None:
    """The other half of a partition: paying for one file twice.

    Built off the real packing rather than the patched one, so this
    assertion is about `coverage_problems` alone.
    """
    count = _count_in_workflow()
    seconds, default = shards.load_weights()  # type: ignore[attr-defined]
    built = _PLAN(collected_files, seconds, default, count)
    doubled = [built[0] + [built[1][0]]] + built[1:]
    problems = shards.coverage_problems(doubled, sorted(collected_files))  # type: ignore[attr-defined]
    assert len(problems) == 1 and "paid for twice" in problems[0]


# -- the guard the split would otherwise have taken out of CI -----------


def test_the_prover_holds_the_state_page_to_the_suite_s_own_size() -> None:
    """A sharded job is a subset, so the page's count needs another keeper.

    `tests/test_claim_inventory.py` holds `docs/STATE.md`'s stated
    suite size, and stands down on a selected run because a subset
    collects fewer cases. EVERY SHARDED JOB IS A SELECTED RUN, so that
    case skips in all of them and the split would have quietly taken
    the one mechanically enforced half of the page's rule out of CI.
    The coverage job collects the whole suite, so it carries the check
    now, and these are the two ways it can read.
    """
    collection = "tests/test_a.py::test_one\n\n7000 tests collected in 1.2s\n"
    agreeing = "| suite | 7,000 collected, and **1 min** on the reference machine |"
    assert shards.state_page_problems(collection, agreeing) == []  # type: ignore[attr-defined]
    disagreeing = "| suite | 6,999 collected, and **1 min** on the reference machine |"
    problems = shards.state_page_problems(collection, disagreeing)  # type: ignore[attr-defined]
    assert len(problems) == 1 and "6,999" in problems[0] and "7,000" in problems[0]
    missing = "| suite | nothing stated here |"
    assert len(shards.state_page_problems(collection, missing)) == 1  # type: ignore[attr-defined]


def _coverage_job_problems(workflow: str) -> "list[str]":
    """What would stop CI's shard-coverage job holding the whole-suite count."""
    job = re.search(
        r"^  shard-coverage:\n(?P<body>(?:(?!  \S).*\n?)*)", workflow, re.MULTILINE
    )
    if job is None:
        return ["ci.yml has no shard-coverage job"]
    body = job.group("body")
    problems = []
    if "pytest --collect-only" not in body:
        problems.append("shard-coverage no longer collects the whole suite")
    if not re.search(r"tools/ci/shards\.py\b[^\n]*--prove[^\n]*--collected", body):
        problems.append("shard-coverage no longer runs tools/ci/shards.py --prove on it")
    if re.search(r"^\s+if:", body, re.MULTILINE):
        problems.append("shard-coverage runs only under a condition")
    return problems


def test_the_shard_coverage_job_still_holds_the_state_page_count() -> None:
    """The prover above is the ONLY keeper of the page's count in CI.

    The case in `tests/test_claim_inventory.py` skips in every shard, so
    a workflow that dropped the prover step would leave that count
    checked nowhere in CI with every job green. MEASURED 2026-09-24: the
    five-shard run and one process differ by exactly that case, 7,601
    passed and 50 skipped against 7,602 and 49.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert _coverage_job_problems(text) == []
    dropped = text.replace(" --prove --collected collected.txt", "")
    assert dropped != text, "the prover step is no longer spelled as this test expects"
    assert _coverage_job_problems(dropped) == [
        "shard-coverage no longer runs tools/ci/shards.py --prove on it"
    ]
    gated = text.replace("  shard-coverage:\n", "  shard-coverage:\n    if: false\n", 1)
    assert _coverage_job_problems(gated) == ["shard-coverage runs only under a condition"]
    assert _coverage_job_problems(text.replace("  shard-coverage:\n", "  renamed:\n", 1)) == [
        "ci.yml has no shard-coverage job"
    ]


def test_the_prover_reads_the_same_count_pytest_prints() -> None:
    """`N tests collected` is the line, in both of pytest's spellings."""
    assert shards.cases_in("1 test collected in 0.1s\n") == 1  # type: ignore[attr-defined]
    assert shards.cases_in("7105 tests collected in 1.5s\n") == 7105  # type: ignore[attr-defined]
    assert shards.cases_in("no tests ran\n") is None  # type: ignore[attr-defined]


# -- the workflow says the same number ----------------------------------


def test_every_matrix_runs_exactly_the_shards_the_split_has(
    collected_files: "list[str]",
) -> None:
    """A matrix one shard short drops that shard's files and goes green.

    Both sharded jobs -- the matrix cell suite and the floors job --
    name their shards as a list, and every such list must be 1..N for
    the one declared N. The `include` rows that add the macOS cell name
    one shard each instead, and between them they must name the same N:
    a split grown by one would otherwise leave macOS running four
    fifths of the suite with every job still green.
    """
    count = _count_in_workflow()
    wanted = list(range(1, count + 1))
    lists = _matrix_shard_lists()
    assert lists, ".github/workflows/ci.yml names no `shard:` matrix at all"
    for entry in lists:
        assert entry == wanted, (
            f"a matrix runs shards {entry} of a {count}-way split; it must run "
            f"{wanted}, or the files in the missing shards run nowhere"
        )
    included = _included_shards()
    assert included, (
        ".github/workflows/ci.yml has no `include` row naming a shard; the "
        "macOS cell is added one shard at a time and each row names its own"
    )
    assert included == wanted, (
        f"the `include` rows name shards {included} of a {count}-way split; "
        f"they must name {wanted}, or that cell runs part of the suite"
    )


def test_the_workflow_asks_the_tool_for_the_count_it_declares() -> None:
    """Every call of the tool in CI is `--of "$SHARD_COUNT"`, never a literal.

    Comment lines are left out: the workflow sets out the split in
    prose and may quote the command, and a sentence is not a job step.
    """
    steps = "\n".join(
        line
        for line in WORKFLOW.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )
    calls = re.findall(r"tools/ci/shards\.py\s+--of\s+(\S+)", steps)
    assert calls, "no CI job calls tools/ci/shards.py"
    for argument in calls:
        assert argument == '"$SHARD_COUNT"', (
            f"a CI job asks tools/ci/shards.py for --of {argument}; it must ask for "
            'the declared "$SHARD_COUNT", so the count cannot drift in one place'
        )


def test_the_matrix_cells_are_the_platforms_and_pythons_they_were() -> None:
    """Sharding adds a dimension; it removes no platform and no Python.

    The suite must pass on 3.10 through 3.14 on Ubuntu, Windows and
    macOS, and a split that quietly stopped running a cell would be a
    cheaper CI that proves less.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    for wanted in ('"3.10"', '"3.11"', '"3.12"', '"3.13"', '"3.14"'):
        assert wanted in text, f"the test matrix no longer names Python {wanted}"
    for platform in ("ubuntu-latest", "windows-latest", "macos-latest"):
        assert platform in text, f"the test matrix no longer names {platform}"


# -- the packing --------------------------------------------------------


def test_the_plan_does_not_depend_on_the_order_it_is_given(
    collected_files: "list[str]",
) -> None:
    """Deterministic: the same files in any order give the same shards."""
    count = _count_in_workflow()
    shuffled = list(collected_files)
    random.Random(20260921).shuffle(shuffled)
    assert _plan(count, shuffled) == _plan(count, collected_files)


def test_a_file_the_weight_table_never_heard_of_is_still_placed() -> None:
    """A test file added since the last measurement runs from that commit."""
    named = ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]
    built = _PLAN(named, {"tests/test_a.py": 30.0}, 1.0, 2)
    assert sorted(name for shard in built for name in shard) == named
    assert built[0] == ["tests/test_a.py"]


def test_the_heaviest_shard_is_inside_the_greedy_bound(
    collected_files: "list[str]",
) -> None:
    """Longest-processing-time first, held to what it guarantees.

    No split can beat the heaviest single file, and none can beat the
    total divided by the shards; greedy longest-first stays within 4/3
    of that. Asserting the bound rather than a measured number keeps
    this green when the weights are re-measured, and red if the packing
    is replaced by something that drops a slow file into an already
    full shard.
    """
    count = _count_in_workflow()
    seconds, default = shards.load_weights()  # type: ignore[attr-defined]
    built = _plan(count, collected_files)
    loads = [shards.projected(shard, seconds, default) for shard in built]  # type: ignore[attr-defined]
    heaviest_file = max(
        float(seconds[name]) if name in seconds else default for name in collected_files
    )
    best_possible = max(heaviest_file, sum(loads) / count)
    assert max(loads) <= best_possible * 4 / 3 + default, (
        f"the heaviest shard is {max(loads):.1f} s against a best possible "
        f"{best_possible:.1f} s: the packing is not longest-first any more"
    )


def test_the_weight_table_names_only_files_that_exist(
    collected_files: "list[str]",
) -> None:
    """A weight for a deleted file is a measurement of nothing; say so."""
    seconds, _default = shards.load_weights()  # type: ignore[attr-defined]
    stale = sorted(set(seconds) - set(collected_files))
    assert not stale, (
        "tools/ci/shard_weights.py weighs files this tree does not have:\n  "
        + "\n  ".join(stale)
    )


def test_the_tool_refuses_a_collection_file_that_names_no_test(
    tmp_path: pathlib.Path,
) -> None:
    """An empty collection is a broken job, not a suite with nothing in it."""
    empty = tmp_path / "collected.txt"
    empty.write_text("no tests ran\n", encoding="utf-8", newline="\n")
    count = _count_in_workflow()
    code = shards.main(  # type: ignore[attr-defined]
        ["--of", str(count), "--prove", "--collected", str(empty)]
    )
    assert code == 2


def test_the_tool_prints_one_shard_and_nothing_else(
    capsys: "typing.Any", collected_files: "list[str]"
) -> None:
    """`--shard N` is what the CI step passes to pytest, so it is only names."""
    count = _count_in_workflow()
    code = shards.main(["--of", str(count), "--shard", "1"])  # type: ignore[attr-defined]
    assert code == 0
    printed = capsys.readouterr().out.splitlines()
    assert printed == _plan(count, collected_files)[0]


# -- the bytes the CI step redirects into a file ------------------------

# A child that runs the real tool with a stdout that translates line
# endings the way a Windows console stream does, and writes it to the
# file the CI step redirects into. Nothing here emulates the TOOL: the
# tool is loaded from the repository and run as CI runs it. The only
# thing standing in for Windows is the one byte-level behaviour of a
# text stream opened with the platform default, which is what a macOS
# or Linux runner cannot show by itself.
_WINDOWS_STDOUT_CHILD = """
import io, os, pathlib, runpy, sys

target = pathlib.Path(sys.argv[1])
count = sys.argv[2]
shard = sys.argv[3]
tool = pathlib.Path(sys.argv[4])

handle = open(target, "wb")
sys.stdout = io.TextIOWrapper(handle, encoding="utf-8", newline="\\r\\n")
sys.argv = ["shards.py", "--of", count, "--shard", shard]
try:
    runpy.run_path(str(tool), run_name="__main__")
except SystemExit as leaving:
    code = leaving.code
else:
    code = 0
sys.stdout.flush()
handle.close()
raise SystemExit(code)
"""

_WITHOUT_THE_GUARD = """
import io, pathlib, sys

target = pathlib.Path(sys.argv[1])
count = sys.argv[2]
shard = sys.argv[3]
tool = pathlib.Path(sys.argv[4])

import importlib.util
spec = importlib.util.spec_from_file_location("shards_under_windows", tool)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.line_endings_stay_plain = lambda: False

handle = open(target, "wb")
sys.stdout = io.TextIOWrapper(handle, encoding="utf-8", newline="\\r\\n")
code = module.main(["--of", count, "--shard", shard])
sys.stdout.flush()
handle.close()
raise SystemExit(code)
"""


def test_the_shard_list_holds_no_carriage_return_on_any_platform(
    tmp_path: pathlib.Path, collected_files: "list[str]"
) -> None:
    """The file list the CI step writes must be readable by bash on Windows.

    THE REPRODUCTION. The `tests` job redirects this tool into
    `shard-files.txt` and hands the words to pytest:

        python tools/ci/shards.py --of 5 --shard N > shard-files.txt
        python -m pytest $(cat shard-files.txt)

    The workflow declares `shell: bash` for every platform, and bash
    splits a command substitution on space, tab and newline -- never on
    a carriage return. So if the tool's stdout translates \n to \r\n,
    as a Windows text stream does by default, every path reaches pytest
    with a trailing \r and pytest answers "file or directory not
    found" for each one: all 25 Windows test jobs red, for a reason
    that has nothing to do with any test.

    This runs the tool with exactly that stream and reads the BYTES,
    which is the half `capsys` cannot see -- a capture fixture is
    handed the string and never the file the step actually writes.

    THE MUTATION CHECK, and it is the same reproduction:

        REINSTATE=D-SHARD-CRLF python -m pytest tests/test_ci_shards.py
    """
    count = _count_in_workflow()
    written = tmp_path / "shard-files.txt"
    child = _WINDOWS_STDOUT_CHILD
    if os.environ.get("REINSTATE") == "D-SHARD-CRLF":
        child = _WITHOUT_THE_GUARD
    done = subprocess.run(
        [
            sys.executable,
            "-c",
            child,
            str(written),
            str(count),
            "1",
            str(REPO / "tools" / "ci" / "shards.py"),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stderr
    raw = written.read_bytes()
    assert b"\r" not in raw, (
        "tools/ci/shards.py wrote a carriage return into the file the CI step "
        "hands to pytest. On Windows every path in it would reach pytest with "
        "a trailing \\r and no test would be found. See "
        "shards.line_endings_stay_plain."
    )
    assert raw.decode("utf-8").splitlines() == _plan(count, collected_files)[0]


# -- what those steps leave behind in the checkout ----------------------


def _files_the_sharded_steps_write() -> "list[str]":
    """Every `> name.txt` the shard steps redirect into the checkout root."""
    text = WORKFLOW.read_text(encoding="utf-8")
    found: list[str] = []
    for name in re.findall(r">\s*([A-Za-z0-9_.-]+\.txt)\s*$", text, flags=re.MULTILINE):
        if name not in found:
            found = found + [name]
    return found


def _ignore_lines() -> "list[str]":
    """The .gitignore, one stripped line at a time, with the mutant applied."""
    lines = [
        line.strip()
        for line in IGNORED.read_text(encoding="utf-8").splitlines()
    ]
    if os.environ.get("REINSTATE") == "D-SHARD-ARTEFACTS":
        written = _files_the_sharded_steps_write()
        return [line for line in lines if line not in written]
    return lines


def test_what_the_sharded_steps_write_never_enters_the_repository(
) -> None:
    """A CI step's output file must not be stageable by the next `git add -A`.

    THE REPRODUCTION. The sharded steps write `shard-files.txt` into
    the checkout root, and the coverage job writes `collected.txt`
    beside it. On a runner that folder is thrown away, but
    CONTRIBUTING.md now tells a contributor how to run the same step
    locally, and the landing checklist of this repository opens with
    `git add -A`. A generated list of test files would be staged into a
    tree that is otherwise strict about what enters it, and nothing
    else here would refuse it.

    The assertion is read off the workflow rather than written out, so
    a step that starts redirecting into a third file has to say so
    here.

    THE MUTATION CHECK:

        REINSTATE=D-SHARD-ARTEFACTS python -m pytest tests/test_ci_shards.py
    """
    written = _files_the_sharded_steps_write()
    assert written, (
        ".github/workflows/ci.yml redirects nothing into a .txt file; this "
        "test reads the steps rather than a fixed list, so a step that "
        "stopped doing that should take this case with it"
    )
    ignored = _ignore_lines()
    missing = [name for name in written if name not in ignored]
    assert not missing, (
        f"the CI steps write {missing} into the checkout root and .gitignore "
        "does not name them, so `git add -A` would stage a generated list"
    )
