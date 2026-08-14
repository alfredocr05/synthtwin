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
asked, so the rule is drawn around three things it can be asked: a
write whose text comes from the canonical serializer; a write whose
target is named as a `.json` or a `.csv` file -- the two extensions
synthtwin's own readers open; and a write whose target is HANDED TO the
product afterwards. That takes in a few files that are neither a
description nor a table -- a signed attestation, a stand-in left in the
way of a run, a stray file placed to make a scanner refuse it -- and
asks each of them for one keyword argument they could have done
without. It is the cheap side of the trade: what the guard asks for is
never wrong, and the file it fails to ask turns a platform red that
nobody can reproduce locally.

THE THIRD LEG IS WHY THIS FILE WAS REOPENED (2026-08-14, review item
P3-V3-F10). The first two read NAMES, and the product does not read
names: `synthtwin validate` accepts whatever local path it is handed,
so a test writing ``tmp_path / "measured"`` and giving it to
`validation.measure` wrote a CRLF file on Windows that no rule here
looked at -- the same defect as the golden's, under a file name with no
extension. A rule that governs `twin.csv` and lets `measured` through
is governing spelling, not substance. So the third leg governs by what
the write IS: a file this suite writes and then hands to a function of
the product is a file the product reads, whatever it is called. The
product's module names come from the package directory rather than a
list here, so a new module joins the rule on the commit that adds it.

AND THE THIRD LEG WAS WALKED AROUND (2026-08-14, review item
P3-V4-F9). It followed a written path by the NAME OF THE VARIABLE, so a
helper that writes an extensionless file and RETURNS it, a caller that
puts the return value in a list, and a `choices[0]` handed to
`validation.measure` was three steps past the end of it and the guard
said nothing. That is the fourth time a rule here has been found with a
route around it, and each route was narrower than the last, which is
what a shrinking classifier looks like. So there is no classifier on
the main rule any more: EVERY text-mode write in this suite pins its
line ending, whatever it writes and whoever reads it. What that costs
is a keyword argument on sixty-six writes that did not strictly need
one -- a scanner's fixture, a hashed manifest, a stand-in file -- and
every one of those had its bytes decided by the platform too, so the
cost buys the same property one class wider. The classification is
kept, because rules 2 and 3 below are about descriptions specifically
and still have to know which write is one.

WHAT THIS FILE CHECKS, and it states the whole of it:

1. Every ``write_text`` call in the suite passes an explicit
   ``newline``. No analysis decides which ones are covered, so no
   analysis can be walked around.
2. The only module that composes description bytes itself, instead of
   asking the fixture for them, is the one whose whole subject is the
   refusal of bytes synthtwin would never have written.
3. Every module that hands the loader a description asks the fixture for
   it. Without this the first two tests could go quiet by matching
   nothing at all.
4. Each leg of rule 1 recognizes at least one write that really is in
   the suite. Rule 3 is that floor for descriptions; this is the floor
   for the legs added in 2026-08-14, because a rule that has quietly
   stopped seeing `.csv` targets, or stopped following a file to the
   function it is handed to, passes rule 1 in silence and the next
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
8. Every ``open`` in a writing mode passes an explicit ``newline`` too.
   It is the other call that leaves bytes on a disk, and rule 1 would
   otherwise be total over one of the two ways to write a file.

WHAT IT DOES NOT CHECK, stated in full because a rule's edge is the
part that rots. Two call names are read -- ``write_text`` and ``open``
-- and they are the two this suite writes files with. A route to the
filesystem that is neither, and a write inside `tools/`, are outside
this file.
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

# What "the product" is called in this suite's source, read off the
# package rather than written out, so that a module added tomorrow is
# inside the rule on the commit that adds it. `main` is beside them
# because the CLI tests import it bare and it is the widest door of all:
# `main(["validate", f"{target}"])` opens whatever it was handed.
# What the fourth field of a `product_input_writes` entry says when the
# file was recognized by the function it is handed to rather than by its
# name. It is not an extension, and it deliberately is not one: this is
# the leg that exists because names settle nothing.
HANDED_OVER = "handed to the product"

PACKAGE = TESTS.parent / "src" / "synthtwin"
PRODUCT_NAMES = frozenset(
    {module.stem for module in PACKAGE.glob("*.py") if module.stem != "__init__"}
    | {"synthtwin", "main"}
)


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


def _handed_to_the_product(tree: ast.Module) -> "set[str]":
    """Every variable in ``tree`` that is passed to a function of the product.

    The rule this serves governs a write by WHAT IT IS rather than by
    what it is named (review item P3-V3-F10): the product accepts any
    local path, so `validation.measure(described, str(measured))` makes
    `measured` a file the product reads whether it is called
    `twin.csv`, `measured`, or nothing at all.

    Every name anywhere inside such a call is taken, not the path
    argument alone. Which position holds the path differs between entry
    points and can be inside an f-string inside a list -- which is how
    the CLI tests spell it -- and over-collecting costs at worst a
    ``newline`` argument on a write that did not need one, which is the
    direction this whole file errs in.
    """
    handed: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        reaches = False
        if isinstance(named, ast.Attribute):
            root = named.value
            while isinstance(root, ast.Attribute):
                root = root.value
            reaches = isinstance(root, ast.Name) and root.id in PRODUCT_NAMES
        elif isinstance(named, ast.Name):
            reaches = named.id in PRODUCT_NAMES
        if not reaches:
            continue
        for argument in list(node.args) + [
            keyword.value for keyword in node.keywords
        ]:
            for inner in ast.walk(argument):
                if isinstance(inner, ast.Name):
                    handed.add(inner.id)
    return handed


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
    -- ``"handed to the product"`` where the name settles nothing and
    the file was recognized by the function it is given to, and ``""``
    where the serialized text alone recognized it. Accepts any Python
    source as text, which is what lets the detector be put through each
    defect itself below rather than trusted.
    """
    tree = ast.parse(source)
    paths = _read_paths(tree)
    handed = _handed_to_the_product(tree)
    found: list[tuple[int, bool, bool, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if not isinstance(named, ast.Attribute) or named.attr != "write_text":
            continue
        composed = _serializes_a_description(node)
        extension = _names_a_file_the_product_reads(node, paths)
        written_through = named.value
        if (
            not extension
            and isinstance(written_through, ast.Name)
            and written_through.id in handed
        ):
            extension = HANDED_OVER
        if not composed and not extension:
            continue
        keywords = {keyword.arg for keyword in node.keywords}
        found.append((node.lineno, composed, "newline" in keywords, extension))
    return found


# --------------------------------------------------------------------
# 1. Nothing writes a description and leaves the line ending to luck
# --------------------------------------------------------------------


def every_text_write(source: str) -> "list[tuple[int, bool]]":
    """Every ``write_text`` in ``source``: its line, and whether it pins.

    NO CLASSIFICATION AT ALL, and that is the repair (review item
    P3-V4-F9). Every version of this rule until now decided first
    whether a write was one the product would read, and each version's
    answer had a route around it: a name with no extension, then a
    variable followed only while it stayed a bare name in the same
    module. The reviewer walked through the second one -- a helper that
    writes and returns an extensionless path, a caller that puts it in
    a list and hands over `paths[0]` -- and the guard said nothing.

    A rule with a route around it is a rule that cannot fail for
    whatever takes the route. So there is no route: a text-mode write
    in this suite pins its line ending, whatever it writes and whoever
    reads it. That asks for a keyword argument on a few writes that did
    not need one -- a scanner's fixture, a manifest -- and every one of
    those is a file whose bytes were being decided by the platform too,
    which is the same defect wearing different clothes.

    `product_input_writes` is kept, because the rules that follow it
    are about descriptions specifically and still need to know which
    write is one.
    """
    found: list[tuple[int, bool]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        if not isinstance(named, ast.Attribute) or named.attr != "write_text":
            continue
        keywords = {keyword.arg for keyword in node.keywords}
        found.append((node.lineno, "newline" in keywords))
    return found


def test_every_file_this_suite_writes_fixes_its_own_line_endings() -> None:
    """Both defects, and every shape of them, made impossible.

    The rule is TOTAL over `write_text` (review item P3-V4-F9): no
    analysis decides which writes it covers, so no analysis can be
    walked around.
    """
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, newline in every_text_write(source):
            if not newline:
                loose.append(f"{path.name} line {line}")
    assert not loose, (
        "these calls write a file with the line ending left to the "
        "platform. On Windows that is different bytes from the ones "
        "the author saw -- a description the loader must refuse, a "
        "measured file whose line-ending rule must be reported MISSED, "
        "or a fixture whose hash a guard computes differently: "
        + ", ".join(loose)
        + f". Ask {THE_ONE_PLACE} for a description or `fixtures.write` "
        "for any other file; if the bytes have to be exactly what this "
        "test composed, pass newline= so that they are the same bytes "
        "on every platform."
    )


_WRITING_MODES = ("w", "a", "x", "+")


def every_handle_write(source: str) -> "list[tuple[int, bool]]":
    """Every ``open`` in a writing text mode: its line, and whether it pins.

    Both spellings -- the builtin and `pathlib.Path.open` -- because
    both leave bytes on a disk. A binary mode is not here: it writes
    what it is given and translates nothing. A mode this cannot read --
    one built out of a variable -- is treated as a writing mode, which
    errs in the direction this whole file errs in.
    """
    found: list[tuple[int, bool]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        named = node.func
        # The mode is the FIRST argument of `path.open` and the second
        # of the builtin, which is the whole difference between the two
        # spellings as far as this reading is concerned.
        if isinstance(named, ast.Attribute):
            opening, where = named.attr == "open", 0
        elif isinstance(named, ast.Name):
            opening, where = named.id == "open", 1
        else:
            continue
        if not opening:
            continue
        mode: ast.expr | None = (
            node.args[where] if len(node.args) > where else None
        )
        for keyword in node.keywords:
            if keyword.arg == "mode":
                mode = keyword.value
        if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
            spelled = mode.value
            if "b" in spelled:
                continue
            if not any(letter in spelled for letter in _WRITING_MODES):
                continue
        elif mode is None:
            # No mode at all is "r": a read translates nothing on to a
            # disk, so it is not this rule's business.
            continue
        found.append((node.lineno, "newline" in {k.arg for k in node.keywords}))
    return found


def test_every_handle_this_suite_opens_to_write_fixes_its_line_endings() -> (
    None
):
    """Rule 1's other half: the call that is not ``write_text``.

    A rule total over one of the two ways to write a file is a rule
    with the other one outside it, which is the shape review item
    P3-V4-F9 found in the leg before this. Both are read now.
    """
    loose = []
    for path in _test_modules():
        source = path.read_text(encoding="utf-8")
        for line, newline in every_handle_write(source):
            if not newline:
                loose.append(f"{path.name} line {line}")
    assert not loose, (
        "these calls open a file for writing in text mode with the line "
        "ending left to the platform: " + ", ".join(loose) + ". Pass "
        "newline= so that the bytes are the same on every platform."
    )
    # ...and the reading really does recognize the shapes it claims to,
    # so that a suite which stopped opening handles cannot make this
    # rule quiet.
    assert every_handle_write('open(p, "w", encoding="utf-8")\n') == [(1, False)]
    assert every_handle_write('p.open("w", newline="")\n') == [(1, True)]
    assert every_handle_write('open(p, "rb")\n') == []
    assert every_handle_write('open(p)\n') == []


def test_the_rule_is_total_over_the_writes_it_can_see() -> None:
    """The escape route review item P3-V4-F9 walked through, closed.

    The guard used to follow a written path by the NAME OF THE
    VARIABLE, in the same module, and stop there. This is the source
    the reviewer built: a helper writes an extensionless file and
    RETURNS it, the caller stores it in a list, and the product is
    handed `choices[0]` -- three steps, none of them a bare name at the
    point of the write. Under the rule that classified writes, nothing
    here was a product input and the missing ``newline`` was invisible.

    It is asserted of the DETECTOR rather than of the suite, because
    the suite must not contain the defect for this to have teeth.
    """
    escaping = '''
def _written(folder):
    target = folder / "measured"
    target.write_text("a,b\\n1,2\\n", encoding="utf-8")
    return target


def test_it(tmp_path):
    choices = [_written(tmp_path)]
    validation.measure(described, str(choices[0]))
'''
    seen = every_text_write(escaping)
    assert seen == [(4, False)], (
        "the rule no longer sees a write that reaches the product "
        "through a helper's return value and a list, which is the route "
        f"review item P3-V4-F9 walked through: {seen}"
    )
    # ...and it is not simply saying "not pinned" about everything: the
    # same write with the argument is not reported.
    pinned = escaping.replace('encoding="utf-8")', 'encoding="utf-8", newline="\\n")')
    assert every_text_write(pinned) == [(4, True)]
    # ...and a module with no write at all yields nothing, so the rule
    # is answering about writes rather than about lines.
    assert every_text_write("x = 1\n") == []


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
        extension
        for extension in PRODUCT_READS + (HANDED_OVER,)
        if extension not in seen
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

# The third defect, and the one no leg of the rule could see before
# 2026-08-14 (review item P3-V3-F10): the same measured file under a
# name with no extension at all. `synthtwin validate` takes any local
# path, so this is a file the product reads and the platform decides its
# bytes -- and the first two legs, which read names, report nothing.
_THE_MEASURED_FILE_WITH_NO_EXTENSION = '''
def test_a_check(tmp_path, described):
    measured = tmp_path / "measured"
    measured.write_text("age,site\\n31,north\\n", encoding="utf-8")
    outcome = validation.measure(described, str(measured))
'''

# The same file reaching the product through the command line instead,
# which is the wider door and the one the CLI tests use.
_THROUGH_THE_COMMAND_LINE = '''
def test_a_run(tmp_path, description):
    measured = tmp_path / "candidate"
    measured.write_text("age,site\\n31,north\\n", encoding="utf-8")
    assert main(["validate", f"{description}", "--twin", f"{measured}"]) == 0
'''

# Not a file the product reads at all, and none of this file's business.
_ANOTHER_FILE_ENTIRELY = '''
def _notes(folder, text):
    (folder / "notes.md").write_text(text, encoding="utf-8")
'''

# The same file, still never handed to anything of the product's: a
# neighbour of the third leg that it must not take in.
_A_FILE_NOBODY_HANDS_OVER = '''
def _notes(folder, text):
    target = folder / "notes"
    target.write_text(text, encoding="utf-8")
    return target.read_text(encoding="utf-8")
'''


def test_the_detector_recognizes_the_defect_that_reddened_windows() -> None:
    """Line 4 of the fragment, composed by hand, with no newline given."""
    assert product_input_writes(_THE_DEFECT) == [(4, False, False, ".json")]


def test_the_detector_recognizes_the_defect_behind_a_variable() -> None:
    """The path says nothing, so two other marks have to carry it.

    The serializer in the text is the first, and it is the one this
    fragment was written for. The second arrived with the third leg
    (review item P3-V3-F10): the file is handed to `contract.load_profile`
    two lines further down, which makes it a file the product reads
    whatever it is called. Either alone would catch this; the entry
    records the second because a name that settles nothing is exactly
    the case the third leg exists for.
    """
    assert product_input_writes(_THE_DEFECT_THROUGH_A_VARIABLE) == [
        (4, True, False, HANDED_OVER)
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


def test_the_detector_recognizes_a_measured_file_with_no_extension() -> None:
    """The third defect, under both doors the product opens.

    Neither fragment names a `.json` or a `.csv` and neither composes a
    description, so before the third leg the detector read both and
    reported nothing at all -- which is what let a test hand
    `validation.measure` a file whose bytes the platform decided
    (review item P3-V3-F10).
    """
    assert product_input_writes(_THE_MEASURED_FILE_WITH_NO_EXTENSION) == [
        (4, False, False, HANDED_OVER)
    ]
    assert product_input_writes(_THROUGH_THE_COMMAND_LINE) == [
        (4, False, False, HANDED_OVER)
    ]


def test_the_detector_leaves_a_file_the_product_never_reads_alone() -> None:
    """Over-reach is its own defect: prose is written by other rules."""
    assert product_input_writes(_ANOTHER_FILE_ENTIRELY) == []
    assert product_input_writes(_A_FILE_NOBODY_HANDS_OVER) == []


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
