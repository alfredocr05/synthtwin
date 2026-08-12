"""The line endings of a description a test writes, on every platform.

WHAT HAPPENED. Every Windows job of this suite failed while every macOS
and Linux job passed, on one refusal:

    The description at ...date_only.json is not in the exact form
    synthtwin writes: written out again, it does not come out the same.

Nothing in the product was wrong, and that is the point. The writer
fixes the line ending rather than leaving it to the platform, so a
description synthtwin writes is the same bytes everywhere (plan D12);
the loader writes the parsed document out again and compares the bytes,
so it refuses a file it cannot prove synthtwin wrote. Both behaved
exactly as specified. The TEST was wrong: it wrote the description with
``write_text(text, encoding="utf-8")`` and no ``newline`` argument, so
Python's text mode translated every line ending to the platform's own
and left a file that on Windows -- and only on Windows -- the loader had
to refuse.

WHY A GUARD RATHER THAN TWENTY-THREE REPAIRS. Twenty-three test modules
each wrote a description of their own. Repairing them one at a time
leaves the same hole open for the twenty-fourth, and the hole is
invisible on the machine its author works on: on macOS and Linux the
wrong line of Python writes exactly the right bytes, so the defect is
undetectable until it reaches a platform nobody runs locally. So the
bytes are decided in ONE place -- `fixtures.write_profile`, whose
docstring carries the guarantee -- and this file reads the source of
every test module and turns red when a description is written anywhere
else with its line ending left to the platform.

HOW WIDE THE RULE IS DRAWN, and why wider than a description. "This
file is a profile document" is not a question source text can be asked,
so the rule is drawn around what it can be asked: a write whose text
comes from the canonical serializer, and a write whose target is named
as a `.json` file. That takes in a few files that are not descriptions
at all -- a signed attestation, a stand-in left in the way of a run --
and asks each of them for one keyword argument they could have done
without. It is the cheap side of the trade: what the guard asks for is
never wrong, and the file it fails to ask turns a platform red that
nobody can reproduce locally.

WHAT THIS FILE CHECKS, and it states the whole of it:

1. Every ``write_text`` call in the suite that writes a description --
   one whose text comes from the canonical serializer, or whose target
   names a `.json` file -- passes an explicit ``newline``.
2. The only module that composes description bytes itself, instead of
   asking the fixture for them, is the one whose whole subject is the
   refusal of bytes synthtwin would never have written.
3. Every module that hands the loader a description asks the fixture for
   it. Without this the first two tests could go quiet by matching
   nothing at all.
4. The detector is put through source carrying the exact original defect
   and source without it, so a rule that has stopped recognizing a
   description cannot pass this file in silence.
5. The fixture's bytes are the product's bytes, compared byte for byte
   against `writing.write_text_file` for the same document.
6. A description whose lines end the Windows way is refused, with the
   message the Windows jobs printed. That is the property all of the
   above exists to keep from reaching a person.

WHAT IT DOES NOT CHECK. Only ``write_text`` is read. A description
written through ``open`` would pass unnoticed here; nothing in the suite
writes one that way, and the fixture is the door every test now uses.
"""

import ast
import pathlib

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    errors,
    profile,
    reading,
    taxonomy,
    writing,
)

TESTS = pathlib.Path(__file__).resolve().parent

# The one place a description's bytes are decided, named here so a
# failure below can send its reader straight to it.
THE_ONE_PLACE = "fixtures.write_profile"

# The module that may compose description bytes of its own. Its subject
# IS the refusal: it damages a conforming description one rule at a time
# and proves the loader turns each one away, so its bytes have to be
# exactly what it composed and cannot come from a helper that writes
# only conforming ones.
MAY_COMPOSE_ITS_OWN = frozenset({"test_contract_loader.py"})

# What a call to the canonical serializer looks like, under any of the
# three names it is reachable by: `canonical.serialize`,
# `profile.serialize` (the same function, re-exported), or a bare
# `serialize` imported directly.
_SERIALIZER = "serialize"


def _test_modules() -> "list[pathlib.Path]":
    """Every Python source file of the suite, this one included."""
    found = sorted(TESTS.glob("*.py"))
    assert found, f"no test modules were found under {TESTS}"
    return found


def _serializes_a_description(call: ast.Call) -> bool:
    """Whether the text this call writes came from the serializer."""
    if not call.args:
        return False
    for node in ast.walk(call.args[0]):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if isinstance(named, ast.Attribute) and named.attr == _SERIALIZER:
            return True
        if isinstance(named, ast.Name) and named.id == _SERIALIZER:
            return True
    return False


def _spells_a_json_name(expression: ast.expr) -> bool:
    """Whether a path expression ends in a name ending in `.json`.

    The LAST piece is what decides it, which is the difference between a
    description and a file that merely carries the word: ``folder /
    "table-profile.json"`` and ``folder / f"{name}.json"`` are both
    descriptions, while ``tmp / f"clinic-profile.json{SUFFIX}-1"`` is a
    working file whose name happens to begin with one, and is not.
    """
    if isinstance(expression, ast.Constant):
        return isinstance(expression.value, str) and expression.value.endswith(
            ".json"
        )
    if isinstance(expression, ast.JoinedStr):
        if not expression.values:
            return False
        return _spells_a_json_name(expression.values[-1])
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Div):
        return _spells_a_json_name(expression.right)
    if isinstance(expression, ast.Call) and expression.args:
        return _spells_a_json_name(expression.args[0])
    return False


def _json_paths(tree: ast.Module) -> "set[str]":
    """Every variable in ``tree`` ever assigned a path ending in `.json`.

    The defect was written as two statements -- the name on one line and
    the write on the next -- so a rule that reads only the receiver of
    the call sees a bare variable and lets the defect through.

    The names are gathered across the whole module rather than one scope
    at a time, which can ask a write in another function for a
    ``newline`` it did not strictly need. That is the direction to err
    in: what the guard asks for is never wrong, and a description it
    failed to recognize is a Windows job nobody can reproduce locally.
    """
    named: set[str] = set()
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        value = node.value
        if value is None or not _spells_a_json_name(value):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                named.add(target.id)
    return named


def _names_a_description_file(call: ast.Call, paths: "set[str]") -> bool:
    """Whether the file written to is a `.json` one.

    Three shapes are recognized, and the first two are how the defect
    was actually written: ``folder / f"{name}.json"``, a variable
    assigned such a path earlier in the module, and the name written
    out in the call itself as ``(folder / "table-profile.json")``.
    """
    target = call.func
    if not isinstance(target, ast.Attribute):
        return False
    if isinstance(target.value, ast.Name) and target.value.id in paths:
        return True
    return _spells_a_json_name(target.value)


def description_writes(source: str) -> "list[tuple[int, bool, bool]]":
    """Every description-writing ``write_text`` call in ``source``.

    Returns one entry per call: its line, whether it composed the bytes
    itself through the serializer, and whether it passed an explicit
    ``newline``. Accepts any Python source as text, which is what lets
    the detector be put through the defect itself below rather than
    trusted.
    """
    tree = ast.parse(source)
    paths = _json_paths(tree)
    found: list[tuple[int, bool, bool]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if not isinstance(named, ast.Attribute) or named.attr != "write_text":
            continue
        composed = _serializes_a_description(node)
        if not composed and not _names_a_description_file(node, paths):
            continue
        keywords = {keyword.arg for keyword in node.keywords}
        found.append((node.lineno, composed, "newline" in keywords))
    return found


# --------------------------------------------------------------------
# 1. Nothing writes a description and leaves the line ending to luck
# --------------------------------------------------------------------


def test_every_description_a_test_writes_fixes_its_own_line_endings() -> None:
    """The defect itself, made impossible to reintroduce unnoticed."""
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, _composed, newline in description_writes(source):
            if not newline:
                loose.append(f"{path.name} line {line}")
    assert not loose, (
        "these calls write a description -- or a file named like one -- "
        "with the line ending left to the platform, so what they leave "
        "on Windows is a file the loader must refuse: "
        + ", ".join(loose)
        + f". Ask {THE_ONE_PLACE} for the file instead; if the bytes "
        "have to be exactly what this test composed, pass newline= so "
        "that they are the same bytes on every platform."
    )


# --------------------------------------------------------------------
# 2. The bytes of a conforming description are decided in one place
# --------------------------------------------------------------------


def test_only_the_refusal_battery_composes_a_description_of_its_own() -> None:
    """One place decides those bytes, and one module is excused.

    A second place deciding them is a second place to get them wrong,
    which is exactly how the defect arrived: twenty-three modules each
    wrote the file themselves, and one of the twenty-three wrote it a
    slightly different way.
    """
    composing = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        if any(composed for _line, composed, _end in description_writes(source)):
            composing.append(path.name)
    unexpected = [name for name in composing if name not in MAY_COMPOSE_ITS_OWN]
    assert not unexpected, (
        "these modules serialize a description and write the file "
        "themselves: "
        + ", ".join(sorted(unexpected))
        + f". Ask {THE_ONE_PLACE} for it, so that the bytes of a "
        "description are decided in one place."
    )


def test_every_module_that_loads_a_description_asks_the_fixture_for_it() -> None:
    """The floor under the two tests above.

    Both of them pass trivially if nothing in the suite writes a
    description any more -- a rule that matches nothing is not a rule.
    This is the positive form: a module that hands a file to the loader
    got that file from the fixture, unless it is the one module allowed
    to compose bytes of its own.
    """
    missing = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        if "contract.load_profile" not in source:
            continue
        if path.name in MAY_COMPOSE_ITS_OWN:
            continue
        if THE_ONE_PLACE not in source:
            missing.append(path.name)
    assert not missing, (
        "these modules hand a description to the loader without asking "
        f"{THE_ONE_PLACE} for the file: " + ", ".join(sorted(missing))
    )


# --------------------------------------------------------------------
# 3. The detector, put through the defect it exists to catch
# --------------------------------------------------------------------

# The original defect, spelled exactly as it stood in
# tests/test_generation_reference.py before the repair.
_THE_DEFECT = '''
def _load(case, name, folder):
    path = folder / f"{name}.json"
    path.write_text(
        json.dumps(_profile_document(case, name), indent=2, sort_keys=True)
        + "\\n",
        encoding="utf-8",
    )
    return contract.load_profile(str(path))
'''

# The same defect in its other shape: the serializer's own text, written
# to a path whose name the source does not spell out.
_THE_DEFECT_THROUGH_A_VARIABLE = '''
def _described(folder, document):
    target = _somewhere(folder)
    target.write_text(canonical.serialize(document), encoding="utf-8")
    return contract.load_profile(str(target))
'''

# The repair: the fixture decides the bytes and no write_text is left.
_THE_REPAIR = '''
def _load(case, name, folder):
    path = fixtures.write_profile(
        folder, f"{name}.json", _profile_document(case, name)
    )
    return contract.load_profile(str(path))
'''

# Deliberate bytes, kept deliberate on every platform.
_DELIBERATE_BYTES = '''
def refusal_of_text(folder, text):
    target = folder / "table-profile.json"
    target.write_text(text, encoding="utf-8", newline="")
'''

# Not a description at all, and none of this file's business.
_ANOTHER_FILE_ENTIRELY = '''
def _table(folder, text):
    (folder / "table.csv").write_text(text, encoding="utf-8")
'''


def test_the_detector_recognizes_the_defect_that_reddened_windows() -> None:
    """Line 4 of the fragment, composed by hand, with no newline given."""
    assert description_writes(_THE_DEFECT) == [(4, False, False)]


def test_the_detector_recognizes_the_defect_behind_a_variable() -> None:
    """The path says nothing, so the serializer in the text is the mark."""
    assert description_writes(_THE_DEFECT_THROUGH_A_VARIABLE) == [
        (4, True, False)
    ]


def test_the_detector_passes_the_repair_and_the_deliberate_bytes() -> None:
    """Neither shape of a correct write may be reported as a defect."""
    assert description_writes(_THE_REPAIR) == []
    assert description_writes(_DELIBERATE_BYTES) == [(4, False, True)]


def test_the_detector_leaves_a_file_that_is_not_a_description_alone() -> None:
    """Over-reach is its own defect: a table is written by other rules."""
    assert description_writes(_ANOTHER_FILE_ENTIRELY) == []


# --------------------------------------------------------------------
# 4. The fixture writes the product's bytes; the platform's are refused
# --------------------------------------------------------------------


def _document(folder: pathlib.Path) -> dict:
    """The producer's own description of a seeded neutral table."""
    path = fixtures.write(folder, "table.csv", fixtures.every_role_table())
    table = reading.read_table(str(path))
    return profile.build_document(table, taxonomy.Settings(), ["record_code"])


def test_the_fixture_writes_the_bytes_the_product_writes(
    tmp_path: pathlib.Path,
) -> None:
    """Byte for byte, against the writer `synthtwin profile` runs.

    The fixture's guarantee is not "close enough to load": it is the
    same file. Anything less and a test would be proving the generator
    against bytes no researcher will ever hold.
    """
    document = _document(tmp_path)
    mine = fixtures.write_profile(tmp_path, "by-the-fixture.json", document)
    theirs = tmp_path / "by-the-product.json"
    writing.write_text_file(theirs, canonical.serialize(document))

    assert mine.read_bytes() == theirs.read_bytes()
    assert b"\r" not in mine.read_bytes()
    contract.load_profile(str(mine))


def test_a_description_whose_lines_end_the_windows_way_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The refusal every Windows job printed, arranged on any platform.

    The file is written as bytes, so the platform running this test is
    not what decides them: this is exactly what a text-mode write with
    no ``newline`` argument leaves on Windows, and the loader is right
    to refuse it.
    """
    document = _document(tmp_path)
    target = tmp_path / "translated-profile.json"
    text = canonical.serialize(document)
    target.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(target))
    assert "is not in the exact form synthtwin writes" in f"{refused.value}"
