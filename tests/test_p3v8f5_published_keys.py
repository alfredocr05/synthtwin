"""A published key is decimal text, and it is read as decimal text.

REVIEW ITEM P3-V8-F5, AND THE FOURTH RETURN OF ONE CLASS. The exactness
class has now been repaired four times: a comparison, a recount, a hole
rule, and now the keys of the description's own multiplicity maps. Each
repair was a different site and the same mistake -- a number the
description states in figures was read through a reader that answers in
binary64, which is exact only below nine quadrillion.

THE WITNESS, AND WHAT IT COST. A description publishing ten groups of
`9007199254740993` rows each is contract-valid: the loader admits the
key as figures and reads it with `int`. The validator read it through
`parse_number`, got `9007199254740992` back -- one row short -- divided
the band's cells by it, and came out needing ELEVEN different spellings
where the description asks for ten and the band holds ten. `synthtwin
validate` then stopped with the sentence that no file can be this
description's twin, on a description the shipped generator builds.

WHY THE GUARD THAT EXISTS DID NOT CATCH IT, which is the part that
matters. The guard written in round 5 and widened in rounds 6 and 7
walks the CLOSURE OF ONE RULE -- `_cells_that_description_reads`, the
rule that decides which cells the file's own description counts as
values. The multiplicity readers are not in that closure and never
were: they belong to the corner classifier and the refusal classifier,
which are different closures reached from different entry points. So
the guard was rooted at a DECISION while the class is about a KIND OF
VALUE, and rooting it at one more decision would have left the next site
uncovered exactly as this one was -- which is what happened between
rounds 5, 6 and 7.

So this guard is not another closure walk. It follows the VALUE: every
key of every mapping the profile contract publishes, from wherever it is
first read out of that mapping, through every assignment and every call
that carries it into another shipped function, and it complains where
one of them reaches a reader that answers in binary64. A site added
tomorrow is inside it on the commit that adds it, whichever rule that
site belongs to, because the thing being guarded is the key and not the
rule.

`int` IS NOT ONE OF THE READERS IT REFUSES, and that is deliberate:
`int` on decimal text is exact at every size, and it is what the
contract's loader itself reads the key with. What the guard refuses is
`parse_number`, `float`, `round` and `complex` -- the readers that turn
figures into the nearest number binary64 holds.

THE RED CHECK, in two parts. `REINSTATE=P3-V8-F5` puts the binary64
reading of a key back into `contract.occurrence_size`, and the witness
above goes red with it -- the refusal returns, the corner returns, and
the arithmetic that produced them is printed. The guard has its own red
beside that one and does not need an environment variable for it: eight
doctored modules are put through the SAME walk the guard runs, one of
them the shipped code exactly as the review found it and the other seven
spelling the call every other way it has ever been spelled, and every
one of them has to be complained about.

Every table is built at test time by seeded neutral builders; no
data-format file enters the repository (plan D13).
"""

import ast
import inspect
import os
import pathlib
import types

import pytest

import fixtures
import synthtwin as synthtwin_package
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    taxonomy,
    validation,
)

NAME = "col"

# 2**53 + 1: the smallest whole number binary64 cannot hold, and the
# smallest key at which the two readings part. `parse_number` answers
# one less; `int` answers the number.
_LOST_KEY = "9007199254740993"
_GROUPS = 10
_ROWS = int(_LOST_KEY) * _GROUPS


def _the_key_through_binary64(key: str) -> "int | None":
    """`occurrence_size` as it stood, spelled out for the red check."""
    from synthtwin import parsing

    value = parsing.parse_number(key)
    if value is None:
        return None
    return int(value)


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put the binary64 reading of a key back on request."""
    if os.environ.get("REINSTATE") == "P3-V8-F5":
        monkeypatch.setattr(
            contract, "occurrence_size", _the_key_through_binary64
        )


# -- the witness, built by the producer and edited where it must be ----


def _described(
    folder: pathlib.Path, cells: "list[str]", stem: str, declared: bool
) -> "dict[str, object]":
    """One column through the real producer, as a document."""
    table = fixtures.write(
        folder, f"{stem}.csv", fixtures.single_column_table(NAME, cells)
    )
    read = reading.read_table(str(table))
    return profile.build_document(
        read, taxonomy.Settings(), [NAME] if declared else []
    )


def _at_the_lost_key(
    folder: pathlib.Path, cells: "list[str]", stem: str, declared: bool
) -> contract.Profile:
    """The producer's own document, moved onto the key that is lost.

    THE COLUMN'S SHAPE IS THE PRODUCER'S; only the four numbers that fix
    the arithmetic are moved -- how many cells, how they divide between
    the alphabet bands, how many different values, and the multiplicity
    map. A table of ninety quadrillion rows is not one anybody profiles,
    and it does not have to be: the contract admits the key, the loader
    reads it with `int`, and the classifier is a function of published
    numbers alone. The size is where the two readings part, so the size
    is what the witness has to be.
    """
    document = _described(folder, cells, stem, declared)
    blocks = document["columns"]
    assert isinstance(blocks, list)
    column = blocks[0]
    assert isinstance(column, dict)
    column["n_present"] = _ROWS
    column["n_numeric"] = _ROWS
    column["n_not_numeric"] = 0
    column["n_all_digits"] = _ROWS
    column["n_code_alphabet"] = _ROWS
    column["n_distinct"] = _GROUPS
    column["n_distinct_folded"] = _GROUPS
    column["n_distinct_by_occurrences"] = {_LOST_KEY: _GROUPS}
    column["remarks"] = []
    if declared:
        column["all_whole_numbers"] = False
        column["min_length"] = 1
        column["max_length"] = 1
    document["n_rows"] = _ROWS
    document["publication_notes"] = []
    written = fixtures.write_profile(
        folder, f"{stem}-profile.json", document
    )
    return contract.load_profile(str(written))


@pytest.fixture(scope="module")
def free_text(
    tmp_path_factory: pytest.TempPathFactory,
) -> contract.Profile:
    """The refusal's own witness: one figure per cell, ten of them."""
    folder = tmp_path_factory.mktemp("lost-key-text")
    cells = [f"{place % 10}" for place in range(30)] + ["z"]
    return _at_the_lost_key(folder, cells, "text", False)


@pytest.fixture(scope="module")
def declared(
    tmp_path_factory: pytest.TempPathFactory,
) -> contract.Profile:
    """The corner's own witness: the same numbers on a declared column."""
    folder = tmp_path_factory.mktemp("lost-key-declared")
    cells = [f"{place % 10}" for place in range(40)]
    return _at_the_lost_key(folder, cells, "declared", True)


def test_a_key_is_read_as_the_whole_number_its_figures_name(
) -> None:
    """The two readings, side by side, at the size where they part."""
    assert contract.occurrence_size(_LOST_KEY) == int(_LOST_KEY)
    assert _the_key_through_binary64(_LOST_KEY) == int(_LOST_KEY) - 1
    # ...and they agree everywhere below it, which is why four rounds of
    # review walked past this: every fixture in this suite is smaller.
    for key in ("1", "2", "9", "10", "4503599627370496"):
        assert contract.occurrence_size(key) == _the_key_through_binary64(
            key
        ), key
    # Text that is not a row count is not a row count, whatever a number
    # reader would make of it. The callers each say which way that
    # leaves them; this says only that it is not read.
    for text in ("", " 1", "1.0", "1e3", "(1)", "1,000", "-1", "٣"):
        assert contract.occurrence_size(text) is None, text


def test_the_band_that_holds_ten_is_not_told_it_must_hold_eleven(
    free_text: contract.Profile,
) -> None:
    """The arithmetic the refusal is made of, at both readings.

    Ten groups of `9007199254740993` cells are ninety quadrillion cells,
    and ten spellings cover them exactly. Read one row short, the same
    division needs eleven -- and the figures band at one character holds
    ten.
    """
    column = free_text.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    assert dict(facts.n_distinct_by_occurrences) == {_LOST_KEY: _GROUPS}
    assert validation._widest_group(facts.n_distinct_by_occurrences) == int(
        _LOST_KEY
    )
    assert validation._rounded_up(_ROWS, int(_LOST_KEY)) == _GROUPS
    assert validation._rounded_up(_ROWS, int(_LOST_KEY) - 1) == _GROUPS + 1
    assert (
        validation._band_capacity(validation._BAND_DIGITS, 1, 1) == _GROUPS
    )


def test_a_description_a_twin_exists_for_is_not_refused(
    free_text: contract.Profile,
) -> None:
    """V4.3: a refusal says no conforming twin exists. Here one does."""
    assert validation.refusal_of(free_text) == ""
    assert validation._group_span(
        free_text.columns[0].facts.n_distinct_by_occurrences
    ) == (int(_LOST_KEY), int(_LOST_KEY), _GROUPS)


def test_the_identifier_corner_is_not_claimed_on_the_same_arithmetic(
    declared: contract.Profile,
) -> None:
    """The other reader of the same map, and the other cost.

    On a declared column the wrong reading claims owner decision 6's
    corner instead of a refusal, which takes three checks off the report
    rather than stopping the run -- the quieter of the two costs and the
    one a green suite says nothing about.
    """
    column = declared.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert validation._group_sizes(facts.n_distinct_by_occurrences) == (
        (int(_LOST_KEY), _GROUPS),
    )
    assert not validation._identifier_is_infeasible(column, facts)
    assert validation.corners_of(declared) == {}


def test_the_generator_reads_the_same_key_and_builds_the_groups(
    free_text: contract.Profile,
) -> None:
    """The other writing of the same rule, compared where both may run.

    V4.2's principle applied to the key itself: the generator's own
    reading is `int(key)` and it has always been exact, so the two
    writings now answer the same number. That is what makes the refusal
    a validator defect rather than a disagreement about the contract.
    """
    facts = free_text.columns[0].facts
    sizes = generation._groups_of(facts.n_distinct_by_occurrences)
    assert len(sizes) == _GROUPS
    assert set(sizes) == {int(_LOST_KEY)}
    assert sum(sizes) == _ROWS


# -- the class as a shape: a published key never reaches binary64 ------


# The readers that answer "what number is this?" by rounding to the
# nearest number binary64 holds. `int` is deliberately absent: on
# decimal text it is exact at every size, and it is what the contract's
# own loader reads a key with.
_BINARY64_READERS = ("parse_number", "float", "round", "complex")

# What an expression is, when it is anything this walk cares about.
_MAP = "a published mapping"
_KEYS = "its keys"
_KEY = "one of its keys"
_ITEMS = "its keys and values in pairs"

# The calls that carry a mapping's shape through unchanged, so that
# `sorted(published)` is still keys.
_PASS_THROUGH = ("sorted", "list", "tuple", "reversed", "frozenset", "set")

# What a call target reduces to when it is not a dotted path: a step the
# walk cannot see the far side of. Spelled so no Python name equals one.
_UNREADABLE = "?"


def _shipped_trees() -> "dict[str, ast.Module]":
    """Every shipped module, parsed, keyed by its import name."""
    found: dict[str, ast.Module] = {}
    for name in sorted(vars(synthtwin_package)):
        member = getattr(synthtwin_package, name)
        if isinstance(member, types.ModuleType):
            found[name] = ast.parse(inspect.getsource(member))
    return found


def _published_maps(tree: ast.Module) -> "tuple[str, ...]":
    """Every contract field whose keys are text the description states.

    Read off the contract's OWN dataclasses rather than listed here, so
    a field added to the profile is inside this guard on the commit that
    adds it. A FIELD OF A CLASS annotated `dict[str, ...]` is a mapping
    the description publishes and whose keys are its own text; an
    annotated local of some function is not a published field and is not
    counted, so what this guard says it walks is what it walks.
    """
    found: list[str] = []
    for holder in ast.walk(tree):
        if not isinstance(holder, ast.ClassDef):
            continue
        for node in holder.body:
            if not isinstance(node, ast.AnnAssign):
                continue
            if not isinstance(node.target, ast.Name):
                continue
            written = ast.unparse(node.annotation).strip().strip("'\"")
            if not written.startswith("dict[str,"):
                continue
            if node.target.id not in found:
                found = found + [node.target.id]
    return tuple(sorted(found))


def _dotted(node: ast.AST) -> "tuple[str, ...]":
    """The dotted path an expression spells, head first, or ()."""
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value)
        if not head:
            return ()
        return head + (node.attr,)
    return ()


def _target_path(node: ast.AST) -> "tuple[str, ...]":
    """A call target as a path, or the unreadable mark."""
    path = _dotted(node)
    if path:
        return path
    return (_UNREADABLE,)


def _aliases_in(tree: ast.AST) -> "dict[str, tuple[str, ...]]":
    """Every name in one tree that stands for another name.

    `import x as y`, `from a import b as c`, and a plain assignment of
    one dotted path to a name. Without this a reader reached under a
    different name is a reader the walk cannot see -- which is the way
    past the round-6 guard that round 7 recorded.
    """
    found: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found[alias.asname or alias.name] = tuple(
                    alias.name.split(".")
                )
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                found[alias.asname or alias.name] = (alias.name,)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            path = _dotted(node.value)
            if isinstance(target, ast.Name) and path:
                found[target.id] = path
    return found


def _resolved(
    path: "tuple[str, ...]", aliases: "dict[str, tuple[str, ...]]"
) -> "tuple[str, ...]":
    """The path with its head replaced by whatever it stands for."""
    seen = 0
    while path and path[0] in aliases and seen < 8:
        stood_for = aliases[path[0]]
        if stood_for == path[: len(stood_for)]:
            break
        path = stood_for + path[1:]
        seen = seen + 1
    return path


def _parameters_of(node: ast.AST) -> "list[str]":
    """Every parameter name of one function, in order."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return []
    args = node.args
    listed = (
        list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    )
    return [one.arg for one in listed]


def _seed_of(node: ast.AST) -> "dict[str, str]":
    """Parameters a function's own annotations say hold a mapping."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return {}
    args = node.args
    found: dict[str, str] = {}
    listed = (
        list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    )
    for one in listed:
        if one.annotation is None:
            continue
        written = ast.unparse(one.annotation).strip().strip("'\"")
        if written.startswith("dict[str,"):
            found[one.arg] = _MAP
    return found


def _kind_of(
    node: ast.AST,
    kinds: "dict[str, str]",
    published: "tuple[str, ...]",
    aliases: "dict[str, tuple[str, ...]]",
) -> str:
    """What one expression is, if it is a published mapping or a key."""
    if isinstance(node, ast.Name):
        return kinds.get(node.id, "")
    if isinstance(node, ast.Attribute):
        if node.attr in published:
            return _MAP
        return ""
    if isinstance(node, ast.Call):
        target = _resolved(_target_path(node.func), aliases)
        if not target:
            return ""
        last = target[len(target) - 1]
        if last in _PASS_THROUGH and len(node.args) == 1:
            inner = _kind_of(node.args[0], kinds, published, aliases)
            if inner in (_MAP, _KEYS):
                return _KEYS
            return ""
        if last == "keys" and isinstance(node.func, ast.Attribute):
            if _kind_of(node.func.value, kinds, published, aliases) == _MAP:
                return _KEYS
            return ""
        if last == "items" and isinstance(node.func, ast.Attribute):
            if _kind_of(node.func.value, kinds, published, aliases) == _MAP:
                return _ITEMS
            return ""
        # A key read exactly is still that key's number, so a binary64
        # reader applied to it afterwards is the same defect one step
        # later.
        if (
            last == "int"
            and len(node.args) == 1
            and _kind_of(node.args[0], kinds, published, aliases) == _KEY
        ):
            return _KEY
        return ""
    return ""


def _named_by(target: ast.AST) -> "list[str]":
    """Every plain name one assignment or loop target binds."""
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        found: list[str] = []
        for one in target.elts:
            found = found + _named_by(one)
        return found
    return []


def _first_named_by(target: ast.AST) -> "list[str]":
    """The names bound by the FIRST element of a tuple target."""
    if isinstance(target, (ast.Tuple, ast.List)) and target.elts:
        return _named_by(target.elts[0])
    return _named_by(target)


def _kinds_in(
    body: ast.AST,
    seed: "dict[str, str]",
    published: "tuple[str, ...]",
    aliases: "dict[str, tuple[str, ...]]",
) -> "dict[str, str]":
    """Every name in one function that holds a mapping or one of its keys.

    Taken as facts about the whole function rather than in statement
    order, which is the safe direction here: a name that holds a key
    anywhere in the body is treated as holding one everywhere, so a
    reader reached before the binding is read is still seen.
    """
    kinds = dict(seed)
    moving = True
    rounds = 0
    while moving and rounds < 12:
        moving = False
        rounds = rounds + 1
        for node in ast.walk(body):
            pairs: list[tuple[ast.AST, str]] = []
            if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                over = _kind_of(node.iter, kinds, published, aliases)
                if over in (_MAP, _KEYS):
                    pairs = [(node.target, _KEY)]
                if over == _ITEMS:
                    for name in _first_named_by(node.target):
                        pairs = pairs + [(ast.Name(id=name), _KEY)]
            if isinstance(node, ast.Assign):
                found = _kind_of(node.value, kinds, published, aliases)
                if found:
                    pairs = [(one, found) for one in node.targets]
            if (
                isinstance(node, (ast.AnnAssign, ast.AugAssign))
                and node.value is not None
            ):
                found = _kind_of(node.value, kinds, published, aliases)
                if found:
                    pairs = [(node.target, found)]
            for target, kind in pairs:
                for name in _named_by(target):
                    if kinds.get(name) != kind:
                        kinds[name] = kind
                        moving = True
    return kinds


def _complaint_at(
    node: ast.Call,
    kinds: "dict[str, str]",
    published: "tuple[str, ...]",
    aliases: "dict[str, tuple[str, ...]]",
    where: str,
) -> str:
    """What is wrong with one call that is handed a published key."""
    carried = [
        one
        for one in list(node.args) + [word.value for word in node.keywords]
        if _kind_of(one, kinds, published, aliases) in (_MAP, _KEYS, _KEY)
    ]
    if not carried:
        return ""
    target = _resolved(_target_path(node.func), aliases)
    for part in target:
        if part in _BINARY64_READERS:
            return (
                f"{where} hands a key of a mapping the description "
                f"publishes to `{'.'.join(target)}`. A key is decimal "
                f"text and a row count is not a number binary64 holds "
                f"past nine quadrillion, so this reads a key the "
                f"contract admitted as a number one short of it "
                f"(review item P3-V8-F5). `contract.occurrence_size` is "
                f"the reader for it"
            )
    # A reader named where a VALUE belongs reaches every key without
    # being called here at all: `map(float, published)` is the shape.
    for one in list(node.args) + [word.value for word in node.keywords]:
        named = _resolved(_target_path(one), aliases)
        for part in named:
            if part in _BINARY64_READERS:
                return (
                    f"{where} names `{'.'.join(named)}` beside a mapping "
                    f"the description publishes. A reader that answers "
                    f"in binary64 does not have to be CALLED here to "
                    f"read these keys -- handing it to something that "
                    f"walks them reads every one (review item "
                    f"P3-V8-F5)"
                )
    if _UNREADABLE in target:
        return (
            f"{where} hands a key of a mapping the description "
            f"publishes to something this walk cannot name -- a call "
            f"through a subscript, a returned function, or an "
            f"expression. The walk cannot say which reader that is, so "
            f"it cannot say the key is read exactly (review item "
            f"P3-V8-F5)"
        )
    return ""


def _the_keys_of(
    trees: "dict[str, ast.Module]", published: "tuple[str, ...]"
) -> "tuple[str, tuple[tuple[str, str], ...]]":
    """Follow every published key through the shipped code; say what it met.

    Returns the complaint -- empty where every key is read exactly --
    and every (module, function) the walk found holding one. Taking the
    parsed modules as an argument is what lets the probes below run the
    SAME walk over a doctored tree: a guard whose teeth are described
    rather than exercised is the guard round 6 walked past.
    """
    functions: dict[str, dict[str, ast.AST]] = {}
    aliases: dict[str, dict[str, tuple[str, ...]]] = {}
    for module_name in trees:
        found: dict[str, ast.AST] = {}
        for node in ast.walk(trees[module_name]):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found[node.name] = node
        functions[module_name] = found
        aliases[module_name] = _aliases_in(trees[module_name])
    seeds: dict[tuple[str, str], dict[str, str]] = {}
    for module_name in sorted(functions):
        for name in sorted(functions[module_name]):
            seeds[(module_name, name)] = _seed_of(
                functions[module_name][name]
            )
    holding: dict[tuple[str, str], int] = {}
    moving = True
    rounds = 0
    while moving and rounds < 12:
        moving = False
        rounds = rounds + 1
        for module_name in sorted(functions):
            here = aliases[module_name]
            for name in sorted(functions[module_name]):
                body = functions[module_name][name]
                kinds = _kinds_in(
                    body, seeds[(module_name, name)], published, here
                )
                carries = [one for one in kinds if kinds[one]]
                if carries:
                    holding[(module_name, name)] = 1
                where = f"`{module_name}.{name}`"
                for node in ast.walk(body):
                    if not isinstance(node, ast.Call):
                        continue
                    complaint = _complaint_at(
                        node, kinds, published, here, where
                    )
                    if complaint:
                        return (complaint, tuple(sorted(holding)))
                    landed = _landing(node, functions, here, module_name)
                    if landed is None:
                        continue
                    given = _handed_on(node, functions[landed[0]][landed[1]])
                    for place, argument in given:
                        kind = _kind_of(argument, kinds, published, here)
                        if not kind:
                            continue
                        if seeds[landed].get(place) == kind:
                            continue
                        seeds[landed][place] = kind
                        moving = True
    return ("", tuple(sorted(holding)))


def _landing(
    node: ast.Call,
    functions: "dict[str, dict[str, ast.AST]]",
    aliases: "dict[str, tuple[str, ...]]",
    module_name: str,
) -> "tuple[str, str] | None":
    """Which shipped function one call lands in, if the walk can read it."""
    target = _resolved(_target_path(node.func), aliases)
    if not target or _UNREADABLE in target:
        return None
    last = target[len(target) - 1]
    if len(target) == 1 and last in functions.get(module_name, {}):
        return (module_name, last)
    if len(target) > 1:
        held = target[len(target) - 2]
        if held in functions and last in functions[held]:
            return (held, last)
    return None


def _handed_on(
    node: ast.Call, landed: ast.AST
) -> "list[tuple[str, ast.AST]]":
    """Each argument of one call, paired with the parameter it fills."""
    names = _parameters_of(landed)
    given: list[tuple[str, ast.AST]] = []
    for place, argument in enumerate(node.args):
        if place < len(names):
            given = given + [(names[place], argument)]
    for word in node.keywords:
        if word.arg is not None:
            given = given + [(word.arg, word.value)]
    return given


def test_no_published_key_is_read_by_a_reader_that_answers_in_binary64(
) -> None:
    """THE CLASS, NOT THE CASE, AND FOLLOWING THE VALUE RATHER THAN A RULE.

    Four repairs of the exactness class have now been written and every
    one was a different site, so a guard rooted at any one decision
    leaves the next site open -- which is exactly what happened here,
    with a guard that walks the closure of the rule deciding which cells
    are read while the defect sat in the rule deciding whether a twin
    exists.

    So this walks the KEYS. Every field the profile contract annotates
    `dict[str, ...]` is a mapping whose keys are text the description
    states; wherever the shipped code reads those keys out, this follows
    them through assignments and through calls into other shipped
    functions, and asserts that not one of them reaches `parse_number`,
    `float`, `round` or `complex`. `int` is allowed by name, because on
    decimal text it is exact at every size and it is what the contract's
    loader reads the key with.
    """
    trees = _shipped_trees()
    assert "contract" in trees
    published = _published_maps(trees["contract"])
    assert "n_distinct_by_occurrences" in published
    assert "variants_withheld" in published
    assert "numeric_styles" in published
    complaint, holding = _the_keys_of(trees, published)
    assert not complaint, complaint
    # THE WALK HAS TO HAVE GONE WHERE THE DEFECT WAS. Naming the four
    # readers the review found is not the guard -- the guard is the walk
    # above -- but a walk that reached none of them would satisfy every
    # assertion here while asserting nothing at all.
    for reached in (
        ("validation", "_group_sizes"),
        ("validation", "_widest_group"),
        ("validation", "_occurrence_key"),
        ("validation", "_group_span"),
        ("validation", "_spelling_supply"),
        ("contract", "occurrence_size"),
        ("generation", "_groups_of"),
    ):
        assert reached in holding, reached
    # ...and it has to have left one module, or its cross-module claim
    # is asserting nothing.
    assert len({where[0] for where in holding}) >= 3, holding


# EVERY WAY OF SPELLING THE CALL THAT THIS GUARD HAS BEEN SHOWN. Each
# entry is a whole stand-in `validation` module, so the walk starts
# where it really starts and the probe is the only thing it finds; each
# carries the words its complaint has to contain, so a probe cannot be
# satisfied by the walk complaining about something else.
_PROBES = {
    "straight-off-the-attribute": (
        """
from synthtwin import parsing


def _widest(facts):
    widest = 0
    for key in facts.n_distinct_by_occurrences:
        widest = max(widest, int(parsing.parse_number(key)))
    return widest
""",
        "parsing.parse_number",
    ),
    "through-a-sorted-walk": (
        """
from synthtwin import parsing


def _sizes(facts):
    found = []
    for key in sorted(facts.numeric_styles):
        found = found + [parsing.parse_number(key)]
    return found
""",
        "parsing.parse_number",
    ),
    "off-an-annotated-parameter": (
        '''
def _widest(occurrences: "dict[str, int]") -> int:
    widest = 0
    for key in occurrences:
        widest = max(widest, int(float(key)))
    return widest
''',
        "float",
    ),
    "one-hop-into-a-helper": (
        """
from synthtwin import parsing


def _read(key):
    return parsing.parse_number(key)


def _widest(facts):
    widest = 0
    for spelling in facts.variants_withheld:
        widest = max(widest, _read(spelling))
    return widest
""",
        "parsing.parse_number",
    ),
    "under-another-name": (
        """
from synthtwin.parsing import parse_number as reader


def _widest(facts):
    widest = 0
    for key in facts.n_distinct_by_occurrences:
        widest = max(widest, reader(key))
    return widest
""",
        "parse_number",
    ),
    "through-a-subscript": (
        """
readers = (float,)


def _widest(facts):
    widest = 0
    for key in facts.n_distinct_by_occurrences:
        widest = max(widest, readers[0](key))
    return widest
""",
        "cannot name",
    ),
    "the-site-the-review-found": (
        '''
from synthtwin import parsing


def _widest_group(occurrences: "dict[str, int]") -> int:
    """The shipped reader exactly as review round 8 found it."""
    widest = 0
    for key in occurrences:
        size = parsing.parse_number(key)
        if size is None:
            continue
        widest = max(widest, int(size))
    return widest
''',
        "parse_number",
    ),
    "handed-to-a-walk": (
        """
from synthtwin import parsing


def _sizes(facts):
    return list(map(parsing.parse_number, facts.n_distinct_by_occurrences))
""",
        "parsing.parse_number",
    ),
}


@pytest.mark.parametrize("route", sorted(_PROBES))
def test_the_guard_complains_about_each_way_of_spelling_it(
    route: str,
) -> None:
    """The teeth, exercised rather than described.

    Each probe is a module the walk is really run over, spelling the
    same defect a different way: the shipped site as the review found
    it, straight off the published attribute, through `sorted`, off a
    parameter the annotation says is a mapping, one hop into a helper,
    under an import alias, through a subscript the walk cannot read, and
    handed to something that walks the keys without calling the reader
    here at all.
    """
    source, words = _PROBES[route]
    trees = _shipped_trees()
    published = _published_maps(trees["contract"])
    trees["validation"] = ast.parse(source)
    complaint, _holding = _the_keys_of(trees, published)
    assert complaint, route
    assert words in complaint, (route, complaint)


def test_every_probe_names_a_route_the_shipped_code_could_take(
) -> None:
    """NOT VACUOUS: each probe has to parse and to be about a key."""
    for route in sorted(_PROBES):
        source, _words = _PROBES[route]
        tree = ast.parse(source)
        assert [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ], route
    assert len(_PROBES) == 8
