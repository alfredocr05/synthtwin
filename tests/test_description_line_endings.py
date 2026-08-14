"""The line endings of a file a test writes for the product to read.

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

IT HAPPENED A SECOND TIME, ON THE OTHER KIND OF FILE (2026-08-14,
review item P3-V2-F-F1), which is why this file is no longer about
descriptions alone. `tests/test_twin_golden.py` wrote the twin it
measures with ``write_text(text, encoding="utf-8")`` and handed the
file to `validation.measure`. On Windows that file is a CRLF twin, so
the byte rule `bytes.line-endings` MISSED, `GOLDEN_QUALITY_SHA256`
moved, and the message a Windows maintainer would read called it a
release-blocking determinism defect in the product. The product was
innocent both times: `writing.write_text_file` pins the line ending, so
a real generate-then-validate holds that rule on Windows too.

Two kinds of file, one class: A FILE A TEST WRITES FOR THE PRODUCT TO
READ, whose bytes the platform was left to decide. The first shape cost
a refusal a Windows maintainer could not reproduce; the second would
have cost a false verdict against the product. So the rule is drawn
around the class, not around the shape that bit first.

HOW WIDE THE RULE IS DRAWN, and why wider than the two files that bit.
"This file is a profile document" is not a question source text can be
asked, so the rule is drawn around what it can be asked: a write whose
text comes from the canonical serializer, and a write whose target is
named as a `.json` or a `.csv` file -- the two extensions synthtwin's
own readers open. That takes in a few files that are neither a
description nor a table -- a signed attestation, a stand-in left in the
way of a run, a stray file placed to make a scanner refuse it -- and
asks each of them for one keyword argument they could have done
without. It is the cheap side of the trade: what the guard asks for is
never wrong, and the file it fails to ask turns a platform red that
nobody can reproduce locally.

WHAT THIS FILE CHECKS, and it states the whole of it:

1. Every ``write_text`` call in the suite that writes a file the
   product reads -- one whose text comes from the canonical serializer,
   or whose target names a `.json` or `.csv` file -- passes an explicit
   ``newline``.
2. The only module that composes description bytes itself, instead of
   asking the fixture for them, is the one whose whole subject is the
   refusal of bytes synthtwin would never have written.
3. Every module that hands the loader a description asks the fixture for
   it. Without this the first two tests could go quiet by matching
   nothing at all.
4. Each half of rule 1 recognizes at least one write that really is in
   the suite. Rule 3 is that floor for descriptions; this is the floor
   for the half added in 2026-08-14, because a rule that has quietly
   stopped seeing `.csv` targets passes rule 1 in silence and the next
   golden to write its own measured file is red on Windows only.
5. The detector is put through source carrying each defect and source
   without it, so a rule that has stopped recognizing one of them
   cannot pass this file in silence.
6. The fixture's bytes are the product's bytes, compared byte for byte
   against `writing.write_text_file` for the same document.
7. A description whose lines end the Windows way is refused, with the
   message the Windows jobs printed; and a measured file whose lines end
   that way MISSES the byte rule it should miss. Those are the two
   properties all of the above exists to keep from reaching a person --
   one as a refusal nobody can reproduce, one as a false verdict against
   the product.

WHAT IT DOES NOT CHECK. Only ``write_text`` is read. A file written
through ``open`` would pass unnoticed here; nothing in the suite writes
one that way, and the fixture is the door every test now uses. And the
rule reads NAMES, not what a file is handed to: a measured file written
under a name ending in neither `.json` nor `.csv` is outside it. Nothing
in the suite writes one, and rule 4's floor is what turns a shrinking
rule red rather than quiet.
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
    validation,
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

# The file names synthtwin's own readers open, and therefore the names
# whose bytes a test may not leave to the platform. `.json` is the
# description, read by `contract.load_profile`; `.csv` is the table the
# profiler reads and the measured file `validation.measure` reads. Both
# have now cost a Windows-only failure, one per extension.
PRODUCT_READS = (".json", ".csv")


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


def _spelled_extension(expression: ast.expr) -> str:
    """The `PRODUCT_READS` extension a path expression ends in, or ``""``.

    The LAST piece is what decides it, which is the difference between a
    file the product reads and a file that merely carries the word:
    ``folder / "table-profile.json"``, ``folder / f"{name}.json"`` and
    ``tmp_path / "twin.csv"`` are all read by synthtwin, while ``tmp /
    f"clinic-profile.json{SUFFIX}-1"`` is a working file whose name
    happens to begin with one, and is not.
    """
    if isinstance(expression, ast.Constant):
        if not isinstance(expression.value, str):
            return ""
        for extension in PRODUCT_READS:
            if expression.value.endswith(extension):
                return extension
        return ""
    if isinstance(expression, ast.JoinedStr):
        if not expression.values:
            return ""
        return _spelled_extension(expression.values[-1])
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Div):
        return _spelled_extension(expression.right)
    if isinstance(expression, ast.Call) and expression.args:
        return _spelled_extension(expression.args[0])
    return ""


def _read_paths(tree: ast.Module) -> "dict[str, str]":
    """Every variable in ``tree`` assigned a path the product reads.

    Maps the variable's name to the extension it was last seen carrying.
    Both defects were written as two statements -- the name on one line
    and the write on the next -- so a rule that reads only the receiver
    of the call sees a bare variable and lets the defect through. That
    is exactly how the golden's measured file was written:
    ``target = tmp_path / "twin.csv"`` and then ``target.write_text(...)``.

    The names are gathered across the whole module rather than one scope
    at a time, which can ask a write in another function for a
    ``newline`` it did not strictly need. That is the direction to err
    in: what the guard asks for is never wrong, and a file it failed to
    ask is a Windows job nobody can reproduce locally.
    """
    named: dict[str, str] = {}
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        else:
            continue
        value = node.value
        if value is None:
            continue
        extension = _spelled_extension(value)
        if not extension:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                named[target.id] = extension
    return named


def _names_a_file_the_product_reads(
    call: ast.Call, paths: "dict[str, str]"
) -> str:
    """The extension of the file written to, or ``""`` for none of them.

    Three shapes are recognized, and the first two are how the two
    defects were actually written: ``folder / f"{name}.json"``, a
    variable assigned such a path earlier in the module (which is how
    ``target = tmp_path / "twin.csv"`` reached `validation.measure`), and
    the name written out in the call itself as ``(folder /
    "table-profile.json")``.
    """
    target = call.func
    if not isinstance(target, ast.Attribute):
        return ""
    if isinstance(target.value, ast.Name) and target.value.id in paths:
        return paths[target.value.id]
    return _spelled_extension(target.value)


def product_input_writes(source: str) -> "list[tuple[int, bool, bool, str]]":
    """Every ``write_text`` in ``source`` that writes a file synthtwin reads.

    Returns one entry per call: its line, whether it composed the bytes
    itself through the serializer, whether it passed an explicit
    ``newline``, and which of `PRODUCT_READS` the target's name ends in
    (``""`` when the call was recognized by its serialized text alone,
    because then the name settles nothing). Accepts any Python source as
    text, which is what lets the detector be put through each defect
    itself below rather than trusted.
    """
    tree = ast.parse(source)
    paths = _read_paths(tree)
    found: list[tuple[int, bool, bool, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if not isinstance(named, ast.Attribute) or named.attr != "write_text":
            continue
        composed = _serializes_a_description(node)
        extension = _names_a_file_the_product_reads(node, paths)
        if not composed and not extension:
            continue
        keywords = {keyword.arg for keyword in node.keywords}
        found.append((node.lineno, composed, "newline" in keywords, extension))
    return found


# --------------------------------------------------------------------
# 1. Nothing writes a description and leaves the line ending to luck
# --------------------------------------------------------------------


def test_every_file_the_product_reads_fixes_its_own_line_endings() -> None:
    """Both defects, made impossible to reintroduce unnoticed."""
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, _composed, newline, _named in product_input_writes(source):
            if not newline:
                loose.append(f"{path.name} line {line}")
    assert not loose, (
        "these calls write a file synthtwin's own readers open -- a "
        "description, a table, a measured file, or a file named like "
        "one -- with the line ending left to the platform. What they "
        "leave on Windows is a file the loader must refuse, or a file "
        "whose line endings the check must report as MISSED: "
        + ", ".join(loose)
        + f". Ask {THE_ONE_PLACE} for a description or `fixtures.write` "
        "for any other file; if the bytes have to be exactly what this "
        "test composed, pass newline= so that they are the same bytes "
        "on every platform."
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
        if any(
            composed
            for _line, composed, _end, _named in product_input_writes(source)
        ):
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


def test_the_rule_still_recognizes_a_write_of_each_kind_it_governs() -> None:
    """The floor under the widened half of rule 1.

    The test above is the floor for descriptions: a module that loads
    one has to have asked the fixture. There is no equivalent question
    to ask about a table or a measured file -- they reach the product
    through several doors and under several names -- so the floor here
    is directly on the RULE: each extension it governs is still matched
    by a real write somewhere in this suite.

    Without it, a `.csv` leg that stopped matching anything would leave
    rule 1 green and silent, which is precisely the state the suite was
    in on 2026-08-13: the golden wrote its own measured file, no rule
    looked at it, and only Windows would ever have said so.
    """
    seen: dict[str, str] = {}
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, _composed, _end, named in product_input_writes(source):
            if named and named not in seen:
                seen[named] = f"{path.name} line {line}"
    unmatched = [
        extension for extension in PRODUCT_READS if extension not in seen
    ]
    assert not unmatched, (
        "the rule governs these file names and no write in the whole "
        "suite is being matched under them: "
        + ", ".join(unmatched)
        + ". Either every such write has left the suite, or the rule has "
        "stopped recognizing them -- and the second is invisible on the "
        "machine you are reading this on. Check `_spelled_extension` "
        "against a write you can point at before changing this test."
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

# The second defect, spelled exactly as it stood in
# tests/test_twin_golden.py before the repair: the measured file, named
# on one line and written on the next, then handed to `measure`.
_THE_MEASURED_FILE_DEFECT = '''
def test_golden(tmp_path, loaded, built):
    target = tmp_path / "twin.csv"
    target.write_text(rendering.twin_csv(built), encoding="utf-8")
    outcome = validation.measure(loaded, str(target))
'''

# Its repair, the same one the description's defect got.
_THE_MEASURED_FILE_REPAIR = '''
def test_golden(tmp_path, loaded, built):
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(built))
    outcome = validation.measure(loaded, str(target))
'''

# Not a file the product reads at all, and none of this file's business.
_ANOTHER_FILE_ENTIRELY = '''
def _notes(folder, text):
    (folder / "notes.md").write_text(text, encoding="utf-8")
'''


def test_the_detector_recognizes_the_defect_that_reddened_windows() -> None:
    """Line 4 of the fragment, composed by hand, with no newline given."""
    assert product_input_writes(_THE_DEFECT) == [(4, False, False, ".json")]


def test_the_detector_recognizes_the_defect_behind_a_variable() -> None:
    """The path says nothing, so the serializer in the text is the mark."""
    assert product_input_writes(_THE_DEFECT_THROUGH_A_VARIABLE) == [
        (4, True, False, "")
    ]


def test_the_detector_recognizes_the_measured_file_defect() -> None:
    """The second defect: a `.csv` name behind a variable, no newline.

    This case is the whole reason the rule was widened. Before it, the
    detector read this fragment and reported nothing at all, which is
    what let a golden measure a CRLF twin on Windows.
    """
    assert product_input_writes(_THE_MEASURED_FILE_DEFECT) == [
        (4, False, False, ".csv")
    ]


def test_the_detector_passes_the_repair_and_the_deliberate_bytes() -> None:
    """No shape of a correct write may be reported as a defect."""
    assert product_input_writes(_THE_REPAIR) == []
    assert product_input_writes(_THE_MEASURED_FILE_REPAIR) == []
    assert product_input_writes(_DELIBERATE_BYTES) == [(4, False, True, ".json")]


def test_the_detector_leaves_a_file_the_product_never_reads_alone() -> None:
    """Over-reach is its own defect: prose is written by other rules."""
    assert product_input_writes(_ANOTHER_FILE_ENTIRELY) == []


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


def test_a_measured_file_whose_lines_end_the_windows_way_misses(
    tmp_path: pathlib.Path,
) -> None:
    """The other half of what the platform decides, and what it costs.

    A description refused is loud: nobody can mistake it for a verdict.
    A measured file carrying the platform's line ending is quiet and
    worse -- the check runs, and reports the file MISSING a byte rule
    that the file, as the product would have written it, holds. That is
    a false verdict against synthtwin, printed by synthtwin, on the one
    platform whose maintainer cannot reproduce it anywhere else.

    Both files here are written as BYTES, so the platform running this
    test decides nothing: the second is exactly what a text-mode write
    with no ``newline`` argument leaves on Windows.
    """
    document = _document(tmp_path)
    described = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "table-profile.json", document))
    )
    text = (tmp_path / "table.csv").read_text(encoding="utf-8")

    as_written = tmp_path / "as-the-product-writes-it.csv"
    as_written.write_bytes(text.encode("utf-8"))
    translated = tmp_path / "as-the-platform-left-it.csv"
    translated.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    def _endings(target: pathlib.Path) -> validation.Check:
        outcome = validation.measure(described, str(target))
        found = [
            check
            for check in outcome.checks
            if check.subcheck == "bytes.line-endings"
        ]
        assert len(found) == 1, "the byte rule this test is about is gone"
        return found[0]

    assert _endings(as_written).verdict == validation.HELD
    assert _endings(translated).verdict == validation.MISSED, (
        "a measured file whose lines end the Windows way must MISS the "
        "line-ending rule; if it stopped doing so, the guard above is "
        "protecting the suite from a defect the product no longer has "
        "and this file needs rewriting rather than deleting"
    )
