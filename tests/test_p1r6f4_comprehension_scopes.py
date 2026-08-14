"""Scanner mutation checks for comprehension scopes (P1-R6-F4).

Round 6 postponed def, async def and lambda bodies, but stopped at the
forms the review named. Python has a THIRD deferred form -- the
generator expression -- and all four comprehension forms carry a scope
of their own. Both omissions produced the same misplaced trust:

* a generator expression read where it stands is read against a
  half-built scope, so a store written below it is missing from the
  origin set at the moment trust is granted;
* a comprehension's loop variable is not the surrounding name, so
  `[Path(v) for Path in items]` calls whatever the caller's `items`
  yields, while the scanner went on reading `Path` as the import.

Each mutation below RUNS as written. The green tests underneath keep
the repair from turning into a blanket refusal of comprehensions: the
loop variable must stay inside the comprehension, a walrus must still
escape it, and ordinary comprehension code must stay clean.

ROUND 7 added the second half of this file. Round 6's repair moved
trust onto a position-blind view of each scope but kept the walk's own
position-sensitive view reachable beside it and returned the union of
the two answers, which still let a name the blind view did not bind at
all be resolved from what the walk had reached. The tests below hold
the finished rule: no trust decision can reach the walk's stack, and
the collector that fills the blind view is held to Python's own
grammar, one binding form at a time, in each kind of scope.

TWO of the mutations below are written in syntax that arrived in
Python 3.12, and this project supports 3.10 upward. Those two split on
`sys.version_info`; see `_PEP695_PARSES` below for why the split keeps
the whole of the property on every supported version rather than
trading the floor away for a green run.
"""

import ast
import importlib.util
import pathlib
import re
import sys
import textwrap

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNER_PATH = REPO_ROOT / "tools" / "offline_scan" / "scan_imports.py"
SRC_TREE = REPO_ROOT / "src" / "synthtwin"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("scan_imports", SCANNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SCANNER = _load_scanner()

_PROVENANCE = "trace to validate_local_path"

# PEP 695 -- `def name[T](...)` and the `type X = ...` statement -- is
# syntax that Python 3.12 introduced. On 3.10 and 3.11 the two probe
# modules that use it are not Python at all, so the scanner never
# reaches the rule those two tests pin: `ast.parse` raises before any
# rule runs.
#
# That is not a hole, because the scanner FAILS CLOSED. A file it
# cannot parse comes back as one violation of its own (`_UNPARSEABLE`
# below), so the module is refused rather than passed, which is the
# behaviour that protects the project on those versions -- a security
# control that cannot read a file must never call it clean. So the two
# tests assert the specific rule where the syntax parses and the
# refusal where it does not, and neither version is left asserting
# nothing.
_PEP695_PARSES = sys.version_info >= (3, 12)

# The text the scanner reports for a file it could not parse, taken
# from `scan_source`. It carries the reason from Python's own
# SyntaxError after it, which differs between versions, so only the
# scanner's own constant wording is matched here.
_UNPARSEABLE = "could not be parsed as Python"


def _scan_code(tmp_path, code):
    """Write one module into a fresh tree and scan that tree."""
    tree = tmp_path / "tree"
    tree.mkdir()
    (
        tree / "sample.py").write_text(textwrap.dedent(code),
        encoding="utf-8",
        newline="\n",
    )
    return _SCANNER.scan_tree(tree)


def _assert_red(violations, needle):
    assert violations, (
        "expected the scanner to go red on this mutation, but it "
        "reported nothing"
    )
    joined = "\n".join(violations)
    assert needle in joined, (
        "expected a violation mentioning " + repr(needle) + ", got:\n" + joined
    )
    for line in violations:
        assert re.search(r":\d+: ", line), (
            "violation line is not in 'file:line: explanation' form: " + line
        )


# -- the third deferred form: a generator expression ------------------


def test_a_generator_expression_body_sees_a_rebinding_below_it(tmp_path):
    # The reviewer's round-6 example with the def replaced by the third
    # deferred form. Nothing inside the parentheses runs until something
    # draws from `frames`; the last statement of the module has run long
    # before that, so the reader is handed the web address.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        frames = (
            pandas.read_csv(Path(validate_local_path(name, purpose="input")))
            for name in ["data.csv"]
        )

        Path = substitute_path
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_generator_expression_in_a_function_sees_a_later_rebinding(tmp_path):
    # The same postponement one scope in: the expression is built on the
    # first line and drawn from by the caller, after `Path` has been
    # rebound two lines below it.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def outer(raw_path, names):
            validated = validate_local_path(raw_path, purpose="input")
            frames = (pandas.read_csv(Path(validated)) for name in names)
            Path = str
            return frames
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_an_async_comprehension_body_sees_a_rebinding_below_it(tmp_path):
    # A comprehension carrying `async for` runs later for the same
    # reason a generator expression does, so it is postponed too.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        async def fetch(raw_path, names):
            validated = validate_local_path(raw_path, purpose="input")
            frames = [pandas.read_csv(Path(validated)) async for name in names]
            Path = str
            return frames
        """,
    )
    _assert_red(violations, _PROVENANCE)


# -- a comprehension is a scope of its own ----------------------------


def test_a_list_comprehension_target_shadows_the_import(tmp_path):
    # `Path` inside the brackets is the loop variable, so the value that
    # reaches the reader is whatever the caller's `candidates` yields --
    # a web address, on the caller's choosing. The import above settles
    # nothing about it.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, candidates):
            validated = validate_local_path(raw_path, purpose="input")
            return [pandas.read_csv(Path(validated)) for Path in candidates]
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_set_comprehension_target_shadows_the_import(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, candidates):
            validated = validate_local_path(raw_path, purpose="input")
            return {pandas.read_csv(Path(validated)) for Path in candidates}
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_dict_comprehension_target_shadows_the_import(tmp_path):
    # The dict form carries two result expressions rather than one, and
    # a tuple target rather than a plain name; both have to be read in
    # the comprehension's own scope.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, candidates):
            validated = validate_local_path(raw_path, purpose="input")
            return {
                name: pandas.read_csv(Path(validated))
                for Path, name in candidates
            }
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_generator_expression_target_shadows_the_import(tmp_path):
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, candidates):
            validated = validate_local_path(raw_path, purpose="input")
            return (pandas.read_csv(Path(validated)) for Path in candidates)
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_nested_comprehension_target_shadows_the_import(tmp_path):
    # The inner comprehension is a scope inside a scope; the shadowing
    # has to hold at every depth, exactly as the postponement does.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, groups):
            validated = validate_local_path(raw_path, purpose="input")
            return [
                [pandas.read_csv(Path(validated)) for Path in group]
                for group in groups
            ]
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_second_generator_iterable_is_read_in_the_inner_scope(tmp_path):
    # Only the FIRST iterable is evaluated where the comprehension
    # stands; every later one is evaluated inside the comprehension,
    # where the earlier targets are already in force. (This one was
    # red before the repair too, for a different reason -- the walk
    # happened to reach the target store first. It is kept because it
    # pins the inner-scope reading the repair now relies on: hoisting
    # every iterable out to the surrounding scope would turn it green.)
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, candidates):
            validated = validate_local_path(raw_path, purpose="input")
            return [
                row
                for Path in candidates
                for row in pandas.read_csv(Path(validated))
            ]
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_comprehension_target_that_is_not_a_name_is_refused(tmp_path):
    # `for holder.slot in rows` stores into an object that outlives the
    # comprehension, at a moment this audit cannot place. A construct it
    # cannot reason about is refused rather than admitted.
    violations = _scan_code(
        tmp_path,
        """
        def collect(rows, holder):
            return [1 for holder.slot in rows]
        """,
    )
    _assert_red(violations, "comprehension's loop variable")


# -- an unreadable file is refused, on every supported version --------


def test_a_file_the_scanner_cannot_parse_is_refused(tmp_path):
    """A file the audit cannot read must never be treated as clean.

    This is the property the two version-split tests below lean on, so
    it is pinned here on its own and on EVERY supported version: the
    source is broken in a way no Python parses, past or future. The
    scanner is a security control, and a control that shrugs at a file
    it could not read is worse than no control, because the run still
    ends 0 and the reader believes the tree was audited.
    """
    violations = _scan_code(tmp_path, "def fetch(:\n    pass\n")
    _assert_red(violations, _UNPARSEABLE)
    assert len(violations) == 1, (
        "an unparseable file is reported once, as the parse failure "
        "itself: " + "\n".join(violations)
    )


def test_a_file_the_scanner_cannot_decode_is_refused(tmp_path):
    """The same rule one step earlier: bytes that are not UTF-8 text.

    `scan_files` reads every file as UTF-8 before anything is parsed. A
    file that fails there is never handed to the parser at all, so it
    needs its own refusal or it would leave the scan silently.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "sample.py").write_bytes(b"value = '\xff\xfe not utf-8'\n")
    violations = _SCANNER.scan_tree(tree)
    _assert_red(violations, "could not be decoded as UTF-8 text")


# -- the other lazily evaluated forms, refused rather than admitted ---


def test_a_type_parameter_list_is_refused(tmp_path):
    # `def fetch[Path](...)` binds Path in a lazily evaluated scope
    # wrapped around the definition, where the name lives in a plain
    # string field and no store is ever recorded. Every `Path` in the
    # body is that parameter, not the import. The scope is not modelled,
    # so the form is refused.
    #
    # The square-bracket form is 3.12 syntax. On 3.10 and 3.11 this
    # module does not parse, and the refusal that protects the project
    # there is the parse refusal -- checked rather than skipped, so the
    # floor really asserts that the module is turned away.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch[Path](raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            return pandas.read_csv(Path(validated))
        """,
    )
    if _PEP695_PARSES:
        _assert_red(violations, "type parameters in square brackets")
    else:
        _assert_red(violations, _UNPARSEABLE)


def test_a_type_alias_statement_is_refused(tmp_path):
    # What follows the '=' in a `type` statement is held and evaluated
    # on first use, in a scope of its own -- so the module-level store
    # below it has already run by then.
    #
    # `type` became a soft keyword in 3.12; on 3.10 and 3.11 the line
    # is two names side by side and the module does not parse, so the
    # same split as above applies.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        type Table = pandas.read_csv(
            Path(validate_local_path("data.csv", purpose="input"))
        )

        Path = substitute_path
        """,
    )
    if _PEP695_PARSES:
        _assert_red(violations, "'type' alias statement")
    else:
        _assert_red(violations, _UNPARSEABLE)


def test_the_version_split_matches_what_the_interpreter_can_parse():
    """`_PEP695_PARSES` must agree with the running interpreter.

    The two tests above choose which message to assert from a version
    comparison written by hand. If that comparison ever disagreed with
    the interpreter actually running them, both would assert the wrong
    half and the disagreement would never show. So the claim is checked
    against `ast` itself rather than trusted.
    """
    try:
        ast.parse("type Table = int\n")
        ast.parse("def fetch[T](value):\n    return value\n")
    except SyntaxError:
        parses = False
    else:
        parses = True
    assert parses is _PEP695_PARSES, (
        "_PEP695_PARSES says "
        + str(_PEP695_PARSES)
        + " but this interpreter ("
        + ".".join(str(piece) for piece in sys.version_info[:3])
        + ") says "
        + str(parses)
    )


# -- the repair is not a blanket refusal ------------------------------


def test_the_real_src_tree_is_still_clean():
    """The shipped tree uses comprehensions in both forms and must stay
    green: the repair rejects the shadowing and the postponement error,
    not the construct."""
    violations = _SCANNER.scan_tree(SRC_TREE)
    assert violations == [], "\n".join(violations)


def test_ordinary_comprehensions_over_a_validated_path_stay_clean(tmp_path):
    # The honest shape of every form the repair touches, eager and lazy,
    # with nothing rebound below them.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            frames = [pandas.read_csv(Path(validated)) for _ in range(1)]
            lazy = (pandas.read_csv(Path(validated)) for _ in range(1))
            return frames, lazy
        """,
    )
    assert violations == [], violations


def test_comprehensions_over_checked_text_stay_clean(tmp_path):
    # All four forms, nested, over a parameter the type check accepted
    # as text. Nothing here is postponed wrongly and nothing shadows an
    # import, so nothing is reported.
    violations = _scan_code(
        tmp_path,
        """
        import json

        def collect(raw: str) -> str:
            if not isinstance(raw, str):
                raise ValueError("give this function a piece of text")
            rows = [raw.strip() for _ in range(2)]
            mapping = {key: len(key) for key in rows}
            widths = {len(key) for key in rows}
            stream = (len(key) for key in rows)
            nested = [[len(key) for key in rows] for _ in range(2)]
            return json.dumps(mapping) + str(widths) + str(nested) + str(stream)
        """,
    )
    assert violations == [], violations


def test_the_first_iterable_is_refused_when_a_later_store_rebinds(tmp_path):
    """Corrected at round 7.

    This once asserted the module below stays clean, which matches how
    Python itself behaves: the first iterable of a generator expression
    is evaluated where the expression stands.

    The scanner now settles trust without modelling position. The origin
    set of a name is the union of every binding it takes anywhere in the
    scope, above the use or below it. Four repairs tried to track where
    each binding takes effect and each was beaten one construct over, so
    the fifth stops tracking. The price appears here: a module that is
    in fact safe is refused, because the name it reads through is
    rebound elsewhere in the same scope.

    That price is paid openly rather than written around, since an
    exception for "this position is safe" is the same reasoning that was
    beaten four times. A refusal costs a contributor one message and one edit;
    trust granted over half a scope costs a user their data in silence.

    The property this once pinned -- the first iterable being read in
    the surrounding scope, not inside the comprehension -- is kept by
    the two tests below, which need no rebinding to show it.
    """
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        rows = (
            row
            for row in pandas.read_csv(
                Path(validate_local_path("data.csv", purpose="input"))
            )
        )

        Path = substitute_path
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_the_first_iterable_is_read_where_the_comprehension_stands(tmp_path):
    # The counterweight to the postponement, restated so that it turns
    # on the SCOPE the first iterable is read in rather than on a store
    # written below it. The comprehension's own target is named
    # `validated`, which shadows the surrounding `validated` everywhere
    # INSIDE the brackets -- but the first iterable is evaluated where
    # the comprehension stands, in the function around it, so the
    # `validated` handed to Path() there is still the validated path.
    # Reading the first iterable inside the comprehension's scope would
    # report this correct code; postponing it would too.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path):
            validated = validate_local_path(raw_path, purpose="input")
            return [row for validated in pandas.read_csv(Path(validated))]
        """,
    )
    assert violations == [], violations


def test_an_honest_first_iterable_with_nothing_rebound_stays_clean(tmp_path):
    # The plain shape, kept green so the correction above cannot quietly
    # become a blanket refusal of a fenced read inside a generator
    # expression's first iterable.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        rows = (
            row
            for row in pandas.read_csv(
                Path(validate_local_path("data.csv", purpose="input"))
            )
        )
        """,
    )
    assert violations == [], violations


def test_a_comprehension_target_does_not_leak_out_of_it(tmp_path):
    # The other half of the scope rule. Python does not let a loop
    # variable escape a comprehension, so the `Path` used after the
    # brackets is still the import and the read is honest. Recording the
    # target in the surrounding scope would have reported this correct
    # code.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def fetch(raw_path, rows):
            validated = validate_local_path(raw_path, purpose="input")
            seen = [Path for Path in rows]
            return pandas.read_csv(Path(validated)), seen
        """,
    )
    assert violations == [], violations


def test_a_walrus_inside_a_comprehension_still_rebinds_the_outer_name(tmp_path):
    # The one binding that deliberately escapes a comprehension. Python
    # stores `:=` in the function around it, so `Path` below the
    # brackets is the substitute -- and giving the comprehension a scope
    # of its own must not swallow that store.
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        def fetch(raw_path, items):
            validated = validate_local_path(raw_path, purpose="input")
            keep = [(Path := substitute_path) for item in items]
            return pandas.read_csv(Path(validated)), keep
        """,
    )
    _assert_red(violations, _PROVENANCE)


def test_a_walrus_outside_a_comprehension_still_binds_where_it_stands(tmp_path):
    # The walrus rule must not have changed anything outside a
    # comprehension: an ordinary `:=` in an if statement stays clean.
    violations = _scan_code(
        tmp_path,
        """
        import json

        def collect(raw: str):
            if not isinstance(raw, str):
                raise ValueError("give this function a piece of text")
            if (parsed := json.loads(raw)):
                return parsed
            return None
        """,
    )
    assert violations == [], violations


# =====================================================================
# ROUND 7: trust is position-blind, and there is no path back
# =====================================================================


def _scan_package(tmp_path, modules):
    """Write several first-party modules into a fresh tree and scan it."""
    tree = tmp_path / "tree"
    package = tree / "synthtwin"
    package.mkdir(parents=True)
    for name, text in modules.items():
        (
            package / name).write_text(textwrap.dedent(text),
            encoding="utf-8",
            newline="\n",
        )
    return _SCANNER.scan_tree(tree)


# The three low-level readers. Each answers against WHICHEVER scope
# stack is in force, so a call to one of them is a call that has to say
# which view it meant.
_VIEW_RELATIVE_READERS = frozenset({"_lookup", "_resolve", "_value_origins"})

# Methods that are themselves view-relative: they are driven from both
# views (the walk's own and the position-blind one) and read whichever
# is in force, exactly as the readers above do.
_VIEW_RELATIVE_METHODS = frozenset(
    {
        "_resolve",
        "_value_origins",
        "_call_result_origins",
        "_bind_from_value",
    }
)

# The trust entry points. Each opens the position-blind view before it
# reads anything, and every grant in the scanner goes through one of
# them (or through _resolve_exclusively, which goes through these).
_TRUST_ENTRY_POINTS = frozenset({"_trust_lookup", "_trust_origins", "_trust_resolve"})

# The methods that deliberately read the walk's own, position-sensitive
# view -- and the reason each one may. Every one of them REPORTS; none
# of them grants. Reporting a statement against a store written below it
# would call honest code a violation, which is why this view exists at
# all. A method added to this list is a policy decision, not a routine
# change: it is the list the next reviewer checks first.
_CHECKING_QUESTIONS = {
    "visit_Name": "reports a bare name whose origin the policy forbids",
    "visit_Attribute": "reports a dotted chain the policy forbids",
    "visit_Subscript": "reports a write to os.environ",
    "_check_callable_arguments": "reports a scanned function handed outward",
    "_slot_flagged_elsewhere": (
        "suppresses the duplicate of a message the line above raised, and "
        "reads the same view that raised it"
    ),
}


def _methods_reading_the_walk_view():
    """{method name: readers it calls} for the scanner's checker class."""
    tree = ast.parse(SCANNER_PATH.read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for member in node.body:
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            used = set()
            for inner in ast.walk(member):
                if not isinstance(inner, ast.Call):
                    continue
                callee = inner.func
                if not isinstance(callee, ast.Attribute):
                    continue
                if not isinstance(callee.value, ast.Name) or callee.value.id != "self":
                    continue
                if callee.attr in _VIEW_RELATIVE_READERS:
                    used.add(callee.attr)
            if used:
                found[member.name] = used
    return found


def test_only_the_reporting_questions_read_the_walk_view():
    """No method outside the enumerated reporting set reads the scope
    stack directly.

    This is the structural half of the round-7 repair. The fourth
    attempt did not fail because someone believed position was safe; it
    failed because a trust path still had a reference to the walk's own
    view and used it. Reading that view is now confined by name to
    methods that only ever RAISE a message, plus the readers themselves
    and the trust entry points that open the blind view before calling
    them. A future edit that reaches for the walk's view inside a
    granting decision fails here rather than in the next review.
    """
    reading = _methods_reading_the_walk_view()
    allowed = (
        _VIEW_RELATIVE_METHODS | _TRUST_ENTRY_POINTS | set(_CHECKING_QUESTIONS)
    )
    unexpected = sorted(set(reading) - allowed)
    assert not unexpected, (
        "these methods read the scope stack directly and are not "
        "classified as reporting-only, view-relative, or a trust entry "
        "point: " + ", ".join(unexpected)
    )
    # And the classification is not stale: every name on the lists is a
    # method that really does read.
    for name in sorted(_TRUST_ENTRY_POINTS | set(_CHECKING_QUESTIONS)):
        assert name in reading, (
            name + " is classified as reading the scope stack but no "
            "longer reads it; the classification is stale"
        )


# The four entry points a trust question is asked through, plus the
# step that fills the position-blind set. From the moment one of these
# is entered to the moment it returns, every scope read taken must land
# on the position-blind stack -- INCLUDING a read taken after the view
# has been closed again, which is exactly what the fourth repair did
# when it unioned in a second answer on its way out.
_TRUST_CALLS = (
    "_trust_origins",
    "_trust_lookup",
    "_trust_resolve",
    "_resolve_exclusively",
    "_build_trust_scope",
)


def _trace_views(code):
    """Scan `code`, recording which stack was in force at every read
    taken anywhere inside a trust question."""
    checker = _SCANNER._Checker()
    state = {"inside": 0}
    reads = []

    def watch(original):
        def wrapper(*arguments):
            state["inside"] += 1
            try:
                return original(*arguments)
            finally:
                state["inside"] -= 1

        return wrapper

    def watch_read(original):
        def wrapper(*arguments):
            if state["inside"]:
                reads.append(checker.scopes is checker.trust_scopes)
            return original(*arguments)

        return wrapper

    for name in _TRUST_CALLS:
        setattr(checker, name, watch(getattr(checker, name)))
    for name in ("_lookup", "_resolve", "_value_origins"):
        setattr(checker, name, watch_read(getattr(checker, name)))
    checker.visit(ast.parse(textwrap.dedent(code)))
    return reads


def test_every_read_under_a_trust_question_is_position_blind():
    """The running half of the same property.

    The test above reads the source; this one watches the scanner work.
    Every time a trust question is open, every scope read taken under it
    must land on the position-blind stack. One read landing on the
    walk's own stack is the round-6 defect back again.
    """
    reads = _trace_views(
        """
        import pandas
        import json
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        def fetch(raw_path, rows):
            if not isinstance(raw_path, str):
                raise ValueError("give this a path")
            validated = validate_local_path(raw_path.strip(), purpose="input")
            handle = Path(validated)
            frames = [pandas.read_csv(handle) for _ in rows]
            lazy = (pandas.read_csv(handle) for _ in rows)
            label = f"{len(frames):{'>4'}}"
            return json.dumps({"n": label}), lazy

        class Holder:
            reader = fetch
        """
    )
    assert reads, (
        "no read was taken under a trust question at all; the trace is "
        "not watching what it claims to watch"
    )
    assert all(reads), (
        str(reads.count(False))
        + " of "
        + str(len(reads))
        + " reads taken while a trust question was open landed on the "
        "walk's own position-sensitive stack"
    )


# One snippet per binding form in Python's grammar, each binding
# `marker` at the BOTTOM of a loop body -- textually below everything
# above it, and in force on every iteration after the first.
_IN_FUNCTION = {
    "FunctionDef": "for _row in [1]:\n    def marker():\n        return 1\n",
    "AsyncFunctionDef": (
        "for _row in [1]:\n    async def marker():\n        return 1\n"
    ),
    "ClassDef": "for _row in [1]:\n    class marker:\n        pass\n",
    "Name": "for _row in [1]:\n    marker = 1\n",
    "alias": "for _row in [1]:\n    import json as marker\n",
    "ExceptHandler": (
        "for _row in [1]:\n"
        "    try:\n"
        "        pass\n"
        "    except OSError as marker:\n"
        "        pass\n"
    ),
    "MatchAs": (
        "for _row in [1]:\n"
        "    match [1]:\n"
        "        case [marker]:\n"
        "            pass\n"
    ),
    "MatchStar": (
        "for _row in [1]:\n"
        "    match [1]:\n"
        "        case [*marker]:\n"
        "            pass\n"
    ),
    "MatchMapping": (
        "for _row in [1]:\n"
        "    match {}:\n"
        "        case {**marker}:\n"
        "            pass\n"
    ),
    "Global": "global marker\n",
    "Nonlocal": "nonlocal marker\n",
    "TypeVar": None,
    "ParamSpec": None,
    "TypeVarTuple": None,
    "arg": None,
}


def _trust_lookup_in_function(body_text, name):
    """Build a function scope's position-blind set the way the scanner
    builds it, and ask the very helper a trust decision asks."""
    code = "def outer():\n" + textwrap.indent(textwrap.dedent(body_text), "    ")
    tree = ast.parse(code)
    function = tree.body[0]
    checker = _SCANNER._Checker()
    checker._collect_scope_bindings(tree.body)
    checker._build_trust_scope(list(tree.body), None)
    seeded = {
        parameter.arg: {_SCANNER._UNKNOWN}
        for parameter in _SCANNER._parameters_of(function.args)
    }
    checker._enter_scope(seeded, False, False)
    checker._collect_scope_bindings(function.body)
    checker._build_trust_scope(list(function.body), function.body)
    return checker._trust_lookup(name)


def _trust_lookup_in_class(body_text, name):
    """The same, for a class body -- the scope kind whose statements run
    while the class is being built."""
    code = "class Holder:\n" + textwrap.indent(textwrap.dedent(body_text), "    ")
    tree = ast.parse(code)
    holder = tree.body[0]
    checker = _SCANNER._Checker()
    checker._collect_scope_bindings(tree.body)
    checker._build_trust_scope(list(tree.body), None)
    checker._enter_scope({}, True, False)
    checker._collect_scope_bindings(holder.body)
    checker._build_trust_scope(list(holder.body), None)
    return checker._trust_lookup(name)


def test_the_collector_models_every_binding_form_in_a_function_scope(tmp_path):
    """Walk Python's own grammar and hold the collector to it, one
    binding form at a time, inside a FUNCTION body.

    The property every trust decision now rests on is that the
    position-blind set of a scope already holds every name that scope
    binds, before a single statement of it has been checked. A form the
    collector skips is a name missing from that set, which is exactly
    how four rounds of misplaced trust happened. So this walks the ast
    module of the running interpreter rather than a list written from
    memory: a node type a future Python adds arrives unclassified and
    fails here.

    Each name is read back through `_trust_lookup` -- the helper a trust
    decision actually calls -- rather than by reaching into the
    dictionary, so a record the collector makes somewhere a trust
    question cannot see it does not count.
    """
    binding = _SCANNER._BINDING_IDENTIFIER_FIELDS
    treatment = _SCANNER._BINDING_FORM_TREATMENT
    assert set(_IN_FUNCTION) == set(binding), (
        "every binding form in the scanner's grammar table needs a "
        "function-scope self-check"
    )
    checked = 0
    for node_name in sorted(binding):
        if not hasattr(ast, node_name):
            continue
        body_text = _IN_FUNCTION[node_name]
        if body_text is None:
            # Refused where it stands, or seeded in a scope of its own;
            # both are covered by the whole-module tests elsewhere in
            # this file and in test_offline_scan.py.
            assert treatment[node_name] in ("refused", "scope-local"), (
                node_name + " has no function-scope snippet but is "
                "recorded as collected"
            )
            continue
        try:
            ast.parse("def outer():\n" + textwrap.indent(body_text, "    "))
        except SyntaxError:
            continue
        if treatment[node_name] == "refused":
            # `global marker` / `nonlocal marker` bind in a scope this
            # audit does not follow. The collector records the name so
            # nothing downstream reads a stale origin, and the visitor
            # refuses the statement outright.
            holder = tmp_path / node_name
            holder.mkdir()
            violations = _scan_code(
                holder, "def outer():\n" + textwrap.indent(body_text, "    ")
            )
            assert violations, (
                node_name + " is recorded as refused and the scanner "
                "accepted it"
            )
            checked += 1
            continue
        origins = _trust_lookup_in_function(body_text, "marker")
        assert origins, (
            "the collector did not record the name ast."
            + node_name
            + " binds at the bottom of a loop in a function body, so "
            "every trust decision in that function is taken against an "
            "origin set the binding is missing from"
        )
        checked += 1
    assert checked >= 10, "the grammar walk checked almost nothing"


def test_the_collector_models_every_binding_form_in_a_class_scope(tmp_path):
    """The same walk, in a class body.

    A class body is the scope kind the round-6 review broke the scanner
    with: its statements run while the class is being built, so a name
    used there falls back to the module when the class-level store has
    not run. The position-blind set of a class body must hold every name
    that body binds, on the same rule as every other scope.
    """
    binding = _SCANNER._BINDING_IDENTIFIER_FIELDS
    treatment = _SCANNER._BINDING_FORM_TREATMENT
    checked = 0
    for node_name in sorted(binding):
        if not hasattr(ast, node_name) or treatment[node_name] != "collected":
            continue
        body_text = _IN_FUNCTION[node_name]
        if body_text is None:
            continue
        try:
            ast.parse("class Holder:\n" + textwrap.indent(body_text, "    "))
        except SyntaxError:
            continue
        origins = _trust_lookup_in_class(body_text, "marker")
        assert origins, (
            "the collector did not record the name ast."
            + node_name
            + " binds at the bottom of a loop in a CLASS body"
        )
        checked += 1
    assert checked >= 8, "the class-scope grammar walk checked almost nothing"


def test_a_comprehension_scope_is_position_blind_too(tmp_path):
    """A comprehension has a scope of its own, and that scope's origin
    set is built whole before anything inside it is read.

    A walrus written INSIDE the brackets binds in the function around
    them, and the fenced read written to the left of it must see that
    binding -- there is no left-to-right order on the trust side.
    """
    violations = _scan_code(
        tmp_path,
        """
        import pandas
        from pathlib import Path
        from synthtwin.paths import validate_local_path

        def substitute_path(raw):
            return "https://example.invalid/table.csv"

        def fetch(raw_path, items):
            validated = validate_local_path(raw_path, purpose="input")
            keep = [
                pandas.read_csv(Path(validated))
                for item in items
                if (Path := substitute_path)
            ]
            return keep
        """,
    )
    _assert_red(violations, _PROVENANCE)


# -- the same rule one module over ------------------------------------


def test_a_sibling_that_rebinds_its_export_is_not_trusted(tmp_path):
    """The cross-module half of the same defect.

    `synthtwin.paths` defines `validate_local_path` and rebinds it on
    its last line. The module that imports the name reads only the
    first binding and went on treating what the substitute returns as a
    validated local path -- the identical omission the in-scope repair
    closed, one file over. The importing side now takes the union of the
    sibling's bindings too, and refuses.
    """
    violations = _scan_package(
        tmp_path,
        {
            "paths.py": """
            def validate_local_path(raw, purpose=""):
                return raw


            def substitute(raw, purpose=""):
                return "https://example.invalid/table.csv"


            validate_local_path = substitute
            """,
            "reader.py": """
            import pandas
            from pathlib import Path
            from synthtwin.paths import validate_local_path


            def fetch(raw_path):
                validated = validate_local_path(raw_path, purpose="input")
                return pandas.read_csv(Path(validated))
            """,
        },
    )
    _assert_red(violations, "binds 'validate_local_path' more than once")


def test_a_sibling_rebinding_is_refused_through_the_dotted_form_too(tmp_path):
    """The same, reached as `paths.validate_local_path(...)` rather than
    through a `from` import: one grant, two spellings, and the fourth
    repair closed spellings one at a time."""
    violations = _scan_package(
        tmp_path,
        {
            "paths.py": """
            def validate_local_path(raw, purpose=""):
                return raw


            def substitute(raw, purpose=""):
                return "https://example.invalid/table.csv"


            for validate_local_path in [substitute]:
                pass
            """,
            "reader.py": """
            import pandas
            from pathlib import Path
            from synthtwin import paths


            def fetch(raw_path):
                validated = paths.validate_local_path(raw_path, purpose="input")
                return pandas.read_csv(Path(validated))
            """,
        },
    )
    _assert_red(violations, _PROVENANCE)


def test_a_sibling_with_one_plain_definition_stays_trusted(tmp_path):
    """The counterweight: an ordinary sibling module, bound once and
    used across the package, must stay clean. The cross-module rule
    refuses a name bound twice, not a name bound at all."""
    violations = _scan_package(
        tmp_path,
        {
            "paths.py": """
            def validate_local_path(raw, purpose=""):
                return raw
            """,
            "reader.py": """
            import pandas
            from pathlib import Path
            from synthtwin import paths
            from synthtwin.paths import validate_local_path


            def fetch(raw_path):
                validated = validate_local_path(raw_path, purpose="input")
                return pandas.read_csv(Path(validated))


            def fetch_again(raw_path):
                validated = paths.validate_local_path(raw_path, purpose="input")
                return pandas.read_csv(Path(validated))
            """,
        },
    )
    assert violations == [], violations


def test_a_dataclass_decorated_export_stays_trusted(tmp_path):
    """The shipped tree exports dataclasses, and the cross-module rule
    must not refuse them: dataclasses.dataclass hands the very class it
    was given back, so the name still holds the definition written under
    it."""
    violations = _scan_package(
        tmp_path,
        {
            "shapes.py": """
            import dataclasses


            @dataclasses.dataclass(frozen=True)
            class Holder:
                count: int
            """,
            "reader.py": """
            from synthtwin.shapes import Holder


            def build():
                return Holder(count=1)
            """,
        },
    )
    assert violations == [], violations


def test_a_foreign_decorator_on_an_export_withdraws_trust(tmp_path):
    """And the other side of it: a decorator that is not one of the
    enumerated few is handed the definition and gives back whatever it
    likes, so the exported name no longer holds what the def under it
    says."""
    violations = _scan_package(
        tmp_path,
        {
            "shapes.py": """
            def swap(fn):
                return fn


            @swap
            def build_holder():
                return 1
            """,
            "reader.py": """
            from synthtwin.shapes import build_holder


            def build():
                return build_holder()
            """,
        },
    )
    _assert_red(violations, "build_holder")
