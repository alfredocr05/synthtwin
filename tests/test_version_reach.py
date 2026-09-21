"""Every call in this tree has to exist on the OLDEST Python the matrix runs.

THE REPRODUCTION. One helper in `tests/test_p4d188_sheet_names_in_the_report.py`
read a report with `Path.read_text(encoding="utf-8", newline="")`. That
keyword reached `Path.read_text` in PYTHON 3.13; this project's floor is
3.10. On 3.10, 3.11 and 3.12 the call is a `TypeError: Path.read_text()
got an unexpected keyword argument 'newline'` raised before the test
proves anything, so six cells of the governed matrix went red on a line
that reads perfectly well on the machine it was written on.

WHY NOTHING ELSE WAS GOING TO CATCH IT. Neither tool that reads this
tree is looking at the floor. `[tool.ruff.lint]` selects `E4`, `E7`,
`E9` and `F` -- pycodestyle's error subset plus pyflakes -- and none of
those rules knows what version a keyword arrived in. mypy runs
`strict` over `src` alone, with no `python_version`, so it checks
against whichever interpreter CI happened to start it with, which is
the NEWEST of the matrix rather than the oldest. The suite itself ran
green on the author's 3.13. So the first reader of the floor was a CI
cell, and this file is the reader that comes before it.

This is the version-in-time twin of `tests/test_p3v4f10_windows_reach.py`,
which asks the same question across PLATFORMS: that file reads the
suite for `os` members some platform of the matrix lacks, this one
reads the whole tree -- tests, tools AND the product -- for standard
library spellings some PYTHON of the matrix lacks.

WHAT IT SETTLES AND WHAT IT DOES NOT. It settles that no spelling in
the tables below reaches a cell that cannot run it. It is NOT a proof
that the tree is 3.10-clean: the tables are what somebody has written
down, and an addition nobody has written down is an addition this
cannot see. Three quarters of the standard library changed between 3.10
and 3.14. The honest guarantee is narrower and worth stating plainly --
this catches a repeat of the defect it was built for, and the classes
of defect nearest to it, and it grows a row each time a new one is
found. Running the suite on 3.10 is the only thing that proves the
whole of it, and that is what the `minimums` job is for.

AND IT READS EACH FILE AS ITS OWN SYNTAX TREE, WHICH IS THE OTHER
LIMIT. `ast.parse` is what both readings below are built on, so what
this guard sees is what the interpreter would RUN. A post-floor
spelling written inside a STRING is invisible to it. The tree holds
four such strings today, all of them `Path.walk` (3.12, against a
floor of 3.10) in the sample modules `tests/test_offline_scan.py`
hands to the offline import scanner:
`test_path_walk_on_error_callback_goes_red`,
`test_a_validated_path_still_obeys_the_callback_slot_rule`,
`test_a_conditional_receiver_goes_red` and
`test_a_boolean_receiver_goes_red`. Nothing is broken by that, and
none of them should be rewritten: those strings are SCANNED by
another tool and never executed, and `Path.walk` is the exact
spelling that tool's callback-slot rule exists to catch -- it is the
one `pathlib.Path` method taking a callable.
`test_the_reading_recognizes_the_shapes_it_claims_to` below carries
SEVEN more, for the same reason -- a guard needs a sample of the thing
it reports -- and the lookup tables above it hold twenty-two more,
since every key of `NAMES_ABOVE_THE_FLOOR` and
`MODULES_ABOVE_THE_FLOOR` is itself a post-floor spelling written as a
string. Thirty-three in the tree, of which the four in
`test_offline_scan.py` are the only ones outside this file. (Counted
again on 2026-09-21 by running both readings below over every string
constant of the folders, ONE-LINE STRINGS INCLUDED: an earlier count
here said "one more" because the harness behind it skipped any string
with no newline in it, which is most of this file's samples.)

THE LIMIT THAT WOULD MATTER is a string of source that IS RUN --
handed to `exec`, `eval` or `compile`, or to `runpy` -- because that
spelling reaches the 3.10 cells while this file says nothing about it.
The tree holds THIRTEEN such calls. They are listed in
`ROUTES_THAT_RUN_SOURCE` below and
`test_the_routes_that_run_a_string_of_source_are_the_ones_named_here`
holds the tree to that list, so a fourteenth cannot arrive unread.
Every one of them runs a COMMITTED FILE of `tools/`, which the folders
below already read:

- `tests/test_oracle_rule_witnesses.py` builds a module with
  `exec(compile(source, ...))`, where `source` is
  `tools/reference/make_generation_reference_vectors.py` carrying one
  `WITNESS_MUTANTS` or `REFUSALS` edit. Those edits are string
  constants of `tests/`, so what the interpreter runs is not the
  committed file alone; all 31 forms of it -- the oracle and its 30
  edits -- were re-read with both readings below on 2026-09-21 and
  hold no post-floor spelling.
- `runpy.run_path` runs the same kind of committed file: twice in
  `tests/`, in the two stage-2 oracle tests, and nine times in
  `tools/`.

A FILE loaded as a module is NOT this limit. The 26
`importlib.util.spec_from_file_location` calls in the folders load
committed files of `tools/` and `tests/`, which this guard reads as
files rather than as strings; their number is pinned below so that a
new loader makes somebody look at what it loads. (A grep for that name
finds 27 lines -- the twenty-seventh is this paragraph.)

THIS PARAGRAPH WAS WRONG ONCE, WHICH IS WHY IT IS NOW A TABLE. It read
"there is no such string in the tree" and offered `spec_from_file_location`
as the reason, when `exec(compile(...))` above is exactly such a
string and the loader calls numbered 26 rather than the 23 claimed.
The conclusion held -- no post-floor spelling is run -- but a reader
redoing the check would have found the author had apparently not
looked. Anyone adding a route to the table has to prove the floor for
what it runs, because this guard cannot.
"""

import ast
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# THE SUPPORTED FLOOR, and the three places that have to agree on it.
# `test_the_floor_is_the_one_every_governing_file_declares` below reads
# each of them rather than trusting this pair of numbers.
FLOOR = (3, 10)
FLOOR_TEXT = "3.10"

# Keyword arguments that a standard library callable of this name began
# accepting AFTER the floor. Keyed by the callable's own name and the
# keyword, because that pair is what a reader of source can see without
# resolving the receiver's type -- the same trade
# `test_p3v4f10_windows_reach.py` makes for `os.<member>`. A project
# function of the same name taking the same keyword would be a false
# report, which is answered by renaming the row's note, not by dropping
# the row.
KEYWORDS_ABOVE_THE_FLOOR = {
    ("read_text", "newline"): ((3, 13), "pathlib.Path.read_text gained newline in 3.13"),
    ("glob", "case_sensitive"): ((3, 12), "pathlib.Path.glob gained case_sensitive in 3.12"),
    ("rglob", "case_sensitive"): ((3, 12), "pathlib.Path.rglob gained case_sensitive in 3.12"),
    ("glob", "recurse_symlinks"): ((3, 13), "pathlib.Path.glob gained recurse_symlinks in 3.13"),
    ("rglob", "recurse_symlinks"): ((3, 13), "pathlib.Path.rglob gained recurse_symlinks in 3.13"),
    ("relative_to", "walk_up"): ((3, 12), "pathlib.PurePath.relative_to gained walk_up in 3.12"),
    ("match", "case_sensitive"): ((3, 12), "pathlib.PurePath.match gained case_sensitive in 3.12"),
    ("is_file", "follow_symlinks"): ((3, 13), "pathlib.Path.is_file gained follow_symlinks in 3.13"),
    ("is_dir", "follow_symlinks"): ((3, 13), "pathlib.Path.is_dir gained follow_symlinks in 3.13"),
    ("rmtree", "onexc"): ((3, 12), "shutil.rmtree gained onexc in 3.12"),
    ("NamedTemporaryFile", "delete_on_close"): (
        (3, 12), "tempfile.NamedTemporaryFile gained delete_on_close in 3.12"),
    ("parse", "optimize"): ((3, 13), "ast.parse gained optimize in 3.13"),
    ("batched", "strict"): ((3, 13), "itertools.batched gained strict in 3.13"),
    ("correlation", "method"): ((3, 12), "statistics.correlation gained method in 3.12"),
    ("TracebackException", "save_exc_type"): (
        (3, 13), "traceback.TracebackException gained save_exc_type in 3.13"),
    # The one row AT OR BELOW the floor, kept so that the version
    # comparison itself is visible working: `shutil.which` has taken
    # `mode` since it arrived in 3.3, so this row never reports.
    ("which", "mode"): ((3, 3), "shutil.which has taken mode since 3.3"),
}

# Whole names that arrived after the floor, spelled `module.member` so
# that the module says which library is meant and no bare name can be
# mistaken for a local one.
NAMES_ABOVE_THE_FLOOR = {
    "pathlib.Path.from_uri": ((3, 13), "3.13"),
    "itertools.batched": ((3, 12), "3.12"),
    "math.sumprod": ((3, 12), "3.12"),
    "random.binomialvariate": ((3, 12), "3.12"),
    "os.process_cpu_count": ((3, 13), "3.13"),
    "glob.translate": ((3, 13), "3.13"),
    "base64.z85encode": ((3, 13), "3.13"),
    "base64.z85decode": ((3, 13), "3.13"),
    "typing.override": ((3, 12), "3.12"),
    "typing.TypeIs": ((3, 13), "3.13"),
    "typing.ReadOnly": ((3, 13), "3.13"),
    "warnings.deprecated": ((3, 13), "3.13"),
    "copy.replace": ((3, 13), "3.13"),
    "enum.StrEnum": ((3, 11), "3.11"),
    "enum.ReprEnum": ((3, 11), "3.11"),
    "datetime.UTC": ((3, 11), "3.11"),
    "hashlib.file_digest": ((3, 11), "3.11"),
    "asyncio.TaskGroup": ((3, 11), "3.11"),
    "csv.QUOTE_STRINGS": ((3, 12), "3.12"),
    "csv.QUOTE_NOTNULL": ((3, 12), "3.12"),
    "inspect.markcoroutinefunction": ((3, 12), "3.12"),
    "unittest.enterModuleContext": ((3, 11), "3.11"),
}

# Modules whose whole existence postdates the floor: importing one at
# all is a collection failure on every cell below it.
MODULES_ABOVE_THE_FLOOR = {
    "tomllib": ((3, 11), "3.11"),
    "sys.monitoring": ((3, 12), "3.12"),
    "annotationlib": ((3, 14), "3.14"),
    "compression": ((3, 14), "3.14"),
}

# Method names that arrived after the floor and that this tree could
# plausibly write. A name is only reported where the receiver is not
# one of the older spellings that has always had it -- `ast.walk` and
# `os.walk` both predate `pathlib.Path.walk` by many years.
METHODS_ABOVE_THE_FLOOR = {
    "walk": ((3, 12), "pathlib.Path.walk arrived in 3.12"),
    "full_match": ((3, 13), "pathlib.PurePath.full_match arrived in 3.13"),
    "is_junction": ((3, 12), "pathlib.Path.is_junction arrived in 3.12"),
    "copy_into": ((3, 14), "pathlib.Path.copy_into arrived in 3.14"),
    "move_into": ((3, 14), "pathlib.Path.move_into arrived in 3.14"),
}
# The receivers that have carried one of those names since long before
# the floor, so a call on them is not the new method at all.
OLDER_OWNERS = {"walk": ("ast", "os", "os.path")}

# The folders this reads. The product, the tests and the tools all run
# on every cell of the matrix, so all three are read.
FOLDERS = ("src", "tests", "tools")

# THE ROUTES THAT RUN A STRING OF SOURCE, by the file holding the call
# and the name it is spelled with. `compile` is matched as the bare
# name, so the tree's fifty-odd `re.compile` calls are not it. Each of
# these runs a committed file of `tools/` -- the module docstring says
# which and why each is covered -- and a route this table does not hold
# is a spelling this guard cannot see, so the test below fails until
# somebody adds it here and proves the floor for what it runs.
ROUTES_THAT_RUN_SOURCE = {
    ("tests/test_oracle_rule_witnesses.py", "compile"): 1,
    ("tests/test_oracle_rule_witnesses.py", "exec"): 1,
    ("tests/test_stage2_datetime_oracle.py", "runpy.run_path"): 1,
    ("tests/test_stage2_grouping_oracle.py", "runpy.run_path"): 1,
    ("tools/provenance/guard_runner.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_2.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_3.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_4.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_5.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_6.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_branch_vectors_7.py", "runpy.run_path"): 1,
    ("tools/reference/make_generation_document_vectors.py", "runpy.run_path"): 1,
}
RUNNING_NAMES = ("exec", "eval", "compile", "runpy.run_path", "runpy.run_module")

# `importlib.util.spec_from_file_location` loads a FILE as a module,
# which is a file this guard already reads -- so it is a count rather
# than a table. The count is here so that a new loader is looked at
# once: if what it loads is a committed file of the folders, move this
# number and say so.
FILES_LOADED_AS_MODULES = 26


def _files() -> "list[pathlib.Path]":
    """Every Python file of the folders this governs, sorted."""
    found: "list[pathlib.Path]" = []
    for folder in FOLDERS:
        for path in sorted((REPO_ROOT / folder).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            found.append(path)
    return found


def _called_name(node: ast.Call) -> str:
    """The spelling of what a call calls: `p.read_text` or `json.loads`."""
    return ast.unparse(node.func)


def calls_above_the_floor(source: str) -> "list[tuple[int, str]]":
    """Every spelling in ``source`` that the floor's Python does not have.

    Three readings in one pass: a keyword some callable only began
    taking later, a dotted name that arrived later, and a method name
    that arrived later on a receiver that is not one of the older
    owners of that name.
    """
    tree = ast.parse(source)
    found: "list[tuple[int, str]]" = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            spelled = _called_name(node)
            last = spelled.rpartition(".")[2]
            for keyword in node.keywords:
                if keyword.arg is None:
                    continue
                row = KEYWORDS_ABOVE_THE_FLOOR.get((last, keyword.arg))
                if row is None or row[0] <= FLOOR:
                    continue
                found.append((node.lineno, f"{spelled}({keyword.arg}=...): {row[1]}"))
            method = METHODS_ABOVE_THE_FLOOR.get(last)
            owner = spelled.rpartition(".")[0]
            if (
                method is not None
                and method[0] > FLOOR
                and "." in spelled
                and owner not in OLDER_OWNERS.get(last, ())
            ):
                found.append((node.lineno, f"{spelled}(): {method[1]}"))
        if isinstance(node, ast.Attribute):
            spelled = ast.unparse(node)
            row = NAMES_ABOVE_THE_FLOOR.get(spelled)
            if row is not None and row[0] > FLOOR:
                found.append((node.lineno, f"{spelled}: it arrived in Python {row[1]}"))
    return found


def imports_above_the_floor(source: str) -> "list[tuple[int, str]]":
    """Every import of a module that did not exist at the floor."""
    tree = ast.parse(source)
    found: "list[tuple[int, str]]" = []
    for node in ast.walk(tree):
        named: "list[str]" = []
        if isinstance(node, ast.Import):
            named = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            named = [node.module or ""]
        for name in named:
            row = MODULES_ABOVE_THE_FLOOR.get(name) or MODULES_ABOVE_THE_FLOOR.get(
                name.partition(".")[0]
            )
            if row is not None and row[0] > FLOOR:
                found.append((node.lineno, f"{name}: the module arrived in Python {row[1]}"))
        # A name imported OUT of a module it only recently joined --
        # `from datetime import UTC` -- is the same defect wearing an
        # import statement, and `calls_above_the_floor` cannot see it
        # because nothing writes the module's name at the point of use.
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                row = NAMES_ABOVE_THE_FLOOR.get(f"{node.module}.{alias.name}")
                if row is not None and row[0] > FLOOR:
                    found.append((
                        node.lineno,
                        f"{node.module}.{alias.name}: it arrived in Python {row[1]}",
                    ))
    return found


def test_no_file_calls_a_spelling_the_oldest_python_lacks() -> None:
    """The whole tree, read for calls the floor's interpreter cannot make."""
    loose = []
    for path in _files():
        source = path.read_text(encoding="utf-8")
        for line, why in calls_above_the_floor(source):
            loose.append(f"{path.relative_to(REPO_ROOT).as_posix()} line {line}: {why}")
    assert not loose, (
        f"these spellings do not exist on Python {FLOOR_TEXT}, which is this "
        "project's declared floor and the interpreter six cells of the CI "
        "matrix run, so those cells raise before the code proves anything: "
        + "; ".join(loose)
        + ". Write the spelling every supported version has -- for the "
        "keyword that caused this file to exist, `path.read_bytes()"
        '.decode("utf-8")` reads exactly the bytes `read_text(newline="")` '
        "reads -- or raise the floor in pyproject.toml, the CI matrix and "
        "requirements-min together."
    )


def test_no_file_imports_a_module_the_oldest_python_lacks() -> None:
    """Imports, which run at collection on every cell."""
    loose = []
    for path in _files():
        source = path.read_text(encoding="utf-8")
        for line, why in imports_above_the_floor(source):
            loose.append(f"{path.relative_to(REPO_ROOT).as_posix()} line {line}: {why}")
    assert not loose, (
        f"these modules do not exist on Python {FLOOR_TEXT}: "
        + "; ".join(loose)
        + ". An import of one fails at collection, taking the whole file "
        "with it and not only the code that wanted it."
    )


def test_the_floor_is_the_one_every_governing_file_declares() -> None:
    """pyproject, the CI matrix and the `minimums` job name the same oldest Python.

    THE FLOOR IS A CLAIM ABOUT WHAT RUNS, so the three files that make
    that claim are read rather than trusted. `pyproject.toml` declares
    it to anyone who installs; the `tests` matrix is what actually runs
    the suite on it; the `minimums` job pins the dependency floors and
    runs on the oldest interpreter as well. A floor raised in one of
    them and left standing in the others is a version nobody tests and
    everybody is promised.
    """
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'requires-python = ">={FLOOR_TEXT}"' in pyproject

    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    block = workflow[workflow.index("  tests:") : workflow.index("  build:")]
    matrix = re.search(r"python-version: \[(.*?)\]", block, flags=re.DOTALL)
    assert matrix is not None, "the tests job no longer states a python-version list"
    versions = sorted(
        tuple(int(part) for part in found.split("."))
        for found in re.findall(r"\d+\.\d+", matrix.group(1))
    )
    assert versions[0] == FLOOR, (
        f"the tests matrix runs {versions[0]} at the bottom while the floor "
        f"here is {FLOOR}"
    )

    minimums = workflow[workflow.index("  minimums:") : workflow.index("  gate:")]
    assert f'python-version: "{FLOOR_TEXT}"' in minimums, (
        "the minimums job must run the oldest supported interpreter: it is "
        "the one job that proves the declared dependency floors and the "
        "declared Python floor together"
    )


def test_the_reading_recognizes_the_shapes_it_claims_to() -> None:
    """Every acceptance and every refusal, spelled out.

    A guard nobody can see working is a guard that can go quiet: if the
    tree stopped containing any of these shapes, the two tests above
    would pass over an empty reading and say nothing.
    """
    # The defect this file was built for, in the spelling it had.
    assert calls_above_the_floor(
        'report.read_text(encoding="utf-8", newline="")\n'
    ) == [(1, 'report.read_text(newline=...): pathlib.Path.read_text gained newline in 3.13')]
    # The repair, which every supported version has.
    assert calls_above_the_floor('report.read_bytes().decode("utf-8")\n') == []
    # A keyword `read_text` has always taken is not a report.
    assert calls_above_the_floor('report.read_text(encoding="utf-8")\n') == []
    # A write is not a read: `Path.write_text` took `newline` in 3.10.
    assert calls_above_the_floor('p.write_text(t, newline="")\n') == []
    # A dotted name that arrived later, wherever it is written.
    assert calls_above_the_floor("itertools.batched(rows, 3)\n") == [
        (1, "itertools.batched: it arrived in Python 3.12")
    ]
    assert calls_above_the_floor("datetime.UTC\n") == [
        (1, "datetime.UTC: it arrived in Python 3.11")
    ]
    assert calls_above_the_floor("datetime.timezone.utc\n") == []
    # A method that arrived later, and the older owners of its name.
    assert calls_above_the_floor("for root, folders, files in folder.walk():\n    pass\n") == [
        (1, "folder.walk(): pathlib.Path.walk arrived in 3.12")
    ]
    assert calls_above_the_floor("for node in ast.walk(tree):\n    pass\n") == []
    assert calls_above_the_floor("for root, folders, files in os.walk(top):\n    pass\n") == []
    # Imports.
    assert imports_above_the_floor("import tomllib\n") == [
        (1, "tomllib: the module arrived in Python 3.11")
    ]
    assert imports_above_the_floor("from tomllib import loads\n") == [
        (1, "tomllib: the module arrived in Python 3.11")
    ]
    assert imports_above_the_floor("import json\nimport pathlib\n") == []
    assert imports_above_the_floor("from datetime import UTC\n") == [
        (1, "datetime.UTC: it arrived in Python 3.11")
    ]
    assert imports_above_the_floor("from datetime import timezone\n") == []
    # The tables are only read where the version is above the floor, so
    # a row at or below it never reports; `shutil.which(mode=...)` is
    # the row that proves the comparison is made.
    assert calls_above_the_floor('shutil.which("git", mode=1)\n') == []


def _source_running_sites() -> "tuple[dict, int]":
    """Census of the running routes, and the count of file loaders."""
    census: "dict[tuple[str, str], int]" = {}
    loaders = 0
    for path in _files():
        relative = path.relative_to(REPO_ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            spelled = _called_name(node)
            if spelled in RUNNING_NAMES:
                key = (relative, spelled)
                census[key] = census.get(key, 0) + 1
            elif spelled == "importlib.util.spec_from_file_location":
                loaders += 1
    return census, loaders


def test_the_routes_that_run_a_string_of_source_are_the_ones_named_here() -> None:
    """The one limit this guard cannot see is held to a list somebody has read.

    THE REVIEW OF 2026-09-21. The docstring said the limit that would
    matter is a string of source that is EXECUTED, said there was no
    such string in the tree, and gave `spec_from_file_location` as the
    reason. A reader who redid the check found `exec(compile(source,
    ...))` in `tests/test_oracle_rule_witnesses.py` -- precisely the
    excluded route -- and eleven `runpy.run_path` calls, none of them
    mentioned. Nothing was broken by it: all 31 forms of the oracle
    that call runs hold no post-floor spelling. What was broken was the
    claim, and a prose claim nobody can redo is worth what this one
    turned out to be worth.

    So the routes are a table now. A new `exec`, `eval`, `compile` or
    `runpy` call fails this until it is added, which is the moment to
    ask what source it runs and whether the floor holds for it.
    """
    census, loaders = _source_running_sites()
    arrived = {key: n for key, n in census.items() if ROUTES_THAT_RUN_SOURCE.get(key) != n}
    gone = {key: n for key, n in ROUTES_THAT_RUN_SOURCE.items() if census.get(key) != n}
    assert not arrived and not gone, (
        "the routes that RUN a string of source have moved. New or changed "
        f"here: {arrived}. Named below and no longer there: {gone}. This "
        "guard reads each file's own syntax tree, so a post-floor spelling "
        "inside a string it runs is invisible to it: add the route to "
        "ROUTES_THAT_RUN_SOURCE and say in the module docstring what it "
        "runs and why the floor holds for it."
    )
    assert loaders == FILES_LOADED_AS_MODULES, (
        f"{loaders} calls to importlib.util.spec_from_file_location, against "
        f"{FILES_LOADED_AS_MODULES} recorded. Each one loads a FILE as a "
        "module: check that this one loads a committed file of src/, tests/ "
        "or tools/ -- which this guard reads -- and then move the number."
    )
