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


def _functions() -> "list[tuple[str, ast.FunctionDef]]":
    """Every function of the package, with the module it is in."""
    found: "list[tuple[str, ast.FunctionDef]]" = []
    for path in sorted(_SOURCE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
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


def test_no_smallest_group_parameter_defaults_to_a_number_of_its_own() -> None:
    """A `small_cell_floor` parameter's default is the one default.

    Four of them defaulted to the literal 1 (`reading.read_table`,
    `reading._read_authoritatively`, `dialect.survey`, `dialect.settle`),
    so a caller that left the floor out read a file at a floor nobody
    had chosen since 2026-09-22.
    """
    wrong = []
    for module, node in _functions():
        for _place, name, default in _defaulted_floors(node):
            if name == "small_cell_floor" and default != "parsing.DEFAULT_SMALL_CELL_FLOOR":
                wrong += [f"{module}.{node.name}({name}={default})"]
    assert not wrong, wrong


# `parsing.census_names_one_row` takes a LINE, not the person's floor:
# left out, it asks at the line of two, which is what every caller
# written before that argument asked, and only the readings whose S13
# reasoning does not hold pass the settings floor (its docstring says
# which). It is the one function whose floor default is meant to be
# used.
_A_LINE_NOT_A_FLOOR = {("parsing", "census_names_one_row")}


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


def test_the_loader_refuses_an_empty_row_count_below_the_line(
    tmp_path: pathlib.Path,
) -> None:
    """FD5: `empty_rows.interior 1` counts one record of the table."""
    document = _document_at(tmp_path, _absent_in_each_column(120))
    document["source"]["dialect"]["empty_rows"]["interior"] = 1
    with pytest.raises(errors.ProfileError) as refused:
        _loaded(tmp_path, document)
    said = f"{refused.value}"
    assert "FD5" in said and "the line is 11" in said
    _guard_refuses(document, "empty_rows")


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
