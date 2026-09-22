"""Stage 3, landing 3.1: the default smallest group is 11, and the floor holes close.

THE DEFAULT (owner, 2026-09-22; plan P4-D316). The smallest group a run
uses when nobody asks for another is 11 again, the value it held before
amendment A-P4-37 and the same number as the notice line. It is written
once, `parsing.DEFAULT_SMALL_CELL_FLOOR`, and read by the taxonomy's
settings, the loader, the command line, the reader and the file's
written form. `--smallest-group` below it stays legal and keeps its
alarm.

THE HOLES (plan P4-D317), each measured before it was closed and each
held here by a check that was put back to the old code and seen red:

* `dialect.survey` walks the file again when a trailing-delimiter guess
  breaks, and that walk dropped the floor, so the form it published
  was the default's whatever floor the first walk was asked at. The
  validator's zero-row path settled a checked file with no floor at
  all. An AST check asks every call of every function whose floor
  parameter has a default to pass it.
* `tests/kpi_shapes.describe` read a table at the default floor and
  described it at the one it was asked for.
* A description's blank places, its blank lines counted past the cap
  and its counts of empty records were held to the census line by the
  producer alone. The loader (FD4, FD5) and the publication guard now
  ask the producer's own rule from their side.

THE REPAIR PASS (plans P4-D319 and P4-D321), each part put back to the
old code and seen red:

* the producer published two blank places of one text after one record
  at a raised floor, which FD4 refuses, so the loader refused the
  producer's own file; the places are merged, and one order question is
  asked on every side (section 3);
* sixty-one functions in the tests and tools read at the default beside
  a floor of their own, and the literal-default check asked one name of
  floor parameter only (section 1b and the check above it);
* the zero-row check at the default and the leading and trailing counts
  of empty records had no test that could fail (sections 2c and 2d).
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import pathlib

import pytest

import fixtures
import kpi_shapes as S
from synthtwin import (
    cli,
    contract,
    dialect,
    errors,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

_SOURCE = fixtures.REPO_ROOT / "src" / "synthtwin"


# -- 1. the default ------------------------------------------------------


def test_the_default_smallest_group_is_eleven_wherever_it_is_read() -> None:
    """One number, read in every place a run takes its floor from."""
    assert parsing.DEFAULT_SMALL_CELL_FLOOR == 11
    assert taxonomy.Settings().small_cell_floor == 11
    assert contract.DEFAULT_SMALL_CELL_FLOOR == 11
    assert cli._SMALLEST_GROUP == 11
    # The notice line is a different fact that happens to be the same
    # number again; it did not move.
    assert contract.SMALL_GROUP_NOTICE_LINE == 11
    for function in (reading.read_table, dialect.survey, dialect.settle):
        found = inspect.signature(function).parameters["small_cell_floor"]
        assert found.default == 11, function.__name__


def _functions(
    replaced: "dict[str, str] | None" = None,
) -> "list[tuple[str, ast.FunctionDef]]":
    """Every function of the package, with the module it is in.

    ``replaced`` maps a module's name to text read in place of its file,
    which is how a red check below puts old code back.
    """
    found: "list[tuple[str, ast.FunctionDef]]" = []
    for path in sorted(_SOURCE.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if replaced and path.stem in replaced:
            text = replaced[path.stem]
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                found += [(path.stem, node)]
    return found


def _defaulted_floors(
    node: ast.FunctionDef,
) -> "list[tuple[int | None, str, str]]":
    """Each floor parameter of a function that carries a default.

    ``(position, name, default)``; the position is None for a
    keyword-only parameter.
    """
    arguments = node.args
    positional = arguments.posonlyargs + arguments.args
    defaults: "list[ast.expr | None]" = [None] * (
        len(positional) - len(arguments.defaults)
    )
    defaults += list(arguments.defaults)
    found: "list[tuple[int | None, str, str]]" = []
    for place, (parameter, default) in enumerate(zip(positional, defaults)):
        if "floor" in parameter.arg and default is not None:
            found += [(place, parameter.arg, ast.unparse(default))]
    for parameter, keyword_default in zip(
        arguments.kwonlyargs, arguments.kw_defaults
    ):
        if "floor" in parameter.arg and keyword_default is not None:
            found += [(None, parameter.arg, ast.unparse(keyword_default))]
    return found


# `parsing.census_names_one_row` takes a LINE, not the person's floor:
# left out, it asks at the line of two, which is what every caller
# written before that argument asked, and only the readings whose S13
# reasoning does not hold pass the settings floor (its docstring says
# which). It is the one function whose floor default is meant to be
# used.
_A_LINE_NOT_A_FLOOR = {("parsing", "census_names_one_row")}


def _literal_floor_defaults(replaced: "dict[str, str] | None" = None) -> "list[str]":
    """Every floor parameter whose default is a number of its own."""
    wrong: "list[str]" = []
    for module, node in _functions(replaced):
        if (module, node.name) in _A_LINE_NOT_A_FLOOR:
            continue
        for _place, name, default in _defaulted_floors(node):
            if default != "parsing.DEFAULT_SMALL_CELL_FLOOR":
                wrong += [f"{module}.{node.name}({name}={default})"]
    return wrong


def test_no_floor_parameter_defaults_to_a_number_of_its_own() -> None:
    """EVERY parameter named for a floor defaults to the one default, or to nothing.

    Four `small_cell_floor` parameters defaulted to the literal 1
    (`reading.read_table`, `reading._read_authoritatively`,
    `dialect.survey`, `dialect.settle`), so a caller that left the floor
    out read a file at a floor nobody had chosen since 2026-09-22. The
    check asked that one name only, and `reading._read_workbook_table`'s
    `floor` defaulted back to 1 went unseen (the repair pass of landing
    3.1, mutation E20), beside seventeen `floor=0` and `floor=1`
    defaults in `generation` and `validation` that every caller passes.
    Those are gone where the signature allows it and name the default
    where an earlier parameter's default keeps one.
    """
    assert _literal_floor_defaults() == []


def test_the_literal_default_check_is_not_vacuous() -> None:
    """RED CHECK: the workbook reader's floor defaulted back to 1 (E20)."""
    source = (_SOURCE / "reading.py").read_text(encoding="utf-8")
    shipped = "    floor: int = parsing.DEFAULT_SMALL_CELL_FLOOR,\n) -> Table:"
    assert source.count(shipped) == 1
    old = source.replace(shipped, "    floor: int = 1,\n) -> Table:")
    found = _literal_floor_defaults({"reading": old})
    assert found == ["reading._read_workbook_table(floor=1)"], found


def _omissions(replaced: "dict[str, str] | None" = None) -> "list[str]":
    """Every call that leaves out a floor its function would default.

    ``replaced`` maps a module's name to text read in place of its file,
    which is how the red check below puts old code back.
    """
    defaulted: "dict[tuple[str, str], tuple[int | None, str, str]]" = {}
    trees: "dict[str, ast.Module]" = {}
    for path in sorted(_SOURCE.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if replaced and path.stem in replaced:
            text = replaced[path.stem]
        tree = ast.parse(text)
        trees[path.stem] = tree
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                for found in _defaulted_floors(node):
                    defaulted[(path.stem, node.name)] = found
    omitted: "list[str]" = []
    for module, tree in sorted(trees.items()):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            called = node.func
            if isinstance(called, ast.Name):
                key = (module, called.id)
            elif isinstance(called, ast.Attribute) and isinstance(
                called.value, ast.Name
            ):
                key = (called.value.id, called.attr)
            else:
                continue
            if key not in defaulted or key in _A_LINE_NOT_A_FLOOR:
                continue
            place, name, default = defaulted[key]
            passed = (
                any(keyword.arg in (name, None) for keyword in node.keywords)
                or (place is not None and len(node.args) > place)
                or any(isinstance(given, ast.Starred) for given in node.args)
            )
            if not passed:
                omitted += [
                    f"{module}.py:{node.lineno} calls {key[0]}.{key[1]} "
                    f"without {name} (default {default})"
                ]
    return omitted


def test_every_call_passes_the_floor_its_function_would_default() -> None:
    """The class of hole P4-D317 closed twice, asked of the whole package.

    `dialect.survey`'s retry and `validation._surveyed_quietly` each
    called a function whose floor parameter has a default, and left the
    floor out, so each read the file at a floor the person had not
    asked for. A floor that is meant to reach a function is passed to
    it; a default is for a caller outside the package.
    """
    assert _omissions() == []


def test_the_call_check_is_not_vacuous() -> None:
    """RED CHECK: each old call, put back into the text the check reads."""
    retry = (_SOURCE / "dialect.py").read_text(encoding="utf-8")
    passed = (
        "                small_cell_floor,\n            )\n"
        "        raise errors.ProfileError(\n            errors.ragged_rows("
    )
    assert retry.count(passed) == 1
    old_retry = retry.replace(
        passed,
        "            )\n        raise errors.ProfileError(\n            errors.ragged_rows(",
    )
    found = _omissions({"dialect": old_retry})
    assert len(found) == 1, found
    assert "calls dialect.survey without small_cell_floor" in found[0]
    quiet = (_SOURCE / "validation.py").read_text(encoding="utf-8")
    settled = (
        "        return dialect.settle(\n"
        "            text, encoding, marked, not headed, \"\", "
        "small_cell_floor=floor\n        )\n"
    )
    assert quiet.count(settled) == 1
    old_quiet = quiet.replace(
        settled,
        "        return dialect.settle(text, encoding, marked, not headed, \"\")\n",
    )
    found = _omissions({"validation": old_quiet})
    assert len(found) == 1, found
    assert "calls dialect.settle without small_cell_floor" in found[0]


# -- 1b. the same hole in the tests and the tools ----------------------
#
# THE KPI SHAPES WERE ONE OF SIXTY-TWO (the repair pass of landing 3.1).
# `tests/kpi_shapes.describe` read a table at the default and described
# it at the floor it was asked for, and P4-D317 closed that one site;
# sixty-one test helpers and three tool drivers did the same, each
# building `taxonomy.Settings(small_cell_floor=...)` and calling
# `reading.read_table` with no floor -- since the default became 11, a
# floor-one description in any of them carried a file's form read at
# eleven. The package check above could not see them: it reads `src`.
# This one reads `tests` and `tools`, and asks the narrower question the
# hole is made of: in a function (or a script's top level) that names a
# floor for a description, every call of a package function whose floor
# parameter has a default passes a floor too. A call at the default in a
# scope that names none reads and describes at the same floor, and is
# left alone.

_CALLERS = (
    sorted((fixtures.REPO_ROOT / "tests").glob("*.py"))
    + sorted((fixtures.REPO_ROOT / "tools").rglob("*.py"))
)
_PACKAGE_MODULES = {path.stem for path in _SOURCE.glob("*.py")}


def _package_defaults() -> "dict[str, dict[str, tuple[int | None, str]]]":
    """Module -> function -> (position, name) of each defaulted floor."""
    found: "dict[str, dict[str, tuple[int | None, str]]]" = {}
    for module, node in _functions():
        if (module, node.name) in _A_LINE_NOT_A_FLOOR:
            continue
        for place, name, _default in _defaulted_floors(node):
            found.setdefault(module, {})[node.name] = (place, name)
    return found


def _names_a_floor(scope: "list[ast.AST]") -> bool:
    """Whether a scope builds settings with a floor of its own."""
    for top in scope:
        for node in ast.walk(top):
            if not isinstance(node, ast.Call):
                continue
            called = node.func
            name = (
                called.attr
                if isinstance(called, ast.Attribute)
                else called.id if isinstance(called, ast.Name) else ""
            )
            if name == "Settings" and any(
                keyword.arg == "small_cell_floor" for keyword in node.keywords
            ):
                return True
    return False


def _scopes(tree: ast.Module) -> "list[tuple[str, list[ast.AST]]]":
    """Each function of a file, and the file's own top level, as scopes."""
    scopes: "list[tuple[str, list[ast.AST]]]" = [
        (
            "(top level)",
            [
                statement
                for statement in tree.body
                if not isinstance(
                    statement,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                )
            ],
        )
    ]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes += [(node.name, [node])]
    return scopes


def _reads_at_another_floor(
    replaced: "dict[str, str] | None" = None,
) -> "list[str]":
    """Every call in tests and tools that reads at the default beside a floor.

    ``replaced`` maps a file's path relative to the repository to text
    read in place of it, which is how the red check puts old code back.
    """
    defaults = _package_defaults()
    found: "list[str]" = []
    for path in _CALLERS:
        where = path.relative_to(fixtures.REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if replaced and where in replaced:
            text = replaced[where]
        tree = ast.parse(text)
        # A bare name is a package function only where the file imports
        # it from the package under that name.
        imported: "dict[str, str]" = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and (
                node.module.startswith("synthtwin.")
            ):
                module = node.module.split(".", 1)[1]
                for alias in node.names:
                    imported[alias.asname or alias.name] = module
        for scope_name, scope in _scopes(tree):
            if not _names_a_floor(scope):
                continue
            for top in scope:
                for node in ast.walk(top):
                    if not isinstance(node, ast.Call):
                        continue
                    called = node.func
                    if isinstance(called, ast.Attribute) and isinstance(
                        called.value, ast.Name
                    ):
                        module, function = called.value.id, called.attr
                    elif isinstance(called, ast.Name) and called.id in imported:
                        module, function = imported[called.id], called.id
                    else:
                        continue
                    if module not in _PACKAGE_MODULES:
                        continue
                    if function not in defaults.get(module, {}):
                        continue
                    place, name = defaults[module][function]
                    passed = (
                        any(keyword.arg in (name, None) for keyword in node.keywords)
                        or (place is not None and len(node.args) > place)
                        or any(isinstance(given, ast.Starred) for given in node.args)
                    )
                    if not passed:
                        found += [
                            f"{where}:{node.lineno} ({scope_name}) calls "
                            f"{module}.{function} without {name}"
                        ]
    return sorted(set(found))


def test_no_test_or_tool_reads_at_the_default_beside_a_floor_of_its_own() -> None:
    """The hole P4-D317 closed in `kpi_shapes`, asked of every test and tool."""
    assert _reads_at_another_floor() == []


def test_the_test_and_tool_check_is_not_vacuous() -> None:
    """RED CHECK: the KPI shapes' old read, and one of the sixty-one, put back."""
    shapes = (fixtures.REPO_ROOT / "tests" / "kpi_shapes.py").read_text(
        encoding="utf-8"
    )
    passed = "            small_cell_floor=settings.small_cell_floor,\n"
    assert shapes.count(passed) == 1
    found = _reads_at_another_floor(
        {"tests/kpi_shapes.py": shapes.replace(passed, "")}
    )
    assert len(found) == 1, found
    assert "tests/kpi_shapes.py" in found[0] and "(describe)" in found[0]
    assert "reading.read_table without small_cell_floor" in found[0]
    loader = (fixtures.REPO_ROOT / "tests" / "test_contract_loader.py").read_text(
        encoding="utf-8"
    )
    passed = "    table = reading.read_table(str(path), small_cell_floor=1)\n"
    assert loader.count(passed) == 1
    found = _reads_at_another_floor(
        {
            "tests/test_contract_loader.py": loader.replace(
                passed, "    table = reading.read_table(str(path))\n"
            )
        }
    )
    assert len(found) == 1, found
    assert "(at_a_floor_of_one)" in found[0]


# -- 2a. the retry after a broken trailing-delimiter guess ---------------


def _trailing_then_broken() -> str:
    """A header ending in a delimiter, rows that follow it, then one that doesn't.

    The first walk reads `a,b,` as two names and a trailing delimiter,
    record 30 breaks that guess, and `survey` walks the file again as
    three columns. One blank line stands after record 20.
    """
    rows = ["a,b,"]
    for index in range(1, 60):
        rows += [f"{index},{index * 2}," if index != 30 else "30,60,x"]
    lines = rows[:21] + [""] + rows[21:]
    return "\n".join(lines) + "\n"


def test_the_retry_after_a_broken_trailing_delimiter_keeps_the_floor() -> None:
    """P4-D317: the second walk publishes the form at the floor it was asked at.

    A FLOOR OF ONE ON PURPOSE: at the default the lone blank place is
    withheld by both walks, so only a floor other than the default shows
    which floor the second walk used. Measured with the retry's floor
    left out: the floor-one survey published no blank place.
    """
    text = _trailing_then_broken()
    kept = dialect.settle(text, "utf-8", False, False, "t.csv", small_cell_floor=1)
    assert len(kept.header) == 3, "the second walk must be the one read"
    assert kept.form.blank_lines == (
        dialect.BlankPlace(after=20, lines=1, text=""),
    )
    held = dialect.settle(text, "utf-8", False, False, "t.csv")
    assert held.form.blank_lines == ()


# -- 2a. the validator's zero-row path ----------------------------------


def test_a_zero_row_check_surveys_the_file_at_the_description_floor(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D317: the degenerate report reads the checked file's form at the floor.

    A FLOOR OF ONE ON PURPOSE, for the reason above. The description is
    the zero-row form of a floor-one description with one blank line
    after its header, which a floor of one publishes; the checked file
    is exactly that. Measured with `_surveyed_quietly` settling at no
    floor: the checked file was read at the default, its blank place
    withheld, and `bytes.blank-lines` MISSED a file that is the
    description's own.
    """
    described = S.describe(tmp_path, "t", "a,b\n1,2\n3,4\n", floor=1)
    zero = fixtures.zero_rows(described.loaded)
    form = zero.source.dialect
    blank = dialect.BlankPlace(after=0, lines=1, text="")
    ended = dialect.EndingRun(
        ending=form.line_endings[0].ending,
        lines=form.line_endings[0].lines + 1,
    )
    zero = dataclasses.replace(
        zero,
        source=dataclasses.replace(
            zero.source,
            dialect=dataclasses.replace(
                form, blank_lines=(blank,), line_endings=(ended,)
            ),
        ),
    )
    checked = fixtures.write(tmp_path, "checked.csv", "a,b\n\n")
    outcome = validation.measure(zero, f"{checked}")
    verdicts = {check.subcheck: check.verdict for check in outcome.checks}
    assert verdicts["bytes.blank-lines"] == validation.HELD


# -- 2b. the KPI shapes' own reader --------------------------------------


def _one_blank_line() -> str:
    lines = ["record,reading"]
    for index in range(1, 121):
        lines += [f"{index},{(index * 7) % 50}.5"]
        if index == 57:
            lines += [""]
    return "\n".join(lines) + "\n"


def test_the_kpi_shapes_read_a_table_at_the_floor_they_describe_it_at(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D317: `kpi_shapes.describe` hands the reader the floor it describes at.

    A floor of one keeps a lone blank line and the default withholds it,
    so a description at one read at the default published a form no
    description at one publishes. Measured with the reader's floor left
    out: the floor-one description published no blank place.
    """
    at_one = S.describe(tmp_path / "one", "t", _one_blank_line(), floor=1)
    assert at_one.document["source"]["dialect"]["blank_lines"] == [
        {"after": 57, "lines": 1, "text": ""}
    ]
    shipped = S.describe(tmp_path / "default", "t", _one_blank_line())
    assert shipped.document["source"]["dialect"]["blank_lines"] == []


# -- 2c. the loader and the guard hold the file's form to the line ------


def _numbers(count: int) -> str:
    """``count`` records of two columns, every cell different."""
    lines = ["record,reading"]
    for index in range(1, count + 1):
        lines += [f"{index},{index}.25"]
    return "\n".join(lines) + "\n"


def _document_at(
    folder: pathlib.Path, text: str, floor: "int | None" = None
) -> dict:
    """A producer's description of ``text``, before it is written.

    The document itself and not its JSON: the publication guard asks
    every sentence to be one this package wrote from an enumerated form,
    and a sentence read back from JSON is text. It passes the guard as
    the producer built it, so a refusal after an edit is the edit's.
    """
    described = S.describe(folder, "t", text, floor=floor)
    profile.check_publication(described.document)
    return described.document


def _guard_refuses(document: dict, key: str) -> None:
    """The publication guard refuses the document, at the key edited."""
    with pytest.raises(errors.ProfileError) as refused:
        profile.check_publication(document)
    assert key in f"{refused.value}", f"{refused.value}"


def _loaded(folder: pathlib.Path, document: dict) -> "contract.Profile":
    written = fixtures.write_profile(folder, "edited-profile.json", document)
    return contract.load_profile(f"{written}")


def _with_blank_places(document: dict, places: "list[dict]") -> dict:
    """The same description with blank places added and their lines counted."""
    form = document["source"]["dialect"]
    assert form["blank_lines"] == [] and len(form["line_endings"]) == 1
    form["blank_lines"] = places
    added = 0
    for place in places:
        added += place["lines"]
    form["line_endings"][0]["lines"] += added
    return document


def test_the_loader_refuses_a_lone_blank_place_at_the_default_floor(
    tmp_path: pathlib.Path,
) -> None:
    """FD4: one place names one record position (`{after: 57, lines: 1}`)."""
    document = _with_blank_places(
        _document_at(tmp_path, _numbers(120)),
        [{"after": 57, "lines": 1, "text": ""}],
    )
    with pytest.raises(errors.ProfileError) as refused:
        _loaded(tmp_path, document)
    said = f"{refused.value}"
    assert "FD4" in said and "the line is 11" in said
    _guard_refuses(document, "blank_lines")


def test_the_loader_refuses_a_blank_form_fewer_places_wear(
    tmp_path: pathlib.Path,
) -> None:
    """FD4: twelve places clear the count, and a form one of them wears does not."""
    places = [
        {"after": index * 5, "lines": 1, "text": ""} for index in range(1, 12)
    ]
    places += [{"after": 57, "lines": 1, "text": " "}]
    document = _with_blank_places(
        _document_at(tmp_path, _numbers(120)), places
    )
    with pytest.raises(errors.ProfileError) as refused:
        _loaded(tmp_path, document)
    assert "FD4" in f"{refused.value}"
    _guard_refuses(document, "blank_lines")
    # ...and the same twelve places wearing one form load.
    places[11] = {"after": 57, "lines": 1, "text": ""}
    fine = _with_blank_places(_document_at(tmp_path / "fine", _numbers(120)), places)
    profile.check_publication(fine)
    _loaded(tmp_path / "fine", fine)


def test_the_loader_refuses_blank_lines_counted_below_the_line(
    tmp_path: pathlib.Path,
) -> None:
    """FD4: past the cap, the count stands only where the places reach the line.

    A floor of a hundred is the only kind at which this can bite, since
    the count stands only past 64 places.
    """
    document = _document_at(tmp_path, _numbers(200), floor=100)
    form = document["source"]["dialect"]
    form["blank_lines_spread"] = {"first": 1, "last": 70, "lines": 70, "text": ""}
    form["line_endings"][0]["lines"] += 70
    with pytest.raises(errors.ProfileError) as refused:
        _loaded(tmp_path, document)
    said = f"{refused.value}"
    assert "FD4" in said and "the line is 100" in said
    _guard_refuses(document, "blank_lines_spread")


def _absent_in_each_column(count: int) -> str:
    """Two columns, each with a few absent cells of its own."""
    lines = ["record,reading"]
    for index in range(1, count + 1):
        record = "" if index % 30 == 0 else f"{index}"
        reading_text = "" if index % 40 == 0 else f"{index}.25"
        lines += [f"{record},{reading_text}"]
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("which", ["leading", "interior", "trailing"])
def test_the_loader_refuses_an_empty_row_count_below_the_line(
    tmp_path: pathlib.Path, which: str
) -> None:
    """FD5: `empty_rows.interior 1` counts one record of the table.

    EACH OF THE THREE COUNTS, not the interior one alone (the repair pass
    of landing 3.1): the loader's FD5 loop cut to the interior count and
    the guard's `leading` or `trailing` rule put back to a plain count
    each survived every test while only `interior` was asked (mutations
    E21, E22 and E19 of that landing's review). A leading or trailing
    count of one names the first or the last record as surely.
    """
    document = _document_at(tmp_path, _absent_in_each_column(120))
    document["source"]["dialect"]["empty_rows"][which] = 1
    with pytest.raises(errors.ProfileError) as refused:
        _loaded(tmp_path, document)
    said = f"{refused.value}"
    assert "FD5" in said and "the line is 11" in said
    _guard_refuses(document, "empty_rows")
    with pytest.raises(errors.ProfileError) as guarded:
        profile.check_publication(document)
    assert which in f"{guarded.value}", f"{guarded.value}"


def test_a_floor_of_one_still_keeps_the_files_form(tmp_path: pathlib.Path) -> None:
    """A FLOOR OF ONE ON PURPOSE: what the 2026-09-18 gate keeps, it keeps.

    At a floor of one the column censuses publish a level of one row, so
    the file's own form is not held to a stricter standard: a lone blank
    line and a lone empty record are published and load.
    """
    lines = _absent_in_each_column(120).split("\n")
    lines[58] = ","
    lines = lines[:58] + [""] + lines[58:]
    document = _document_at(tmp_path, "\n".join(lines), floor=1)
    form = document["source"]["dialect"]
    assert len(form["blank_lines"]) == 1
    assert form["empty_rows"]["interior"] == 1
    profile.check_publication(document)
    _loaded(tmp_path, document)


# -- 2d. the zero-row check at the default -------------------------------


def test_a_zero_row_check_at_the_default_reads_empty_records_at_the_default(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D317 at the SHIPPED floor, which the floor-one test above cannot see.

    Three records holding nothing are a count below the census line of
    11, so a file read at the default publishes nought of them -- the
    count the zero-row description itself publishes -- and the only rule
    such a file breaks is `bytes.zero-row-form`, which asks for a header
    and nothing else. Read at a floor of one the same three records are
    counted, and `bytes.empty-rows` is missed as well. With
    `_surveyed_quietly` settling at a floor of one whatever the
    description's (mutation E6 of the repair pass of landing 3.1), the
    default-floor half misses `bytes.empty-rows` too, and only the check
    that reads the text of the call went red before this test.
    """
    for floor, missed in (
        (None, ["bytes.zero-row-form"]),
        (1, ["bytes.empty-rows", "bytes.zero-row-form"]),
    ):
        folder = tmp_path / f"floor-{floor}"
        described = S.describe(folder, "t", "a,b\n1,2\n3,4\n", floor=floor)
        zero = fixtures.zero_rows(described.loaded)
        assert zero.source.dialect.empty_rows_interior == 0
        checked = fixtures.write(folder, "checked.csv", "a,b\n,\n,\n,\n")
        outcome = validation.measure(zero, f"{checked}")
        found = sorted(
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        )
        assert found == missed, (floor, found)


# -- 3. two places of one form at one record (plan P4-D319) --------------


def _double_spaced(record: int = 17) -> str:
    """The skeptic's shape: 30 records each followed by a blank line.

    Record ``record`` is followed by a line of three spaces and THEN the
    blank line, so its place is two runs of different text.
    """
    lines = ["id,site,value"]
    for index in range(1, 31):
        lines += [f"{index},{'north' if index % 2 else 'south'},{index * 3}"]
        lines += ["   ", ""] if index == record else [""]
    return "\n".join(lines) + "\n"


def _places(*triples: "tuple[int, int, str]") -> "list[dialect.BlankPlace]":
    return [
        dialect.BlankPlace(after=after, lines=lines, text=text)
        for after, lines, text in triples
    ]


def test_an_absorbed_place_is_merged_into_the_place_it_joins() -> None:
    """P4-D319: the rare spaced line takes the commonest form, and joins its neighbour.

    Derived from the rule, place by place. Thirty places of one blank
    line and one of three spaces after record 17, just before the blank
    line after record 17: the spaced form is worn by one place, fewer
    than 11, so it is written as the commonest form `(1, "")`. Two places
    of one text then stand after record 17, and a file written that way
    reads as ONE place of two lines -- so they are merged. That place
    wears `(2, "")`, a form of one place, and the rule asked again writes
    it as the commonest, one line. Thirty places of one line remain;
    one line of the file's thirty-one is withheld. Before P4-D319 the
    rule stopped after its first step and published `(17, 1, "")`
    twice, which invariant FD4 refuses.
    """
    places = [(index, 1, "") for index in range(1, 17)]
    places += [(17, 1, "   "), (17, 1, "")]
    places += [(index, 1, "") for index in range(18, 31)]
    found = _places(*places)
    told = dialect.blank_places_disclosed(found, 11)
    assert told == _places(*[(index, 1, "") for index in range(1, 31)])
    assert dialect.blank_lines_withheld(found, 11) == 1
    assert dialect.blank_places_broken(told, 11) == ""
    # ...and where the merged form is one the line allows, it stays
    # merged: eleven places of two lines beside it keep `(17, 2, "")`.
    places = [(index, 1, "") for index in range(1, 12)]
    places += [(index, 2, "") for index in range(12, 17)]
    places += [(17, 1, "   "), (17, 1, "")]
    places += [(index, 2, "") for index in range(18, 24)]
    told = dialect.blank_places_disclosed(_places(*places), 11)
    assert _places((17, 2, "")) == [place for place in told if place.after == 17]
    assert dialect.blank_places_broken(told, 11) == ""
    # ...and at a floor of one nothing moves at all.
    assert dialect.blank_places_disclosed(found, 1) == found


def test_the_rule_is_a_fixed_point_the_loader_accepts() -> None:
    """Seeded: whatever the producer publishes, the loader's own question accepts.

    3,000 lists of places a file can hold -- in file order, runs of one
    text at one record -- at floors 2, 5, 11 and 20. What the rule
    returns, it returns unchanged when asked again; no two places it
    returns break `dialect.blank_place_follows`; the loader's question,
    `blank_places_broken`, finds nothing; and the lines it withholds are
    the difference between the two lists. Measured with the rule's
    first step alone, as it stood before P4-D319: 7,471 of the 12,000
    broke the order.
    """
    import random

    draw = random.Random(20260922)
    texts = ["", "", "", " ", "  ", "\t"]
    for trial in range(3000):
        places: "list[dialect.BlankPlace]" = []
        after = 0
        for _place in range(draw.randrange(0, 40)):
            if not places or draw.random() < 0.7:
                after = after + draw.randrange(1, 4)
            text = draw.choice(texts)
            if places and places[-1].after == after and places[-1].text == text:
                continue
            places += [
                dialect.BlankPlace(
                    after=after, lines=draw.choice([1, 1, 1, 2, 3]), text=text
                )
            ]
        for floor in (2, 5, 11, 20):
            told = dialect.blank_places_disclosed(places, floor)
            assert dialect.blank_places_disclosed(told, floor) == told, (trial, floor)
            assert all(
                dialect.blank_place_follows(told[index - 1], told[index])
                for index in range(1, len(told))
            ), (trial, floor, told)
            assert dialect.blank_places_broken(told, floor) == "", (trial, floor)
            kept = sum(place.lines for place in told)
            held = sum(place.lines for place in places)
            assert dialect.blank_lines_withheld(places, floor) == held - kept


def test_the_guard_and_the_loader_ask_the_same_order(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D319: two places of one text at one record are refused on both sides.

    AT A FLOOR OF ONE TOO, where the census line is not asked: the order
    is a fact about how a file is read, not a disclosure rule. The guard
    reaches the loader's rule only through `dialect.blank_places_broken`,
    which asked no order before this, so `profile` could write what the
    loader then refused as a file changed since it was written.
    """
    for floor, places in (
        (1, [{"after": 57, "lines": 1, "text": ""}] * 2),
        (
            None,
            [{"after": index * 5, "lines": 1, "text": ""} for index in range(1, 12)]
            + [{"after": 55, "lines": 1, "text": ""}],
        ),
    ):
        folder = tmp_path / f"floor-{floor}"
        document = _with_blank_places(
            _document_at(folder, _numbers(120), floor=floor), places
        )
        with pytest.raises(errors.ProfileError) as refused:
            _loaded(folder, document)
        assert "FD4" in f"{refused.value}"
        _guard_refuses(document, "blank_lines")
    assert "file order" in dialect.blank_places_broken(
        _places((57, 1, ""), (57, 1, "")), 1
    )


def test_the_double_spaced_file_round_trips_at_the_default(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's minimal shape through the command line, at the default.

    `profile`, `generate` and `validate` each exit 0 -- before P4-D319
    `generate` and `validate` exited 1, refusing the producer's own
    description as a file changed since it was written -- and the real
    table validates against it too. The description publishes the
    thirty places the rule above derives, one per record.
    """
    from tests.test_stage2_round_trip import _exit_of

    table = fixtures.write(tmp_path, "t.csv", _double_spaced())
    assert _exit_of(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    written = tmp_path / "t-profile.json"
    places = contract.load_profile(f"{written}").source.dialect.blank_lines
    assert [(place.after, place.lines, place.text) for place in places] == [
        (index, 1, "") for index in range(1, 31)
    ]
    assert _exit_of(["generate", f"{written}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    assert _exit_of(["validate", f"{written}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    (tmp_path / "real").mkdir()
    assert _exit_of(
        ["validate", f"{written}", "--twin", f"{table}", "--out-dir",
         f"{tmp_path / 'real'}", "--replace"]
    ) == 0


def _blank_heavy(draw: "object", columns: int) -> str:
    """One seeded file heavy in blank lines, the skeptic's fuzz recipe."""
    import random

    assert isinstance(draw, random.Random)
    out = ["h" + ",h".join(str(column) for column in range(columns))]
    for index in range(draw.randrange(15, 120)):
        cells = [str(index)] + [
            str(draw.randrange(0, 20)) if draw.random() > 0.05 else ""
            for _column in range(columns - 1)
        ]
        out += [",".join(cells)]
        if draw.random() < draw.choice([0.12, 0.5, 1.0]):
            out += [
                draw.choice(["", "", "", "", " ", "  ", "\t"])
                for _line in range(draw.choice([1, 1, 1, 2, 3]))
            ]
    return "\n".join(out) + "\n"


def test_blank_heavy_files_describe_load_and_generate_at_the_default(
    tmp_path: pathlib.Path,
) -> None:
    """Seeded fuzz, small enough for the suite: forty files at the default.

    Each is described by the real producer, loaded by the real loader and
    built into a twin, and the twin's blank lines are measured against
    the description. Measured with the rule's first step alone, as it
    stood before P4-D319, on this recipe and seed: 27 of the 40
    descriptions were refused by their own loader under FD4.
    """
    import random

    draw = random.Random(7)
    for trial in range(40):
        text = _blank_heavy(draw, draw.choice([2, 3, 4]))
        described = S.describe(tmp_path / f"{trial}", "t", text)
        twin = S.twin_text(described, trial)
        outcome = S.measure(described, twin, "twin.csv")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
            and check.subcheck.startswith("bytes.")
        ]
        assert missed == [], (trial, missed)
