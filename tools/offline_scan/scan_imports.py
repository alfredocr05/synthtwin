"""Offline static scanner for the synthtwin source tree (plan D6.2, D6.5).

What this tool does, in plain terms: synthtwin promises to run fully
offline -- no network, no launching of other programs, no native code,
and no code loaded dynamically while the program runs. This scanner
reads every Python file under a given source tree WITHOUT running it and
checks that the source text names only the enumerated APIs the Phase 0
plan allows. Anything else is reported, one line per problem, and the
scan fails.

SCOPE OF WHAT THIS SCANNER ESTABLISHES (plan D6 Amendment A3, ratified
with conditions by the Phase 0 closure review). This is a best-effort,
mutation-tested layer. It is NOT a proof that every call target in the
scanned source resolves to exactly one built-in implementation. A
reading-only analysis could in principle reject every construct it
cannot resolve; this one accepts a few of them on purpose, so the tool
stays usable on real code. The isinstance type gate under method calls
below is the clearest such case and says exactly what it does and does
not settle.

One residual is named here and repeated wherever this boundary is
described: code supplied BY THE CALLER -- an object or a callable
handed to synthtwin's public functions -- runs in the caller's own
process under the caller's own authority. This boundary governs what
synthtwin's own code initiates, not what a caller chooses to run
against themselves. It is the same residual family as the local-actor
and network-mount residuals already accepted in SECURITY.md.

WHAT THIS SCANNER DOES NOT DECIDE. Stating this precisely is part of
the layer, because four repairs in a row closed a demonstrated example
and left the class open one construct over. The list is short on
purpose: everything else this audit cannot reason about is REFUSED
rather than admitted (the refused forms are enumerated further down --
`global`, `nonlocal`, PEP 695 type parameters, `type X = ...`, a
comprehension target that is not a plain name, a scope whose origin set
does not settle, and a sibling module's name bound more than once).

  1. A caller's object, as above. Nothing in the source text settles
     what a value handed in from outside will do.
  2. READING an attribute of a value this audit cannot trace --
     `thing.field`, and any chain built on one -- is accepted. Python
     runs the object's own property or __getattr__ on such a read, so
     for a caller-supplied object this is case 1 arriving without a
     call in sight. What IS governed is the narrower set the policy
     below enumerates: method CALLS on untraced values are refused
     outright, and attributes of the restricted libraries are reduced
     to an enumerated list. A general rule for attribute reads would
     refuse ordinary first-party code, so this one is left open and
     named here rather than claimed closed.
  3. The isinstance type gate raises confidence that a value is a
     string; it does not settle that it is a built-in str (see the
     note under method calls).
  4. What another actor in the same process does to synthtwin's own
     modules while it runs. The scanned tree may not perform such
     surgery -- writes to an imported module's attributes, sys.modules
     and sys.path are all refused -- but this is a source audit, not a
     run-time guard.

None of this is what holds the reader shut on its own. SECURITY.md
names three controls on that line, and the one that acts while the
program runs is the path-locality check every path passes immediately
before the reader is handed it -- validate_local_path, which refuses
URL forms lexically before any file is opened (plan
phase-1-profiler.md P1-D2.1). This scanner is ONE BEST-EFFORT LAYER
beside it, in the terms SECURITY.md already uses, and a clean scan
should be read as exactly that and no more.

Policy enforced (plan D6.2, a positive AST/name-binding policy;
Phase 1 additions E1-E4 in plan phase-1-profiler.md, P1-D10):

* Allowed modules for src/: argparse, csv, dataclasses, json, pathlib,
  typing, sys (but sys.modules and sys.path may never be read or
  written); from os only the enumerated os.path helpers, os.fspath,
  os.getcwd, os.lstat, and read-only os.environ; from
  importlib.metadata only the version() function; and the two Phase 1
  runtime dependencies numpy and pandas, each reduced to the exact
  attribute names enumerated below. Imports of the synthtwin package's
  own modules are allowed because those files are scanned too. Every
  other import is a violation.
* NO MODULE-LEVEL TRUST. Membership in an allowed module proves
  nothing about what an attribute can do, so every allowed module's
  usable attribute names are enumerated one by one in
  _ALLOWED_MODULE_ATTRS and any name outside its module's enumeration
  is a violation. In particular: sys is reduced to seven data
  attributes (platform, argv, exit, stdout, stderr, executable,
  version_info) -- sys.call_tracing invokes the function it is
  handed, and the trace, profile, audit-hook, and
  async-generator-hook installers register callables the interpreter
  later runs, so none of them are reachable. typing is reduced to the
  two names the src tree uses (Protocol and cast) --
  typing.get_type_hints compiles and evaluates string annotations,
  turning annotation text into running code, and ForwardRef and
  evaluate_forward_ref expose the same evaluation machinery, so every
  other typing attribute is a violation.
* Always forbidden, allowlist aside: __import__,
  importlib.import_module, exec, eval, compile, subprocess, os.system,
  os.exec*, os.spawn*, os.popen, os.fork, os.posix_spawn, ctypes, cffi,
  multiprocessing, and the reflection primitives getattr, setattr,
  delattr, hasattr, vars, globals, locals, and dir. Aliases are traced
  to their origin, so "g = getattr" followed by "g(...)" is caught.
* Every attribute chain that starts from an imported module must
  resolve, in the source text alone, to an exact enumerated API. A
  chain may take exactly ONE attribute step past a module (os.getcwd,
  os.path.join, json.loads, sys.platform,
  importlib.metadata.version); the only deeper forms accepted are the
  read-only os.environ methods (os.environ.get and friends). Anything
  deeper is rejected, and so is any step whose attribute names another
  module (os.path.os, pathlib.os, json.decoder) or starts with an
  underscore: an allowed module that re-exports another module never
  makes that other module's power allowed.
* The same one-step rule applies to the package's own modules, and
  first-party `from` imports are verified against what the named
  sibling module really defines. Every scanned synthtwin module is
  parsed and its top-level names are recorded: names bound by def,
  class, or a plain assignment are genuine and may be imported or
  referenced in one attribute step
  (synthtwin.paths.validate_local_path); names the module itself
  imported are NOT importable from it ("from synthtwin.paths import
  os" is rejected), because that would launder the sibling's own
  imports past this audit -- the object handed over is the real
  imported module, with all its power. A second attribute step
  (synthtwin.paths.name.attr), or a step whose attribute names a
  module (synthtwin.paths.os), is rejected as before. When the
  sibling's source is not part of the scanned tree, importing a name
  that matches a known module name is rejected for the same reason.
* Name binding is flow-insensitive on purpose and keeps an EXPLICIT
  unknown member. A name bound to a module (or any traced origin)
  ANYWHERE in a scope keeps that origin for the whole scope, no
  matter what else is assigned to it, even on branches that can never
  run. A name bound to anything this audit cannot trace (a function
  parameter, a computed value) carries the unknown member, and other
  origins joining the set NEVER discard it: rebinding adds
  possibilities, it never clears suspicion. The ONE sanctioned
  narrowing is the isinstance type gate described under method calls
  below: a leading "if not isinstance(name, str): raise ..." runs
  before anything else in its function and stops it cold unless the
  parameter is a str instance, so that parameter alone starts as a
  checked-string origin instead of unknown. That narrowing raises
  confidence in what the value is; it does not settle that the value
  is a built-in str (see the gate note under method calls).
* TWO QUESTIONS, TWO VIEWS OF THE SAME BINDINGS. "Must this be
  checked?" and "may this be trusted?" are not the same question and
  are no longer answered from the same set.
  - MUST THIS BE CHECKED reads the walk's own view, which fills up as
    the statements of a scope are read in the order they are written.
    Origins accumulate there and are never discarded, so a name that
    might still hold a dangerous module is still reported. This view
    never reaches ahead of the walk, because reporting a statement
    against a store written below it would call honest code a
    violation.
  - MAY THIS BE TRUSTED reads a second view that does not model
    position at all. For every name it holds the union of EVERY
    binding that name receives anywhere in the scope -- above the use,
    below it, inside a branch, inside a loop, inside a comprehension,
    inside a body that runs later -- and that union is complete before
    the first statement of the scope is checked. Trust is granted only
    when every one of those origins is independently the allowed API;
    one binding anywhere in the scope that is not the allowed API
    withdraws trust everywhere in it, and a construct that still
    cannot be reasoned about is refused.
    WHY POSITION IS NOT MODELLED HERE. Textual position does not
    decide run-time order. A loop repeats, so the last line of its
    body governs every iteration after the first. A function, a
    lambda, and a generator expression defer, so a line below them is
    in force before they run. A module can be re-entered. Three
    repairs in a row tried to say where each binding takes effect, and
    each was defeated by the construct next door -- the third by a
    rebinding written lower in the same loop body. So the trust side
    stops reasoning about position and takes the whole scope instead.
    It is deliberately stricter than Python: source that would in fact
    be safe at run time is refused. That is the chosen direction. A
    refusal is a message to a contributor; a trust granted from half a
    scope is a hole nobody sees.
    HOW THE TWO ARE KEPT APART, which is the part the fourth repair
    got wrong. It kept both stacks reachable at once and returned the
    union of their two answers, reasoning that a union can only add
    possibilities and so can only withdraw trust. It cannot: a name
    the position-blind stack does not bind AT ALL is a name the walk's
    stack then answers for by itself, and that answer is drawn from
    what the walk had reached. So the two are no longer reachable at
    once. `_open_trust_view` puts the position-blind stack in force
    and hands the walk's stack to its caller as a local value; for the
    duration of a trust question there is no attribute on the checker
    that leads back to it. Every grant -- provenance, the fenced
    reader's argument, a method-call receiver, a callback slot, which
    callback slots a callee even has, a decorator that hands the
    definition back, whether a bare call name is a built-in at all,
    whether a callee is first-party, an attribute of a restricted
    library object -- is asked through `_trust_origins`,
    `_trust_lookup`, `_trust_resolve` or `_resolve_exclusively`, and
    each of those opens that view first.
    THE SAME RULE ONE MODULE OVER. A name imported from a sibling in
    the scanned tree is trusted on the strength of that sibling's
    source, so the sibling's own bindings of it are unioned in the
    same way: a top-level name the sibling binds more than once, or
    binds through a form whose value cannot be read, or hands to a
    decorator that does not give it back, is refused on the importing
    side rather than read from its first binding
    (see _module_bindings).
* WHEN a piece of code runs still decides which bindings the CHECKING
  view shows it, so the audit follows Python's own order in the four
  places where that order matters. THE RULE IS THE CLASS, NOT THE
  LIST: every form whose body runs later than the text that carries it
  is postponed, and every form with a scope of its own is read in that
  scope. None of this is load-bearing for trust any more -- it decides
  which messages are raised and where, not what may be believed.
  - A def, an async def, a lambda, and a GENERATOR EXPRESSION BIND or
    build something where they stand; their bodies run later, after
    the surrounding scope has finished -- a generator expression's
    body not until something draws from it, which can be much later
    still. Each body is therefore read only once its whole
    surrounding scope has been walked AND that scope's bindings have
    been completed (the step below), so a store written BELOW it is
    already in the origin set when the body is read. Reading a body
    where it stands read the scope half-built, and a `Path` rebound
    three lines lower kept the trusted import origin it had above.
    A list, set, or dict comprehension carrying an `async for` runs
    later too and is postponed on the same rule; without one it is
    evaluated on the spot and read on the spot.
  - A COMPREHENSION of any of the four forms has a SCOPE OF ITS OWN,
    and its iteration variables live only inside it. So `[Path(v) for
    Path in items]` calls whatever `items` yields, not the imported
    `Path`: every target name starts as the unknown member inside the
    comprehension and shadows the surrounding name there. The binding
    does not leak out either, so the surrounding scope keeps the name
    it had. The FIRST iterable is the one part evaluated where the
    comprehension stands, so it is read in the surrounding scope. The
    one binding that deliberately escapes is a walrus: Python stores
    `:=` in the function or module around the comprehension, and so
    does this audit. A target that is not a plain name (`for
    obj.field in items`) writes into an object that outlives the
    comprehension at a moment this audit cannot place, and is
    refused.
  - A class body RUNS while the class is being built, one statement
    after another, and an unqualified name in it falls straight back
    to the module when the class-level store has not run yet (or ran
    on a branch that was not taken). A name looked up directly in a
    class body therefore carries the class-level origins UNIONED with
    the outer ones, never the class-level ones alone. (Inside a method
    the class scope is skipped entirely: Python resolves an
    unqualified name there to the module, never to the enclosing
    class.)
  - A DECORATOR is handed the definition under it and the decorated
    NAME then holds whatever the decorator hands back. Only the few
    enumerated in _DEFINITION_PRESERVING_DECORATORS give the
    definition itself back; after any other decorator the name also
    carries the unknown member, so calls through it are rejected.
  - The remaining lazily evaluated forms Python has are REFUSED
    rather than read, because their scopes are not modelled here: a
    `type X = ...` alias statement, whose right-hand side is
    evaluated on first use, and a PEP 695 type-parameter list (`def
    name[T](...)`, `class Name[T]:`), whose names are bound in a
    lazy scope wrapped around the definition and would otherwise
    stand in for an import through the whole body without any store
    being recorded. Neither appears in synthtwin source.
* Every form that BINDS a name contributes an origin, and WHICH forms
  those are is taken from Python's grammar rather than from a list of
  the ones that came up before. A binding form this audit did not
  record is a binding the trust rules never see, which is how an
  incomplete origin set turns into misplaced trust -- and three
  successive rounds of review each found one more form left out of a
  hand-written list. So the tables _BINDING_IDENTIFIER_FIELDS and
  _NON_BINDING_IDENTIFIER_FIELDS below cover every place the ast
  module's own node signatures put an identifier, split into the ones
  that bind a name and the ones that name an attribute, a module, or a
  parameter at a call site; each binding form says whether it is
  recorded or refused, and a test walks the running interpreter's ast
  module and fails on any identifier field missing from both tables.
  That covers the forms whose name is a plain string field rather than
  a Name node -- `except E as name`, `case name:`, `case [*name]`,
  `case {**name}` -- along with every Name in a store or delete
  context.
* WHEN those bindings enter each view is a rule of its own, and it is
  one step of the scope walker rather than something each form has to
  remember.
  - The TRUST view of a scope is built ON ENTRY, from the grammar
    above, before a single statement of that scope has been checked.
    It is built repeatedly until it stops growing, because a store
    reads the names around it and some of those are stored further
    down; origins accumulate, so repeating a pass can only add
    possibilities. A scope whose set has not settled by the last pass
    is refused outright rather than read.
  - The CHECKING view fills as the walk goes. The statements of a
    scope are checked first, in the order they are written, because
    that is the order they run in: a store two lines lower has not
    happened yet, and reporting an honest statement against it would
    be a defect of its own. That view's bindings are then COMPLETED
    from the grammar above, and only after that is any postponed body
    read -- a postponed body runs after the whole scope has finished,
    so it must see every name that scope binds. Leaving each form to
    record its store as the walk reached it was not enough: `:=`
    inside a generator expression binds in the scope AROUND it, but
    nothing in a generator expression runs until something draws from
    it, so that store was recorded only while the postponed body
    carrying it was itself being read -- after the function beside it
    had already been read against the name it rebinds.
* A call through a bare name is accepted only when EVERY possible
  origin of the name is a function or class defined in the scanned
  tree, an import traced to the allowlist, or one of a small fixed
  list of built-in constructors and helpers (str, len, print, ...).
  If any possible origin is unknown -- above all a function parameter
  used as a call target, even one that is rebound to an allowed API
  on some branch -- the call is rejected, because this audit cannot
  see what would run. Higher-order callback parameters are therefore
  banned in synthtwin source for Phase 0.
* Method calls (value.method(...)) are accepted in exactly two
  enumerated cases; every other method call target is rejected.
  There are NO method calls on untraced values.
  (a) On a value this audit reads as text. Three readings are
      accepted: the value is a literal constant (or a name bound only
      to literal constants); the value is a parameter whose function
      opens with the exact type gate
      "if not isinstance(name, str): raise ..." (or the equivalent
      positive branch "if isinstance(name, str): ... else:
      raise ...") before any other statement; or the value was
      PRODUCED under this audit's eyes from one of those (Phase 1
      extension E4): the result of an enumerated text-returning
      method called on an accepted text receiver, a slice or index
      of an accepted text value, the result of str(), repr(), or
      format(), or an f-string every one of whose interpolated
      values this audit already resolved -- INCLUDING the format
      specification after each colon, which is an expression in its
      own right: in f"{'x':{spec}}" the text that comes out is built
      from spec just as surely as from the value before the colon.
      Text
      spreads only from those origins; an untraced value never
      becomes text, so nothing is laundered into the accepted set.
      Methods whose result is NOT text (split returns a list, find
      returns a number, startswith returns a truth value) leave the
      result untraced, so no method call is accepted on it.
      WHAT THE GATE DOES, AND WHAT IT DOES NOT DO. The gate raises
      confidence that the value is a string, and that is what lets
      this scanner accept the enumerated string-method calls on it
      (the exact set the src tree calls, listed in _STR_METHODS
      below). The gate does NOT settle that the receiver is a
      built-in str: a str subclass passes isinstance and may
      override any of them, so the method body that runs can be
      the subclass's own -- and under E4 its return value is then
      treated as text as well. Such a call target is RESOLVED UNDER
      THE ENUMERATED POLICY, not shown to be exact. This is the
      best-effort scope ratified as D6 Amendment A3, and its
      residual is caller-supplied code, named at the top of this
      docstring; E4 carries that accepted reading one step
      further without widening the class of thing that can happen,
      because the only operations this policy permits on a text
      value are another enumerated data method or use as data.
      Any method name outside that enumeration, and any
      method call on a value with neither reading -- a bare
      parameter, a computed value, the result of a scanned call --
      is a violation. parameter.find() WITHOUT the gate is rejected,
      because at run time it would run whatever find method the
      caller's object defines, with no reading of it at all.
      EVERY argument of an accepted str-method call must still be a
      plain literal or a value this audit fully resolved as safe (an
      allowlisted API's result, a scanned function's result, a name
      bound only to literals, a gate-checked string): str.format
      invokes the formatting protocol of what it is handed, so
      unknowns and callables are rejected. The gate depends on the
      built-in names isinstance and str, so BINDING any accepted
      built-in call name to anything, anywhere in scanned source, is
      itself a violation -- a rebound built-in could make a checked
      call or a type gate mean something else.
  (b) A value returned by a call to an allowlisted API
      (parser = argparse.ArgumentParser(...)) is tracked as an
      api-instance, and method calls on it
      (parser.add_argument(...)) are accepted: the API that produced
      the value was itself checked against the allowlist. A value
      built by an operator expression with an api-instance operand
      (pathlib.Path(...) / name) is tracked the same way. The
      callable-accepting api-instance methods are enumerated in the
      slot table below (pathlib.Path.walk's on_error above all).
* A function or lambda passed as a call argument to any callee not
  defined in the scanned tree is rejected: outside code could keep
  the callable and run it at any time, in ways this audit cannot
  see. Handing a callable to a function defined in the scanned tree
  is fine, because every call site inside that function is scanned
  under the same rules. Targets put together while the program runs
  (double-underscore internals, lookups through the module table,
  subscripted call targets, star imports) are rejected as before.
* Callback SLOTS are checked by argument position. The allowlisted
  world is closed, so every allowed external API that can INVOKE one
  of its arguments is enumerated in this file with its exact
  callable-accepting slots (the full audit is below). A value placed
  in one of those slots must be a plain literal, a directly named
  accepted built-in (str, int, ...), or a directly named allowlisted
  API. Anything else -- above all a caller-supplied parameter, a
  computed value, or a first-party function or lambda -- is
  rejected, because the API would invoke it outside anything this
  audit can see. Data arguments outside these slots
  (json.loads(raw), parser.parse_args(argv)) stay accepted. Star and
  double-star expansion into an API that has callback slots is
  rejected too, because expansion hides which value lands in which
  slot.

Complete audit of the closed allowed surface. Every enumerated name
below was checked against its documented signature on every supported
interpreter (CPython 3.10 through 3.14); "data" means the API never
invokes that name's arguments. This list IS the audit record -- an
attribute absent from it is not allowed at all:

* argparse: ArgumentParser (formatter_class SLOT) and
  RawDescriptionHelpFormatter, which is the class named in that
  slot: argparse instantiates it and calls its formatting methods
  to lay out help text. Audited: it formats strings and performs
  no I/O, starts no process, and invokes nothing it is handed.
  ArgumentParser's api-instance
  methods: add_argument (action SLOT, type SLOT); add_subparsers
  (action SLOT, parser_class SLOT); register (object SLOT);
  parse_args, parse_known_args, set_defaults, add_argument_group,
  add_mutually_exclusive_group, print_help, format_help, error, and
  exit take data only (set_defaults stores values, it never calls
  them).
* dataclasses: dataclass decorates the scanned class under it -- no
  foreign callable slot; field (default_factory SLOT); asdict
  (dict_factory SLOT); astuple (tuple_factory SLOT); make_dataclass
  (bases SLOT, namespace SLOT, and decorator SLOT -- the decorator
  parameter is new in Python 3.14 and is called to build the class);
  fields, is_dataclass, replace, MISSING: data.
* json: load and loads (cls, object_hook, object_pairs_hook,
  parse_constant, parse_float, parse_int SLOTS); dump and dumps
  (cls, default SLOTS); JSONDecoder (the five hook SLOTS);
  JSONEncoder (default SLOT); JSONDecodeError: data (an exception
  type).
* pathlib: Path (constructor: data). The Path instance methods the
  src tree uses -- resolve, is_absolute, the / operator, and the
  parts attribute -- are data. Across 3.10-3.14 the ONLY Path
  instance method with a callable parameter is walk (on_error SLOT,
  added in 3.12); every other instance method (open, read_text,
  write_text, glob, rglob, iterdir, stat, lstat, mkdir, match,
  relative_to, ...) takes data only, so pathlib.Path.walk carries
  the one instance-method slot entry.
* typing: Protocol (a base class: data) and cast (returns its second
  argument unchanged: data). Nothing else -- see the typing note
  above.
* sys: platform, argv, exit, stdout, stderr, executable, and
  version_info: data. Nothing else is allowed; the slot table keeps
  entries for settrace, setprofile, addaudithook, set_asyncgen_hooks,
  and call_tracing as a second layer even though the attribute
  enumeration already rejects them.
* os: fspath, getcwd, lstat, and read-only os.environ: data. Every
  enumerated os.path helper (join, exists, isfile, dirname, ...) is
  a pure path-text or single-metadata function: data.
* importlib.metadata: version: data.
* csv (Phase 1 extension E3): reader (dialect SLOT -- a dialect class
  is instantiated by the library; every other parameter is a plain
  text or truth-value dialect setting); field_size_limit (reads and
  writes one integer of module state, used to raise and then restore
  the per-field cap); Error (an exception type). None of the three
  performs I/O of its own: reader consumes an iterable of text lines
  that the caller has already opened, and yields lists of text.
* math (Phase 1 extension E2, revised at round 1): fsum, frexp,
  isfinite, ldexp, sqrt. Every one is a pure numeric function of
  numbers; none takes a callable, none performs I/O, and each is a
  correctly rounded IEEE-754 operation or an exact power-of-two
  manipulation. This enumeration replaced the numpy one: round 1 of the
  Phase 1 review showed that numpy's reductions made the published
  statistics depend on row order and on magnitude, so the profiler now
  computes them itself under the rules in taxonomy.py's docstring, and
  imports numpy nowhere. Nothing else from math is allowed -- prod and
  sumprod are reductions with their own ordering behaviour, and the
  trigonometric and special functions are not correctly rounded.
* pandas (Phase 1 extension E1): read_csv, and nothing else. Capability
  audit: read_csv opens its first argument, which may be a path, an
  open file, or a URL, so it IS network-capable. synthtwin never hands
  it a URL: every path reaching it has passed validate_local_path,
  which rejects URL schemes lexically before any filesystem call, and
  it is handed the resulting Path object rather than user text (plan
  phase-1-profiler.md, P1-D2.1 -- a fencing arrangement, not an
  inability, stated in exactly those terms in SECURITY.md). Its
  callable-accepting parameters are enumerated as SLOTS (converters,
  dtype, date_format, date_parser, on_bad_lines, skiprows, usecols,
  dialect, engine, storage_options), so no caller-supplied or computed
  callable can reach the library. Every parameter after the first is
  keyword-only in the supported pandas versions, so no positional slot
  can exist. Values returned by read_csv are api-instances under
  policy case (b).
* Accepted built-ins: sorted, min, and max (key SLOT); map and
  filter (the function argument SLOT); the two-argument form of iter
  (the callable argument SLOT); print (file SLOT -- print invokes
  the write method of whatever object sits there); every other
  accepted built-in takes data (numbers, text, iterables) and never
  invokes an argument it is handed.

Adding a name to any enumeration above is a policy decision reviewed
against the threat model, not a routine code change.

Exit status: 0 clean; 1 one or more violations, each printed as
"file:line: explanation"; 2 the command line itself was wrong.

This tool uses only the Python standard library (ast, pathlib, sys,
argparse) and never imports or runs the code it checks.
"""

import argparse
import ast
import pathlib
import sys

_FIRST_PARTY_ROOT = "synthtwin"

# Every allowed module's usable attribute names, enumerated one by
# one: membership in an allowed module proves nothing about what an
# attribute can do, so there is no module-level trust anywhere. An
# attribute outside its module's enumeration is a violation. The
# module docstring carries the per-name audit (which of these accept
# callables, and where their slots are). Adding a name is a policy
# decision reviewed against the threat model, not a routine code
# change. (os and importlib.metadata are enumerated separately in
# _policy_for because their messages are more specific.)
_ALLOWED_MODULE_ATTRS: "dict[str, frozenset[str]]" = {
    "argparse": frozenset({"ArgumentParser", "RawDescriptionHelpFormatter"}),
    "csv": frozenset({"Error", "field_size_limit", "reader"}),
    "dataclasses": frozenset(
        {
            "MISSING",
            "asdict",
            "astuple",
            "dataclass",
            "field",
            "fields",
            "is_dataclass",
            "make_dataclass",
            "replace",
        }
    ),
    "json": frozenset(
        {
            "JSONDecodeError",
            "JSONDecoder",
            "JSONEncoder",
            "dump",
            "dumps",
            "load",
            "loads",
        }
    ),
    "os.path": frozenset(
        {
            "abspath",
            "altsep",
            "basename",
            "commonpath",
            "commonprefix",
            "curdir",
            "dirname",
            "exists",
            "expanduser",
            "expandvars",
            "getatime",
            "getctime",
            "getmtime",
            "getsize",
            "isabs",
            "isdir",
            "isfile",
            "isjunction",
            "islink",
            "ismount",
            "join",
            "lexists",
            "normcase",
            "normpath",
            "pardir",
            "realpath",
            "relpath",
            "samefile",
            "sep",
            "split",
            "splitdrive",
            "splitext",
            "splitroot",
        }
    ),
    "math": frozenset(
        {"fsum", "frexp", "isfinite", "ldexp", "sqrt"}
    ),
    "pandas": frozenset({"read_csv"}),
    "pathlib": frozenset({"Path"}),
    "sys": frozenset(
        {
            "argv",
            "executable",
            "exit",
            "platform",
            "stderr",
            "stdout",
            "version_info",
        }
    ),
    "typing": frozenset({"Protocol", "cast"}),
}

# typing names that evaluate annotation text as code (a string
# annotation is compiled and run to produce the object it names).
# They are outside the enumeration above anyway; naming them here lets
# the violation message say exactly why they are dangerous.
_TYPING_EVALUATORS = frozenset(
    {"ForwardRef", "evaluate_forward_ref", "get_type_hints"}
)

# Dotted paths that name a module object (as opposed to a function or
# class). Bare references to these outside an import statement or a
# direct dotted access are rejected. Per-file scanning extends this set
# with intra-package module paths seen in import statements.
_KNOWN_MODULE_PATHS = frozenset(_ALLOWED_MODULE_ATTRS) | {
    "sys",
    "os",
    "os.path",
    "importlib",
    "importlib.metadata",
}

_REFLECTION_PRIMITIVES = {
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
    "vars",
    "globals",
    "locals",
    "dir",
}

_DYNAMIC_CODE_PRIMITIVES = {"exec", "eval", "compile", "__import__"}

_BANNED_BUILTINS = _REFLECTION_PRIMITIVES | _DYNAMIC_CODE_PRIMITIVES

_FORBIDDEN_MODULES = {
    "subprocess": "start other programs on this computer",
    "ctypes": "run native machine code",
    "cffi": "run native machine code",
    "multiprocessing": "launch new processes",
}

# Attribute names that are banned wherever they appear, because they
# name dynamic loaders reachable through otherwise-allowed objects.
_ENTRY_POINT_TOKENS = {"EntryPoint", "entry_points"}

_ALLOWED_DUNDER_NAMES = {"__name__", "__doc__", "__file__", "__version__", "__all__"}

_ENV_READ_METHODS = {"get", "keys", "items", "values", "copy"}

# The explicit unknown member of the origin lattice. A name carrying
# this member may hold ANYTHING at run time; other origins joining the
# same set never discard it.
_UNKNOWN = ("unknown", "")

# How many times the position-blind view of one scope is recomputed
# before it is required to have settled. Each pass records every
# binding the scope makes and origins only accumulate, so the passes
# are monotone: one pass fills the set, the next confirms it, and a
# chain of local names handing a value along (a = f(x); b = a; c = b)
# needs one pass per link. A scope that has not settled by the last
# pass is REFUSED rather than read -- see _complete_trust_bindings.
_TRUST_PASSES = 8

# The only method names that may be called on a value this audit reads
# as text (policy case (a) in the module docstring): a literal
# constant, a parameter behind the exact isinstance type gate, or a
# value produced from one of those under extension E4. The gate does
# not settle that the receiver is a built-in str, so a str subclass
# could still supply its own version of any of these. That is the
# best-effort scope ratified as D6 Amendment A3 (module docstring),
# whose residual is caller-supplied code.
#
# Every name below was audited as a pure text transform: it performs no
# I/O, starts no process, loads no code, and invokes nothing it is
# handed except the formatting protocol of an argument (format, and
# the iteration protocol for join), which the safe-argument rule in
# _check_method_call already governs. This is exactly the set of str
# data methods the current src tree calls; adding a name here is a
# policy decision reviewed against the threat model, not a routine
# code change.
#
# The split matters: only a method whose result is itself text keeps
# the text origin (extension E4). split returns a list, find returns a
# number, startswith returns a truth value -- their results are
# untraced, so no further method call is accepted on them.
_TEXT_RESULT_STR_METHODS = {
    "casefold",
    "format",
    "join",
    "lower",
    "lstrip",
    "removeprefix",
    "removesuffix",
    "replace",
    "rstrip",
    "strip",
    "upper",
    "zfill",
}

_OTHER_RESULT_STR_METHODS = {
    "count",
    "endswith",
    "find",
    "isascii",
    "isdigit",
    "split",
    "startswith",
}

_STR_METHODS = _TEXT_RESULT_STR_METHODS | _OTHER_RESULT_STR_METHODS

# Built-in calls whose result is text by construction (extension E4).
# Each is already an accepted call target; this set records that the
# VALUE they return may be read as text. A shadowed name is excluded at
# the call site (and shadowing an accepted built-in is a violation in
# its own right).
_TEXT_PRODUCING_BUILTINS = {"format", "repr", "str"}

# Libraries whose api-instances may NOT be called through at all
# (Phase 1 extension E5), with the exact method names that are
# nonetheless permitted on them -- currently none for either.
#
# Policy case (b) accepts any method name on a value an allowlisted API
# produced, because the API that produced it was itself checked. For
# the standard-library surfaces of Phase 0 that reasoning holds and the
# module docstring carries their per-name audit. It does NOT hold for
# these two: a pandas frame carries writers that reach the network of
# their own accord (to_sql, to_gbq, and the URL-accepting to_* family),
# and a numpy array carries tofile and dump. Accepting arbitrary method
# names on their results would silently reopen everything the E1 and E2
# enumerations close.
#
# synthtwin's source calls no method on a pandas or numpy object: it
# reads attributes, subscripts, and operators, and hands the values
# back to the enumerated module-level functions. The empty sets below
# say exactly that, and adding a name to one of them is a policy
# decision reviewed against the threat model, not a routine code
# change.
_RESTRICTED_INSTANCE_METHODS: "dict[str, frozenset[str]]" = {
    "pandas": frozenset(),
}

# Attributes that may be READ on a value one of those libraries
# produced. Round 1 of the Phase 1 review showed that banning method
# calls is not enough: `frame.style` reaches a whole unenumerated
# capability without a call in sight, and any attribute could. Only the
# names the profiler actually reads are listed.
_RESTRICTED_INSTANCE_ATTRIBUTES: "dict[str, frozenset[str]]" = {
    "pandas": frozenset({"columns"}),
}

# APIs that open whatever they are handed, including a URL. Each may
# appear ONLY as the direct target of a call -- never stored, passed, or
# placed in a callback slot -- and the value it is handed must be
# traceable, inside the same function, to validate_local_path. This is
# the enforcement behind the fence P1-D2.1 describes; round 1 found the
# claim resting on nothing but the order the current source happens to
# be written in.
_FENCED_APIS = frozenset({"pandas.read_csv"})

_LOCAL_PATH_VALIDATOR = "synthtwin.paths.validate_local_path"

# The origin recording "this value came from validate_local_path".
_LOCALPATH = ("localpath", "")

# Origin kinds accepted as ARGUMENTS of an enumerated str-method call
# (policy case (a)): a value built by an allowlisted API, a value
# returned by a scanned def or class, a name bound only to literals,
# or a gate-checked string. Everything else -- the unknown member above
# all -- is rejected, because str.format invokes the formatting
# protocol of what it is handed.
_SAFE_DATA_ARGUMENT_KINDS = {"instance", "literal", "localpath", "result", "str"}

# The only decorators after which the decorated name still holds the
# definition written under it. A decorator REBINDS that name to
# whatever it returns, so "@something" above a def or a class is a
# store like any other, and a name this audit read as a scanned
# definition could hold anything at all (review item P1-R6-F4).
# dataclasses.dataclass hands back the very class it was given;
# staticmethod, classmethod and property return the built-in wrapper
# around the scanned function, which adds no call target this audit
# cannot already see. Every other decorator leaves the decorated name
# carrying the unknown member, so calls through it are rejected.
# Adding a name here is a policy decision reviewed against the threat
# model, not a routine code change.
_DEFINITION_PRESERVING_DECORATORS = {
    "classmethod",
    "dataclasses.dataclass",
    "property",
    "staticmethod",
}

# Every allowed external API that can INVOKE one of its arguments,
# mapped to its exact callable-accepting slots: a frozenset of keyword
# names plus a dict of positional index -> slot name (positions are
# counted at the call site, so an instance method's self never
# counts). The allowlisted world is closed and the module docstring
# carries the complete per-name audit behind this table; adding an
# entry is a policy decision reviewed against the threat model, not a
# routine code change. The "iter" entry applies only to the
# two-argument form (handled at the call site); one-arg iter takes
# plain data. The sys entries (settrace, setprofile, addaudithook,
# set_asyncgen_hooks, call_tracing) are a second layer: the sys
# attribute enumeration already rejects every one of them.
_CALLBACK_SLOTS: "dict[str, tuple[frozenset[str], dict[int, str]]]" = {
    "argparse.ArgumentParser": (
        frozenset({"formatter_class"}),
        {5: "formatter_class"},
    ),
    "argparse.ArgumentParser.add_argument": (
        frozenset({"action", "type"}),
        {},
    ),
    "argparse.ArgumentParser.add_subparsers": (
        frozenset({"action", "parser_class"}),
        {},
    ),
    "argparse.ArgumentParser.register": (frozenset({"object"}), {2: "object"}),
    "csv.reader": (frozenset({"dialect"}), {1: "dialect"}),
    "dataclasses.asdict": (frozenset({"dict_factory"}), {}),
    "dataclasses.astuple": (frozenset({"tuple_factory"}), {}),
    "dataclasses.field": (frozenset({"default_factory"}), {}),
    "dataclasses.make_dataclass": (
        frozenset({"bases", "decorator", "namespace"}),
        {},
    ),
    "filter": (frozenset(), {0: "function"}),
    "iter": (frozenset(), {0: "function"}),
    "json.JSONDecoder": (
        frozenset(
            {
                "object_hook",
                "object_pairs_hook",
                "parse_constant",
                "parse_float",
                "parse_int",
            }
        ),
        {},
    ),
    "json.JSONEncoder": (frozenset({"default"}), {}),
    "json.dump": (frozenset({"cls", "default"}), {}),
    "json.dumps": (frozenset({"cls", "default"}), {}),
    "json.load": (
        frozenset(
            {
                "cls",
                "object_hook",
                "object_pairs_hook",
                "parse_constant",
                "parse_float",
                "parse_int",
            }
        ),
        {},
    ),
    "json.loads": (
        frozenset(
            {
                "cls",
                "object_hook",
                "object_pairs_hook",
                "parse_constant",
                "parse_float",
                "parse_int",
            }
        ),
        {},
    ),
    "map": (frozenset(), {0: "function"}),
    "max": (frozenset({"key"}), {}),
    "min": (frozenset({"key"}), {}),
    "pandas.read_csv": (
        frozenset(
            {
                "converters",
                "date_format",
                "date_parser",
                "dialect",
                "dtype",
                "engine",
                "on_bad_lines",
                "skiprows",
                "storage_options",
                "usecols",
            }
        ),
        {},
    ),
    "pathlib.Path.walk": (frozenset({"on_error"}), {1: "on_error"}),
    "print": (frozenset({"file"}), {}),
    "sorted": (frozenset({"key"}), {}),
    "sys.addaudithook": (frozenset(), {0: "hook"}),
    "sys.call_tracing": (frozenset(), {0: "function"}),
    "sys.set_asyncgen_hooks": (
        frozenset({"finalizer", "firstiter"}),
        {0: "firstiter", 1: "finalizer"},
    ),
    "sys.setprofile": (frozenset(), {0: "function"}),
    "sys.settrace": (frozenset(), {0: "function"}),
}

# sys.modules and sys.path per the plan; the other three are the rest of
# the interpreter's import machinery reachable through sys.
_SYS_BANNED = (
    "sys.modules",
    "sys.path",
    "sys.meta_path",
    "sys.path_hooks",
    "sys.path_importer_cache",
)

_OS_ALLOWED_EXACT = {"os.fspath", "os.getcwd", "os.lstat"}

# Attribute names that are known to name modules when reached through
# another module's namespace (allowed modules re-export several of
# these: os.path holds os and sys, pathlib holds os, json holds its
# decoder/encoder/scanner submodules, and so on). Reaching one module
# through another module's attribute is never allowed, from any root,
# including the package's own modules (synthtwin.paths.os is how
# synthtwin.paths sees its own import of os).
_MODULE_ATTR_BLOCK = {
    "abc",
    "argparse",
    "cffi",
    "codecs",
    "collections",
    "contextlib",
    "copy",
    "copyreg",
    "csv",
    "ctypes",
    "dataclasses",
    "decoder",
    "email",
    "encoder",
    "enum",
    "errno",
    "fnmatch",
    "functools",
    "genericpath",
    "glob",
    "importlib",
    "inspect",
    "io",
    "itertools",
    "json",
    "keyword",
    "math",
    "multiprocessing",
    "nt",
    "ntpath",
    "numpy",
    "operator",
    "os",
    "pandas",
    "path",
    "pathlib",
    "pickle",
    "posix",
    "posixpath",
    "random",
    "re",
    "reprlib",
    "scanner",
    "shutil",
    "socket",
    "stat",
    "string",
    "struct",
    "subprocess",
    "sys",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "types",
    "typing",
    "unicodedata",
    "warnings",
    "zipfile",
}

# Bare-name call targets that are accepted without a traced origin:
# built-in constructors, plain data helpers, and the exception types
# product code may raise. Nothing on this list can start a program,
# open a connection, load code, or reach an attribute by computed name.
_ALLOWED_CALL_BUILTINS = {
    "abs",
    "all",
    "any",
    "bool",
    "bytearray",
    "bytes",
    "chr",
    "dict",
    "divmod",
    "enumerate",
    "filter",
    "float",
    "format",
    "frozenset",
    "hash",
    "hex",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "min",
    "next",
    "oct",
    "ord",
    "print",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "slice",
    "sorted",
    "str",
    "sum",
    "tuple",
    "zip",
    "Exception",
    "FileNotFoundError",
    "IndexError",
    "KeyError",
    "NotImplementedError",
    "OSError",
    "PermissionError",
    "RuntimeError",
    "StopIteration",
    "TypeError",
    "ValueError",
}

_ALLOWLIST_NOTE = (
    "The Phase 0 allowlist (plan D6.2) permits only: argparse, "
    "dataclasses, json, pathlib, typing, sys (never sys.modules or "
    "sys.path), os.path plus os.fspath, os.getcwd, os.lstat and "
    "read-only os.environ, and importlib.metadata.version() -- and "
    "within each module only the attribute names enumerated in this "
    "scanner. Adding anything is a plan-level decision, not a code "
    "change."
)


def _is_dunder(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _parameters_of(args: ast.arguments) -> "list[ast.arg]":
    """Every parameter a def or lambda declares, in one list."""
    named = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    if args.vararg is not None:
        named.append(args.vararg)
    if args.kwarg is not None:
        named.append(args.kwarg)
    return named


def _chain_parts(node: ast.AST) -> "list[str] | None":
    """Return ["root", "attr", ...] for a pure Name/Attribute chain.

    Returns None when the expression is anything else (a call result, a
    subscript result, a literal, ...).
    """
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        parts.reverse()
        return parts
    return None


def _first_party_module_name(path: pathlib.Path) -> "str | None":
    """Dotted first-party module name for ``path``, or None.

    A file is first-party when a folder named exactly like the
    first-party root sits on its path. The LAST such folder is taken as
    the package root, because an outer folder (for example the
    repository folder itself) may carry the same name.
    """
    parts = path.parts
    root_index = None
    for index in range(len(parts) - 1):
        if parts[index] == _FIRST_PARTY_ROOT:
            root_index = index
    if root_index is None:
        return None
    stem = parts[-1].removesuffix(".py")
    pieces = list(parts[root_index:-1])
    if stem != "__init__":
        pieces.append(stem)
    return ".".join(pieces)


def _decorator_dotted(decorator: ast.AST) -> "str | None":
    """The dotted text of a decorator, or None when it is not written
    as a plain name or a pure dotted chain."""
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    parts = _chain_parts(target)
    return ".".join(parts) if parts else None


def _module_bindings(
    tree: ast.Module,
) -> "tuple[set[str], set[str], set[str]]":
    """Split one module's top-level names into (defined, imported,
    unsettled).

    ``defined`` holds the names the module genuinely defines: def,
    class, and plain assignments to a bare name, anywhere at module
    level (including inside if/try blocks, which still bind module
    names). ``imported`` holds every name the module itself imported.
    A name in both sets counts as imported, because the source text
    alone cannot prove the assignment replaced the imported object.
    Nested function, class, and lambda bodies bind nothing at module
    level and are not entered.

    ``unsettled`` is the SAME position-blind rule applied one module
    over (review item P1-R6-F4). A sibling's exported name is trusted
    by the module that imports it, and that trust rests on the sibling
    binding the name ONCE, by a definition or a plain assignment. A
    sibling that binds it a second time anywhere at module level, or
    binds it through a form whose value this audit cannot read (a loop
    variable, a `with ... as`, an `except ... as`, a match capture, a
    walrus, an unpacking, an augmented assignment, a `del`), or hands
    the definition to a decorator that does not give it back, exports
    something the importing module cannot be told. Every such name is
    listed here, and the importing side withdraws trust from it rather
    than reading the first binding and stopping. Without this, a
    sibling could define `validate_local_path` and rebind it on its
    last line, and the module that imported it went on treating what
    the rebinding returns as a validated local path.
    """
    defined: set[str] = set()
    imported: set[str] = set()
    counts: dict[str, int] = {}
    shaky: set[str] = set()
    decorated: list[tuple[str, list[ast.expr]]] = []

    def note(name: str) -> None:
        counts[name] = counts.get(name, 0) + 1

    stack: list[ast.AST] = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
            note(node.name)
            if node.decorator_list:
                decorated.append((node.name, list(node.decorator_list)))
        elif isinstance(node, ast.Lambda):
            continue
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.partition(".")[0]
                imported.add(name)
                note(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    name = alias.asname or alias.name
                    imported.add(name)
                    note(name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
                    note(target.id)
                else:
                    stack.append(target)
            stack.append(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value is not None:
                defined.add(node.target.id)
                note(node.target.id)
            elif not isinstance(node.target, ast.Name):
                stack.append(node.target)
            if node.value is not None:
                stack.append(node.value)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                # A store this walk reached through some other
                # statement: a loop variable, an unpacking, an
                # augmented assignment, a `del`.
                shaky.add(node.id)
                note(node.id)
        elif isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)):
            if node.name is not None:
                shaky.add(node.name)
                note(node.name)
            stack.extend(ast.iter_child_nodes(node))
        elif isinstance(node, ast.MatchMapping):
            if node.rest is not None:
                shaky.add(node.rest)
                note(node.rest)
            stack.extend(ast.iter_child_nodes(node))
        elif isinstance(node, ast.NamedExpr):
            if isinstance(node.target, ast.Name):
                shaky.add(node.target.id)
                note(node.target.id)
            stack.append(node.value)
        else:
            stack.extend(ast.iter_child_nodes(node))

    unsettled = shaky | {name for name, count in counts.items() if count > 1}
    for name, decorators in decorated:
        for decorator in decorators:
            dotted = _decorator_dotted(decorator)
            if dotted not in _DEFINITION_PRESERVING_DECORATORS:
                unsettled.add(name)
                continue
            # The decorator is one of the enumerated few, PROVIDED the
            # name it is written under still means what it reads as in
            # this module.
            root = dotted.partition(".")[0]
            if "." in dotted:
                if root in unsettled or root not in imported:
                    unsettled.add(name)
            elif root in defined or root in imported or root in shaky:
                unsettled.add(name)
    return defined - imported, imported, unsettled


def _primitive_message(name: str) -> str:
    if name in _REFLECTION_PRIMITIVES:
        return (
            "uses the reflection primitive '" + name + "', which can "
            "reach any function or attribute through a name computed "
            "while the program runs. That defeats this offline audit; "
            "call what you need by its direct, written-out name instead."
        )
    return (
        "uses '" + name + "', which can turn text into running code. "
        "That defeats this offline audit and is never allowed in "
        "synthtwin source."
    )


def _forbidden_module_message(name: str, how_used: str) -> str:
    return (
        how_used + " '" + name + "', which can "
        + _FORBIDDEN_MODULES[name]
        + ". synthtwin promises never to do that; remove it."
    )


def _bare_module_message(dotted: str) -> str:
    return (
        "refers to the module '" + dotted + "' as a bare value. Module "
        "objects passed through variables or containers can hide what "
        "gets called later; write the full dotted access (for example "
        "os.path.join) instead."
    )


def _module_hop_message(dotted: str, part: str) -> str:
    return (
        "uses '" + dotted + "': the attribute '" + part + "' names a "
        "module reached through another module's namespace. This audit "
        "accepts only APIs named directly on an allowlisted module, "
        "never a module re-exported by another module; import what you "
        "need directly from the allowlist instead."
    )


def _private_hop_message(dotted: str, part: str) -> str:
    return (
        "uses '" + dotted + "': the attribute '" + part + "' starts "
        "with an underscore. Underscore names are a module's internal "
        "machinery and often alias other modules; they are not part of "
        "any allowlisted API."
    )


def _deep_chain_message(dotted: str, prefix: str) -> str:
    return (
        "uses '" + dotted + "', which steps more than one attribute "
        "past the module '" + prefix + "'. Reading the source can "
        "verify only a single, directly named attribute of a module; "
        "anything deeper can reach objects this audit never cleared. "
        "Name the API you need in one step."
    )


def _unknown_call_message(name: str) -> str:
    return (
        "calls '" + name + "', but on at least one path '" + name + "' "
        "may hold a value this audit cannot trace to any function or "
        "class defined in the scanned code, to an allowlisted import, "
        "or to the fixed list of accepted built-ins. A function passed "
        "around as a value (a callback) cannot be checked by reading "
        "the source, and a possibility once recorded is never "
        "discarded, so Phase 0 synthtwin source must call every "
        "function by its written-out name."
    )


def _unknown_method_message(method: str) -> str:
    return (
        "calls the method '" + method + "' on a value this audit "
        "cannot trace to any allowlisted API and cannot read as a "
        "string. A caller-supplied object may define a method of any "
        "name to do anything, so no method call on an untraced value "
        "is accepted. Build the value from an allowlisted API, or "
        "check that the value is a string first with the exact type "
        "gate 'if not isinstance(name, str): raise ...' at the top of "
        "the function."
    )


def _fenced_reference_message(dotted: str) -> str:
    return (
        "names '" + dotted + "' somewhere other than directly as the "
        "function of a call. This API opens whatever it is handed, a "
        "local file or a URL alike, so it may never be stored in a "
        "variable, handed to another function, or placed in a callback "
        "slot: written that way, this audit cannot see what it would "
        "open. Call it by its full name at the point of use."
    )


def _fenced_argument_message(dotted: str) -> str:
    return (
        "hands '" + dotted + "' a first argument this audit cannot "
        "trace to validate_local_path. This API opens whatever it is "
        "handed, and a path-shaped object is not enough -- "
        "pathlib.Path('https://host/f.csv') still enters the library's "
        "URL branch, because the library turns it back into text before "
        "it decides. The argument must be a plain name bound in this "
        "same function to pathlib.Path(v), where v is the result of "
        "validate_local_path."
    )


def _restricted_attribute_message(name: str, library: str) -> str:
    allowed = sorted(_RESTRICTED_INSTANCE_ATTRIBUTES[library])
    listed = ", ".join(allowed) if allowed else "none at all"
    return (
        "reads the attribute '" + name + "' of a value produced by "
        + library + ". Attributes of these objects reach capability "
        "without a call in sight, so only the enumerated ones may be "
        "read: " + listed + "."
    )


def _scope_escape_message(keyword: str) -> str:
    return (
        "uses '" + keyword + "'. It rebinds a name that belongs to "
        "another scope, which lets a value change identity between the "
        "place this audit reads it and the place it is used. synthtwin "
        "source passes values as arguments and returns them instead."
    )


def _type_parameter_message() -> str:
    return (
        "declares type parameters in square brackets ('def name[T](...)' "
        "or 'class Name[T]:'). Those names live in a scope of their own "
        "that Python evaluates lazily, and this audit does not read that "
        "scope, so a name written there could quietly stand in for an "
        "import for the whole body. Phase 0 synthtwin source writes "
        "plain definitions without them."
    )


def _type_alias_message() -> str:
    return (
        "uses a 'type' alias statement. What is written after the '=' is "
        "not evaluated there: Python keeps it and evaluates it later, on "
        "first use, in a scope of its own. What its names refer to at "
        "that moment cannot be read from this line, so this audit "
        "refuses the form rather than guess. Write the alias with a "
        "plain '=' instead."
    )


def _comprehension_target_message() -> str:
    return (
        "writes a comprehension's loop variable into an attribute or a "
        "subscript ('for obj.field in items'). That store lands on some "
        "object outside the comprehension, at a moment this audit "
        "cannot place, so what the name holds afterwards cannot be read "
        "from the source. Loop over plain names and assign afterwards."
    )


def _restricted_instance_message(method: str, library: str) -> str:
    allowed = sorted(_RESTRICTED_INSTANCE_METHODS[library])
    listed = ", ".join(allowed) if allowed else "none at all"
    return (
        "calls the method '" + method + "' on a value produced by "
        + library + ". Objects from this library carry methods that "
        "reach the network and the filesystem on their own (a data "
        "frame can write to a database or a URL; an array can write "
        "itself to a file), so the enumerated module-level functions "
        "are the only way this audit accepts it being used. Methods "
        "permitted on such a value: " + listed + ". Read what you need "
        "with an attribute, a subscript, or an operator, and pass the "
        "value to an enumerated function."
    )


def _str_method_message(method: str) -> str:
    return (
        "calls the method '" + method + "' on a value this audit "
        "reads as text. Only the enumerated string data methods ("
        + ", ".join(sorted(_STR_METHODS))
        + ") are accepted there; any other name is not a call target "
        "this audit has cleared."
    )


def _unknown_method_argument_message(method: str) -> str:
    return (
        "passes a value this audit cannot fully resolve to the '"
        + method + "' method of a string receiver this audit "
        "accepted. str.format invokes the formatting protocol of "
        "what it is handed, so even on an accepted receiver the "
        "enumerated data methods accept only plain literals or "
        "values built under this audit's eyes (an allowlisted API's "
        "result, a scanned function's result). Pass a literal, or "
        "build the value from an allowlisted API first."
    )


def _builtin_shadow_message(name: str) -> str:
    return (
        "binds the name '" + name + "', which this audit accepts as a "
        "built-in call target. After a rebinding, code that looks "
        "like a checked built-in call -- or like the isinstance type "
        "gate that checks a parameter is a string -- could run "
        "something else entirely. Leave built-in names bound to "
        "Python's own built-ins and pick a different name."
    )


def _module_surface_message(dotted: str, prefix: str) -> str:
    return (
        "uses '" + dotted + "'. From " + prefix + " only the "
        "enumerated names ("
        + ", ".join(sorted(_ALLOWED_MODULE_ATTRS[prefix]))
        + ") are allowed: membership in an allowed module proves "
        "nothing about what an attribute can do, so every usable "
        "attribute is enumerated one by one. Adding a name is a "
        "policy decision reviewed against the threat model, not a "
        "routine code change."
    )


def _typing_evaluator_message(dotted: str) -> str:
    return (
        "uses '" + dotted + "', which turns annotation text into "
        "running code: a string annotation is compiled and evaluated "
        "to produce the object it names, so any expression written "
        "there runs. That is dynamic code execution and defeats this "
        "offline audit; it is never allowed in synthtwin source."
    )


def _callback_slot_message(callee: str, slot: str) -> str:
    return (
        "fills the callback slot '" + slot + "' of " + callee + " with "
        "a value this audit cannot clear. The library calls whatever "
        "sits in that slot, so only a plain literal, a directly named "
        "accepted built-in (for example str or int), or a directly "
        "named allowlisted API may appear there; a caller-supplied or "
        "computed callable, or a function of this package, would run "
        "outside anything this audit can see."
    )


def _unpacked_slot_message(callee: str, star: str) -> str:
    return (
        "expands '" + star + "' arguments into " + callee + ", an API "
        "with callback slots (argument positions whose value the "
        "library will call). Expansion hides which value lands in "
        "which slot, so this audit cannot confirm the callback slots "
        "stay empty; write each argument out explicitly."
    )


def _callable_argument_message(described: str) -> str:
    return (
        "passes " + described + " as an argument to a callee that is "
        "not defined in the scanned code. Outside code could keep the "
        "callable and run it at any time, in ways this audit cannot "
        "see; Phase 0 synthtwin source may hand functions only to its "
        "own scanned functions."
    )


def _reexport_message(module: str, name: str) -> str:
    return (
        "reaches '" + name + "' through '" + module + "', but '"
        + module + "' does not define '" + name + "': it merely "
        "imports it. Importing or reaching a name a sibling module "
        "itself imported would launder the sibling's own imports past "
        "this audit -- the object handed over is the real imported "
        "module or API, with all its power. Import what you need "
        "directly so the allowlist can check it."
    )


def _undefined_export_message(module: str, name: str) -> str:
    return (
        "reaches '" + name + "' through '" + module + "', but '"
        + module + "' does not define a top-level function, class, or "
        "plain assignment named '" + name + "'. Only names a sibling "
        "module genuinely defines can be verified from the source "
        "text; anything else is rejected."
    )


def _unsettled_export_message(module: str, name: str) -> str:
    return (
        "reaches '" + name + "' through '" + module + "', but '"
        + module + "' binds '" + name + "' more than once, or binds it "
        "through a form whose value cannot be read from the source "
        "text (a loop variable, a `with ... as`, an `except ... as`, a "
        "match capture, a walrus, an unpacking, a `del`, or a "
        "decorator that does not hand the definition back). Which of "
        "those bindings is in force when this name is used is not "
        "something the text settles, so it is refused rather than "
        "trusted. Give the exported name exactly one plain definition "
        "in '" + module + "'."
    )


def _unverified_reexport_message(module: str, name: str) -> str:
    return (
        "imports '" + name + "' from '" + module + "'. '" + name + "' "
        "is the name of a module, and the source of '" + module + "' "
        "is not part of this scan, so the import would hand over a "
        "whole module this audit never cleared. Import what you need "
        "directly so the allowlist can check it."
    )


def _attr_component_message(name: str, dotted: "str | None") -> "str | None":
    """Message for one attribute name in a chain, or None if it is fine."""
    if name in _ENTRY_POINT_TOKENS:
        return (
            "refers to '" + name + "'. Package entry points can "
            "load arbitrary code from any installed package "
            "(EntryPoint.load is a dynamic loader), so any "
            "reference is banned."
        )
    if name == "import_module":
        return (
            "calls or references importlib.import_module, which "
            "loads a module chosen while the program runs; this "
            "audit cannot see what it would load. Use a plain "
            "import statement from the allowlist instead."
        )
    if _is_dunder(name):
        return (
            "reads the double-underscore attribute '" + name + "'. "
            "These attributes expose Python's internal machinery "
            "(module tables, code objects, global state) and can "
            "reach code this audit cannot see; they are banned in "
            "synthtwin source."
        )
    if name == "load" and dotted != "json.load":
        return (
            "reads an attribute named 'load'. Only json.load is "
            "recognized; on anything else, 'load' can be a dynamic "
            "code loader (EntryPoint.load), so the audit rejects "
            "it."
        )
    return None


# THE BINDING GRAMMAR, TAKEN FROM PYTHON RATHER THAN FROM MEMORY.
#
# Every previous version of this audit carried a hand-written list of
# the store shapes it knew about, and every review round found the one
# shape left out of it. The list below is instead the complete set of
# places where Python's own grammar puts an IDENTIFIER inside a syntax
# node -- the ast module publishes that grammar in each node type's
# signature -- split into the fields that bind a name in some scope and
# the fields that name something else entirely. A companion test walks
# the ast module of the running interpreter and fails on any
# identifier field missing from both tables, so a shape a future Python
# adds is caught by a test here instead of by the next review.
#
# Fields that BIND a name. Everything reachable this way is either
# recorded before the scope is checked or refused outright; the
# treatment table below says which, and the same test holds each entry
# to a mutation that must go red.
_BINDING_IDENTIFIER_FIELDS: "dict[str, tuple[str, ...]]" = {
    "AsyncFunctionDef": ("name",),
    "ClassDef": ("name",),
    "ExceptHandler": ("name",),
    "FunctionDef": ("name",),
    "Global": ("names",),
    "MatchAs": ("name",),
    "MatchMapping": ("rest",),
    "MatchStar": ("name",),
    "Name": ("id",),
    "Nonlocal": ("names",),
    "ParamSpec": ("name",),
    "TypeVar": ("name",),
    "TypeVarTuple": ("name",),
    "alias": ("name", "asname"),
    "arg": ("arg",),
}

# Fields that hold an identifier WITHOUT binding a name in any scope,
# each with the reason it cannot be one.
_NON_BINDING_IDENTIFIER_FIELDS: "dict[str, tuple[str, ...]]" = {
    # 'value.attr' names an attribute of an object, not a scope name;
    # attribute stores are checked by the dotted-path policy instead.
    "Attribute": ("attr",),
    # 'from module import ...' names the module read FROM; the names it
    # binds live in the alias nodes under it.
    "ImportFrom": ("module",),
    # 'case Point(x=0)' names attributes of the matched object; the
    # names such a pattern binds live in the sub-patterns under it.
    "MatchClass": ("kwd_attrs",),
    # 'f(name=value)' names a parameter of the callee at a call site.
    "keyword": ("arg",),
}

# How each binding form above is modelled. "collected" means the
# pre-pass records it before any statement of its scope is checked,
# which is what keeps a body that runs later from being read against a
# half-built scope; "scope-local" means the name belongs to a scope
# this audit builds itself (a parameter list); "refused" means the form
# is reported as a violation instead of being modelled, because the
# scope it writes into is one this audit does not follow.
_BINDING_FORM_TREATMENT: "dict[str, str]" = {
    "AsyncFunctionDef": "collected",
    "ClassDef": "collected",
    "ExceptHandler": "collected",
    "FunctionDef": "collected",
    "Global": "refused",
    "MatchAs": "collected",
    "MatchMapping": "collected",
    "MatchStar": "collected",
    "Name": "collected",
    "Nonlocal": "refused",
    "ParamSpec": "refused",
    "TypeVar": "refused",
    "TypeVarTuple": "refused",
    "alias": "collected",
    "arg": "scope-local",
}

# The four comprehension forms. Each has a scope of its own in
# Python 3, and a generator expression's body runs only when something
# draws from it.
_Comprehension = ast.GeneratorExp | ast.ListComp | ast.SetComp | ast.DictComp
# One body whose reading was postponed: the def, async def, lambda, or
# comprehension node, plus the scope stack (scope dicts, then the flags
# saying which of them are class bodies and which are comprehension
# scopes) that was in force where it was written.
_Scopes = list[dict[str, set[tuple[str, str]]]]
_DeferredNode = (
    ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | _Comprehension
)
_DeferredBody = tuple[_DeferredNode, _Scopes, _Scopes, list[bool], list[bool]]
# A statement that binds a name to something written under it.
_Definition = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


class _Checker(ast.NodeVisitor):
    """Walks one module and records policy violations."""

    def __init__(
        self,
        module_exports: "dict[str, tuple[set[str], set[str], set[str]]] | None" = None,
        first_party_modules: "set[str] | None" = None,
    ) -> None:
        self.violations: list[tuple[int, str]] = []
        # A stack of scopes. Each scope maps a local name to the SET of
        # possible origins it may hold: ("module", dotted),
        # ("api", dotted), ("def", name) for functions and classes
        # defined in the scanned code, ("instance", dotted) for a value
        # returned by a call to an allowlisted API, ("literal", "") for
        # a plain literal constant, ("result", name) for the result of
        # a call to a def or class defined in the scanned code, and the
        # explicit ("unknown", "") member for anything this audit
        # cannot trace.
        # Origins only accumulate -- a later store NEVER erases an
        # earlier origin (union semantics), and the unknown member is
        # never discarded when other origins join the set, so a
        # rebinding hidden behind a branch can neither launder away a
        # module nor make an untraceable callback look safe.
        self.scopes: list[dict[str, set[tuple[str, str]]]] = [{}]
        # THE POSITION-BLIND VIEW, which answers every TRUST question.
        # One entry per entry of `scopes`, pushed and popped with it,
        # holding the origins of every binding that scope makes ANYWHERE
        # in its text -- above the use, below it, inside a branch, a
        # loop, a comprehension, or a body that runs later. It is
        # completed BEFORE the first statement of the scope is checked,
        # so no question ever reaches it half-built.
        #
        # Why there are two views at all. Textual position does not
        # decide run-time order: a loop repeats, a function and a
        # comprehension defer, a module can be re-entered. Three
        # successive repairs modelled position and each was defeated one
        # boundary over -- most recently by a rebinding written LOWER IN
        # THE SAME LOOP BODY, which is in force on every iteration after
        # the first while the audit had already read the statement above
        # it and moved on. So position is not modelled on the trust side
        # at all (review item P1-R6-F4).
        self.trust_scopes: list[dict[str, set[tuple[str, str]]]] = [{}]
        # Which entries of `scopes` are class bodies. Python does not
        # let a method body see the names a class body binds -- an
        # unqualified name in a method skips straight to the module --
        # so a lookup from inside a function must skip them. Keeping
        # them visible let a class-level `pathlib.Path` stand in for a
        # module-level function of the same name (review item
        # P1-R5-F1).
        self.class_scopes: list[bool] = [False]
        # Which entries of `scopes` are comprehension scopes. A
        # comprehension's iteration variables live only inside it and
        # do not leak out; the one binding that DOES escape is a walrus,
        # which Python stores in the enclosing function or module, so
        # this flag says which scopes a walrus has to step back past
        # (review item P1-R6-F4).
        self.comprehension_scopes: list[bool] = [False]
        # Dotted paths known to name modules: the fixed allowlist plus
        # every intra-package path seen in this file's import
        # statements. The one-attribute-step rule counts from the
        # longest prefix found here.
        self.module_paths: set[str] = set(_KNOWN_MODULE_PATHS)
        # Per-module export records for every first-party module in the
        # scanned tree: module name -> (defined names, imported names).
        # First-party `from` imports and one-step attribute references
        # are verified against these records.
        self.module_exports = module_exports if module_exports is not None else {}
        self.first_party_modules = (
            set(first_party_modules) if first_party_modules is not None else set()
        )
        # Every node that sits in the function position of a call. A
        # fenced API is legal there and nowhere else.
        self.call_targets: set[int] = set()
        # Function and lambda bodies waiting to be read, each with the
        # scope stack it was written in (the same dict objects, so
        # every store recorded later is visible through them). A def
        # statement BINDS a name; the body runs afterwards, once the
        # surrounding scope has finished, so reading the body where it
        # stands read the surrounding scope half-built and a name
        # rebound below the def kept the origin it had above it
        # (review item P1-R6-F4).
        self.deferred: list[_DeferredBody] = []

    # -- bookkeeping -------------------------------------------------

    def _flag(self, node: ast.AST, message: str) -> None:
        self.violations.append((getattr(node, "lineno", 1), message))

    def _bind(
        self,
        name: str,
        value: "tuple[str, str] | None",
        scope: "dict[str, set[tuple[str, str]]] | None" = None,
    ) -> None:
        target = self.scopes[-1] if scope is None else scope
        slot = target.setdefault(name, set())
        slot.add(value if value is not None else _UNKNOWN)

    # -- answering a question against the position-blind view ---------

    def _open_trust_view(self) -> "_Scopes":
        """Put the position-blind stack in force and hand back the one
        it replaced.

        While a trust question is being answered, `self.scopes` IS the
        position-blind stack, and the walk's own position-sensitive
        stack is not reachable through `self` at all: it lives only in
        the caller's local variable until `_close_trust_view` hands it
        back. That unreachability is the whole mechanism. Round 6
        reviewed a version that kept the blind stack beside the walk's
        and unioned the two answers, on the reasoning that a union can
        only add possibilities; it cannot, because a name the blind
        stack does not bind at all is a name the walk's stack can then
        answer for alone, and that answer is drawn from what the walk
        had reached so far. There is no code path from a trust question
        to the walk's stack any more, so no future edit can reintroduce
        that answer by accident.

        Nesting is safe: opening the view twice puts the same stack in
        force, and each close hands back what its own open replaced.
        """
        walk_scopes = self.scopes
        self.scopes = self.trust_scopes
        return walk_scopes

    def _close_trust_view(self, walk_scopes: "_Scopes") -> None:
        """Put the walk's own stack back in force."""
        self.scopes = walk_scopes

    def _trust_origins(self, value: ast.AST) -> "set[tuple[str, str]]":
        """The origin set every TRUST question reads, and the only one.

        Every question whose answer GRANTS something -- this value may
        be handed to the fenced reader, this receiver may be called,
        this slot is cleared, this decorator hands the definition back
        -- asks through here or through `_trust_lookup` /
        `_resolve_exclusively`, because a grant made against half a
        scope is a grant made against a program that does not exist
        (review item P1-R6-F4).

        POSITION PLAYS NO PART. The origins come from the scope-wide
        union: every binding each name receives anywhere in the
        enclosing scope and its enclosing scopes, whether written above
        the use or below it, on a branch, at the bottom of a loop, or
        inside a body that runs later. Nothing here consults what the
        walk had seen when it arrived.
        """
        walk_scopes = self._open_trust_view()
        try:
            return self._value_origins(value)
        finally:
            self._close_trust_view(walk_scopes)

    def _trust_lookup(self, name: str) -> "set[tuple[str, str]] | None":
        """Every origin a name may hold anywhere in its scope, from the
        position-blind view alone (see _trust_origins). None only when
        no enclosing scope binds the name at all."""
        walk_scopes = self._open_trust_view()
        try:
            return self._lookup(name)
        finally:
            self._close_trust_view(walk_scopes)

    def _trust_resolve(self, parts: "list[str]") -> "list[str]":
        """`_resolve` against the position-blind view.

        The ACCUMULATING form of the trust question: which dotted APIs
        might this chain name, taking every binding the scope makes.
        Used where missing a possibility would silently skip a check
        (which callback slots a callee has, above all), as opposed to
        `_resolve_exclusively`, which answers whether the chain is that
        API and nothing else.
        """
        walk_scopes = self._open_trust_view()
        try:
            return self._resolve(parts)
        finally:
            self._close_trust_view(walk_scopes)

    def _walrus_scope(self) -> "dict[str, set[tuple[str, str]]]":
        """WHICH scope a walrus assignment writes into -- and nothing
        about when it is written.

        Every other store lands in the innermost scope, but `:=` inside
        a comprehension deliberately binds in the function or module
        AROUND the comprehension, so this steps back past comprehension
        scopes to find it. That is a question of place only: choosing
        the right scope does not by itself put the binding there in
        time for a body that is read later, and reading this method as
        if it did was the mistake that left a `:=` written inside a
        generator expression missing from the origin set until after
        the postponed bodies beside it had been read. The TIMING is
        settled elsewhere, by _collect_scope_stores, which records every
        walrus in a scope -- including the ones written inside
        comprehensions -- before any statement of that scope is checked.
        """
        active = self.scopes
        depth = len(active) - 1
        while depth > 0 and self.comprehension_scopes[depth]:
            depth = depth - 1
        return active[depth]

    def _lookup(self, name: str) -> "set[tuple[str, str]] | None":
        """Every origin the name may hold at this point in the walk.

        A class body is the one scope whose own bindings do NOT stand
        alone. Its statements run one after another while the class is
        being built, so a name used above the class-level store, or on
        a branch where that store never ran, is still the module-level
        name -- Python falls straight back to it. A class-level `from
        pathlib import Path` written below a statement that calls
        `Path` therefore proves nothing about what that statement
        calls, and reading the class-local binding alone granted trust
        the running program would not (review item P1-R6-F4). The
        class-local origins are UNIONED with the outer ones instead, so
        both possibilities are carried and neither is trusted on its
        own.

        Which stack is read is whichever is in force: the walk's own,
        position-sensitive one for "must this be checked?", and the
        position-blind one for "may this be trusted?", put in force for
        the duration of the question by `_open_trust_view`.
        """
        active = self.scopes
        top = len(active) - 1
        carried: set[tuple[str, str]] = set()
        depth = top
        while depth >= 0:
            # Skip class bodies unless the lookup is happening directly
            # in one: Python resolves an unqualified name in a method to
            # the module, never to the enclosing class.
            if self.class_scopes[depth] and depth != top:
                depth = depth - 1
                continue
            scope = active[depth]
            if name in scope:
                if depth == top and self.class_scopes[depth]:
                    carried = carried | scope[name]
                    depth = depth - 1
                    continue
                return carried | scope[name]
            depth = depth - 1
        return carried or None

    def _register_module_path(self, dotted: str) -> None:
        parts = dotted.split(".")
        for length in range(1, len(parts) + 1):
            self.module_paths.add(".".join(parts[:length]))

    def _module_prefix(self, dotted: str) -> "tuple[str | None, list[str]]":
        """Split dotted into (longest known module path, remaining parts)."""
        parts = dotted.split(".")
        for length in range(len(parts), 0, -1):
            prefix = ".".join(parts[:length])
            if prefix in self.module_paths:
                return prefix, parts[length:]
        return None, parts

    def _resolve(self, parts: "list[str]") -> "list[str]":
        """Turn a Name/Attribute chain into its possible dotted origins,
        tracing aliases back to the imports or builtins they came from.
        Yields only module/api-rooted dotted candidates; def, instance,
        and unknown possibilities carry no dotted path and are handled
        by the origin-set logic in _value_origins.

        A name resolves to an allowlisted API only when EVERY origin it
        carries is that API. A module that imports a name and also
        defines something with the same name binds the definition --
        Python's later binding wins -- while this audit used to keep the
        import in the union and go on trusting it. Two runnable examples
        in review round 4 turned that into real damage: a local `Path`
        that returned a web address was read through the fenced reader,
        and a local `cast` handed a data frame to a writer that
        overwrote the user's own table. When the origins are mixed, the
        name is reported as untraceable rather than as the API.
        """
        root = parts[0]
        bound = self._lookup(root)
        rest = parts[1:]
        if bound is None:
            if root in _BANNED_BUILTINS:
                return [".".join(["builtins." + root] + rest)]
            return []
        out = []
        for kind, origin in sorted(bound):
            if kind in ("module", "api"):
                out.append(".".join([origin] + rest))
        return out

    def _resolve_exclusively(self, parts: "list[str]") -> "list[str]":
        """Like _resolve, but only when EVERY origin is that API -- and
        taken against EVERY binding the scope makes, wherever it stands.

        The difference decides whether a name may be TRUSTED, as opposed
        to whether it must be CHECKED. `_resolve` keeps an imported
        origin even after a rebinding, because a name that might still
        hold a dangerous module must still be flagged. Trust is the
        other way round: a module that imports a name and also defines
        something with that name binds the definition, and Python calls
        the definition. Review round 4 turned that into real damage
        twice -- a local `Path` returning a web address was read through
        the fenced reader, and a local `cast` handed a data frame to a
        writer that overwrote the user's own table -- so provenance,
        value-preserving calls, and fenced call targets all ask this
        question rather than the other one.

        POSITION IS NOT PART OF THE ANSWER. The set consulted here is
        the position-blind one: the union of every binding the name
        receives anywhere in the enclosing scope and its enclosing
        scopes, whether that binding stands above the use or below it,
        inside a branch, inside a loop, or inside a body that runs
        later. Trust is granted only when every one of those origins is
        independently the allowed API; one binding anywhere in the scope
        that is not the allowed API withdraws trust everywhere in it.

        That is deliberately stricter than Python: a name rebound on the
        last line of a module was in fact the import while the lines
        above it ran, and this refuses them anyway. The refusal is the
        correct direction. Three repairs in a row tried to say WHERE a
        binding takes effect, and each was defeated by the next
        construct -- a loop body, whose last line is in force on every
        iteration but the first, was the third. A refusal is a message
        to a contributor; a trust granted from half a scope is a silent
        hole (review item P1-R6-F4).

        The fourth repair kept the walk's own answer beside this one and
        returned the union, so a name the position-blind view did not
        bind at all was still resolved from what the walk had reached.
        That is the branch this closes: the walk's stack is not
        reachable from here.
        """
        bound = self._trust_lookup(parts[0])
        if bound is not None and any(
            kind not in ("module", "api") for kind, _origin in bound
        ):
            return []
        candidates = self._trust_resolve(parts)
        if any(self._export_is_unsettled(dotted) for dotted in candidates):
            # The same rule one module over: a sibling that binds its
            # exported name more than once exports something this text
            # does not settle, so `paths.validate_local_path` is no more
            # trustworthy than `from paths import validate_local_path`.
            return []
        return candidates

    def _export_is_unsettled(self, dotted: str) -> bool:
        """True when `dotted` names a first-party export the sibling
        module binds more than once, or through a form whose value
        cannot be read (see _module_bindings)."""
        module, _dot, name = dotted.rpartition(".")
        exports = self.module_exports.get(module)
        if exports is None:
            return False
        return name in exports[2]

    def _value_origins(self, value: ast.AST) -> "set[tuple[str, str]]":
        """The possible origins of an expression's VALUE.

        Every possibility this audit cannot pin down contributes the
        explicit unknown member; other origins never displace it.
        """
        if isinstance(value, ast.Constant):
            return {("literal", "")}
        if isinstance(value, (ast.Name, ast.Attribute)):
            parts = _chain_parts(value)
            if parts is None:
                return {_UNKNOWN}
            root, rest = parts[0], parts[1:]
            bound = self._lookup(root)
            if bound is None:
                if root in _BANNED_BUILTINS:
                    return {("api", ".".join(["builtins." + root] + rest))}
                return {_UNKNOWN}
            out: set[tuple[str, str]] = set()
            for kind, origin in bound:
                if kind in ("module", "api"):
                    if rest:
                        out.add(("api", ".".join([origin] + rest)))
                    else:
                        out.add((kind, origin))
                elif (
                    kind == "instance"
                    and rest
                    and origin.partition(".")[0] in _RESTRICTED_INSTANCE_METHODS
                ):
                    # An attribute of a restricted object is still that
                    # library's object; only the enumerated names get
                    # this far, and they must not launder the origin.
                    out.add((kind, origin))
                elif rest:
                    # An attribute read on a def, instance, or unknown
                    # value produces a value this audit cannot trace.
                    out.add(_UNKNOWN)
                else:
                    out.add((kind, origin))
            return out or {_UNKNOWN}
        if isinstance(value, ast.Call):
            return self._call_result_origins(value)
        if isinstance(value, ast.BinOp):
            merged = self._value_origins(value.left) | self._value_origins(
                value.right
            )
            instances = {origin for origin in merged if origin[0] == "instance"}
            # An operator on an api-instance runs the API class's own
            # operator method; the result is a value that allowlisted
            # code produced (policy case (b) in the module docstring).
            return instances or {_UNKNOWN}
        if isinstance(value, ast.Subscript):
            # A slice or an index of a value this audit reads as text
            # is itself text (E4). A subscript of a RESTRICTED library
            # object keeps that library: frame["x"] is a pandas object
            # too, and selecting one was a route to its writers
            # (review item P1-R2-F2).
            inner = self._value_origins(value.value)
            carried = {
                (kind, origin)
                for kind, origin in inner
                if kind == "instance"
                and origin.partition(".")[0] in _RESTRICTED_INSTANCE_METHODS
            }
            if carried:
                return carried
            if inner and all(kind in ("literal", "str") for kind, _origin in inner):
                return {("str", "")}
            return {_UNKNOWN}
        if isinstance(value, ast.JoinedStr):
            # An f-string. Its result is text, but only when every
            # interpolated value is one this audit already resolved:
            # formatting invokes the __format__ of what it is handed,
            # and an untraced value must never become text (E4).
            #
            # A FORMAT SPECIFICATION IS ITSELF AN EXPRESSION. In
            # f"{'x':{spec}}" the part after the colon is a nested
            # f-string, so the text that comes out is built from `spec`
            # just as surely as from the value in front of it, and
            # reading only the value let an unknown one arrive as
            # trusted text (review item P1-R6-F12). The same rule is
            # applied to it by walking it through this method, which
            # recurses into any specification nested inside it.
            # The conversion field (!r, !s, !a) needs no separate rule:
            # it applies repr, str, or ascii to the value that was just
            # checked, and produces text from text.
            for piece in value.values:
                if not isinstance(piece, ast.FormattedValue):
                    continue
                # Whether the result may be READ AS TEXT is a trust
                # question, so it is asked position-blind.
                origins = self._trust_origins(piece.value)
                if piece.format_spec is not None:
                    origins = origins | self._trust_origins(piece.format_spec)
                if not all(
                    kind in _SAFE_DATA_ARGUMENT_KINDS for kind, _origin in origins
                ):
                    return {_UNKNOWN}
            return {("str", "")}
        if isinstance(value, ast.IfExp):
            return self._value_origins(value.body) | self._value_origins(
                value.orelse
            )
        if isinstance(value, ast.BoolOp):
            out = set()
            for operand in value.values:
                out |= self._value_origins(operand)
            return out or {_UNKNOWN}
        return {_UNKNOWN}

    def _call_result_origins(self, call: ast.Call) -> "set[tuple[str, str]]":
        """Origins of a call expression's result.

        A call to an API that the allowlist accepts yields an
        api-instance (policy case (b)); a call to a name bound ONLY to
        defs or classes defined in the scanned code yields the
        ("result", name) member (every expression inside a scanned def
        was itself checked under these rules); a text-returning method
        on an accepted text receiver, and a call to str, repr, or
        format, yield the text member (extension E4); every other call
        yields the unknown member.
        """
        func = call.func
        localpath = self._localpath_call_result(call)
        if localpath is not None:
            return localpath
        # typing.cast returns its second argument unchanged. Treating it
        # as a value of its own let a pandas frame shed its origin and
        # walk past the no-method rule (review item P1-R1-F2).
        parts = _chain_parts(func) if isinstance(func, (ast.Name, ast.Attribute)) else None
        if parts is not None and self._resolve_exclusively(parts) == ["typing.cast"]:
            # Every supported call form, not just the positional one:
            # the keyword form slipped a pandas frame past the method
            # rule (review item P1-R2-F2).
            carried = None
            if len(call.args) == 2 and not isinstance(call.args[1], ast.Starred):
                carried = call.args[1]
            for keyword in call.keywords:
                if keyword.arg == "val":
                    carried = keyword.value
            if carried is not None:
                return self._value_origins(carried)
            return {_UNKNOWN}
        text = self._text_call_result(func)
        if text is not None:
            return text
        if not isinstance(func, (ast.Name, ast.Attribute)):
            return {_UNKNOWN}
        parts = _chain_parts(func)
        if parts is None:
            return {_UNKNOWN}
        out: set[tuple[str, str]] = set()
        for dotted in self._resolve(parts):
            if (
                dotted.partition(".")[0] != "builtins"
                and self._policy_for(dotted, False) is None
            ):
                out.add(("instance", dotted))
            else:
                out.add(_UNKNOWN)
        bound = self._lookup(parts[0])
        if bound is None:
            if parts[0] not in _BANNED_BUILTINS:
                out.add(_UNKNOWN)
        elif len(parts) == 1 and all(kind == "def" for kind, _origin in bound):
            out.add(("result", parts[0]))
        else:
            for kind, _origin in bound:
                if kind not in ("module", "api"):
                    out.add(_UNKNOWN)
        return out or {_UNKNOWN}

    def _localpath_call_result(
        self, call: ast.Call
    ) -> "set[tuple[str, str]] | None":
        """The validated-local-path origin, or None (fence for F1).

        It starts at a call to validate_local_path and survives exactly
        one wrapping in pathlib.Path, which is how a validated result
        becomes the object the reader hands to the library. Nothing else
        produces it, so it cannot be manufactured.
        """
        parts = _chain_parts(call.func)
        if parts is None:
            return None
        resolved = self._resolve_exclusively(parts)
        if resolved and all(
            dotted == _LOCAL_PATH_VALIDATOR for dotted in resolved
        ):
            return {_LOCALPATH}
        if resolved == ["pathlib.Path"] and len(call.args) == 1:
            inner = call.args[0]
            if not isinstance(inner, ast.Starred) and self._trust_origins(
                inner
            ) == {_LOCALPATH}:
                return {_LOCALPATH}
        return None

    def _text_call_result(self, func: ast.AST) -> "set[tuple[str, str]] | None":
        """Text origin for a call whose result is text, else None (E4).

        Two shapes qualify, and only these two: an enumerated
        text-RETURNING string method called on a receiver this audit
        already reads as text, and an unshadowed call to str, repr, or
        format. A method whose result is not text (split, find,
        startswith) returns None here, so its result stays untraced and
        no method call is accepted on it. Text never originates at an
        untraced value: the receiver must already be text.
        """
        if isinstance(func, ast.Name):
            if (
                func.id in _TEXT_PRODUCING_BUILTINS
                and self._trust_lookup(func.id) is None
            ):
                return {("str", "")}
            return None
        if not isinstance(func, ast.Attribute):
            return None
        if func.attr not in _TEXT_RESULT_STR_METHODS:
            return None
        receiver = self._trust_origins(func.value)
        if not receiver:
            return None
        if all(kind in ("literal", "str") for kind, _origin in receiver):
            return {("str", "")}
        return None

    def _bind_from_value(self, name: str, value: ast.AST) -> None:
        for kind, origin in self._value_origins(value):
            if kind == "api" and origin in self.module_paths:
                self._bind(name, ("module", origin))
            else:
                self._bind(name, (kind, origin))

    def _collect_scope_bindings(self, body: "list[ast.stmt]") -> None:
        """Pre-bind the imports and definitions this scope makes.

        Flow-insensitive on purpose: an import or a def/class statement
        anywhere in a scope -- inside any branch, loop, or try block --
        is visible to the whole scope before the statements are walked,
        and later stores never erase it. Nested function, class, and
        lambda bodies are separate scopes and are not entered here.

        Imports are recorded first and definitions second, so that a
        decorator written as an imported name is already traceable when
        the name it decorates is bound. Every OTHER binding form is
        recorded by _collect_scope_stores, which runs after these two
        and needs them: it reads the values being stored.
        """
        definitions: list[_Definition] = []
        stack: list[ast.AST] = list(body)
        while stack:
            node = stack.pop()
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                definitions.append(node)
                continue
            if isinstance(node, ast.Lambda):
                continue
            if isinstance(node, ast.Import):
                self._handle_import(node, report=False)
            elif isinstance(node, ast.ImportFrom):
                self._handle_import_from(node, report=False)
            else:
                stack.extend(ast.iter_child_nodes(node))
        for definition in definitions:
            self._bind_definition(definition)

    # -- the position-blind view -------------------------------------

    def _build_trust_scope(
        self, nodes: "list[ast.AST]", gate_body: "list[ast.stmt] | None"
    ) -> None:
        """Fill the top TRUST scope with every binding this scope makes.

        Called once, at scope entry, before a single statement of the
        scope is checked. It replays the same three steps the walk
        itself performs -- imports and definitions, then the type-gate
        narrowing, then every other store -- into `trust_scopes` rather
        than `scopes`, and it does not stop where the walk has got to:
        the whole body is read, so a binding written below a use, at the
        bottom of a loop, or inside a body that runs later is already in
        the set when the use above it asks whether it may be trusted.

        Nothing is reported from here. The collectors it drives record
        origins and raise no message, so a scope is never counted twice.
        """
        walk_scopes = self._open_trust_view()
        try:
            statements = [node for node in nodes if isinstance(node, ast.stmt)]
            self._collect_scope_bindings(statements)
            if gate_body is not None:
                self._upgrade_gated_parameters(gate_body)
            self._complete_trust_bindings(nodes, statements)
        finally:
            self._close_trust_view(walk_scopes)

    def _trust_snapshot(self) -> "dict[str, frozenset[tuple[str, str]]]":
        """A comparable copy of the trust scope now on top."""
        return {
            name: frozenset(origins)
            for name, origins in self.trust_scopes[-1].items()
        }

    def _complete_trust_bindings(
        self, nodes: "list[ast.AST]", statements: "list[ast.stmt]"
    ) -> None:
        """Record every binding of this scope, repeatedly, until the set
        stops growing.

        One pass is not enough on its own. A store reads the names
        around it (`file_path = pathlib.Path(validated)` is a validated
        path only because `validated` is one), and those names may
        themselves be stored further down the scope, so a single pass
        would read some of them before their own origins were in. The
        passes are monotone -- origins accumulate and are never
        discarded -- so repeating one can only add possibilities, and
        the set settles once nothing new arrives.

        BOTH steps repeat, imports and definitions included. A def or a
        class statement is a store whose recorded origin depends on
        reading its decorators, and a decorator read on the first pass
        alone was read against a set the rest of the scope had not
        joined yet: a name decorated by what LOOKED like one of the
        enumerated definition-preserving decorators kept the readable
        definition origin even when the decorator itself was rebound
        further down. Repeating the step lets that later binding
        withdraw the reading, which is the same monotone direction as
        every other pass.

        A scope whose set has not settled by the last pass is one this
        audit cannot reason about, so it is REFUSED: the unknown member
        is added to every name the scope carries, which withdraws trust
        from all of them. Nothing in the src tree comes close to the
        limit; the shapes that do not settle are ones that build a
        longer attribute chain on every pass (`value = value.deeper`),
        and those are rejected on their own terms as well.
        """
        settled = None
        for _pass in range(_TRUST_PASSES):
            self._collect_scope_bindings(statements)
            self._collect_scope_stores(nodes)
            current = self._trust_snapshot()
            if current == settled:
                return
            settled = current
        for name in list(self.trust_scopes[-1]):
            self.trust_scopes[-1][name].add(_UNKNOWN)

    def _enter_scope(
        self,
        locals_: "dict[str, set[tuple[str, str]]]",
        is_class: bool,
        is_comprehension: bool,
    ) -> None:
        """Push one scope onto both stacks, seeded with the same names.

        The two views are always the same depth, so `class_scopes` and
        `comprehension_scopes` describe them both.
        """
        self.scopes.append({name: set(origins) for name, origins in locals_.items()})
        self.trust_scopes.append(
            {name: set(origins) for name, origins in locals_.items()}
        )
        self.class_scopes.append(is_class)
        self.comprehension_scopes.append(is_comprehension)

    def _leave_scope(self) -> None:
        self.scopes.pop()
        self.trust_scopes.pop()
        self.class_scopes.pop()
        self.comprehension_scopes.pop()

    # -- completing a scope's bindings -------------------------------

    def _collect_scope_stores(self, nodes: "list[ast.AST]") -> None:
        """Record every binding this scope makes, other than its
        imports and definitions (review item P1-R6-F4).

        Driven from two places, into two different views of the scope.
        The POSITION-BLIND view calls it on scope entry, repeatedly,
        before a single statement has been checked, which is what lets
        a trust decision see a binding written below it. The CHECKING
        view calls it at one moment: after the scope's own statements
        have been checked where they stand, and before the first body
        postponed inside it is read. Both halves of that second
        placement are load-bearing.

        Not earlier, because the statements of a scope run in the order
        they are written: a store two lines below a statement has not
        happened when that statement runs, and reporting the statement
        against it would call honest code a violation.

        Not later, because a postponed body -- a function, a lambda, a
        generator expression -- runs after the scope around it has
        finished, so it must be read against a scope whose bindings are
        all in. Leaving each form to record its own store as the walk
        reached it left the stores the walk had not reached yet missing
        from the set: a `:=` written inside a generator expression
        binds in the scope around it, but nothing in that expression is
        executed until something draws from it, so it was recorded only
        while that postponed body was itself being read -- after the
        function beside it had already been read, and trusted, against
        the name it rebinds.

        What is walked is Python's grammar, not a list of the shapes
        that came up in review: any Name in a store or delete context
        binds, and so does every identifier field the grammar tables
        above mark as binding. Two kinds of subtree are skipped because
        their names belong to a DIFFERENT scope -- the body of a nested
        def, lambda, or class, and a comprehension's iteration targets
        -- while the expressions such a form evaluates where it stands
        (decorators, default values, annotations, base classes, the
        iterables and conditions of a comprehension) are walked, since a
        walrus written in one of them binds right here.

        Origins only accumulate, so recording a store a second time can
        add possibilities and can never remove one: this pass can turn
        trust into suspicion, never the other way round. Nothing is
        reported from here -- every violation is raised by the checking
        walk -- so no message is doubled.
        """
        for node in nodes:
            self._collect_store(node)

    def _collect_store(self, node: ast.AST) -> None:
        """Record what one node binds in the scope now on top."""
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Recorded already, with the origins they carry.
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # The name is bound by _collect_scope_bindings; the body is
            # a scope of its own. What is left runs where it stands.
            self._collect_scope_stores(list(node.decorator_list))
            self._collect_argument_stores(node.args)
            if node.returns is not None:
                self._collect_store(node.returns)
            return
        if isinstance(node, ast.Lambda):
            self._collect_argument_stores(node.args)
            return
        if isinstance(node, ast.ClassDef):
            self._collect_scope_stores(list(node.decorator_list))
            self._collect_scope_stores(list(node.bases))
            self._collect_scope_stores([kw.value for kw in node.keywords])
            return
        if isinstance(
            node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
        ):
            self._collect_comprehension_stores(node)
            return
        if isinstance(node, ast.Assign):
            self._collect_store(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._bind_from_value(target.id, node.value)
                else:
                    self._collect_store(target)
            return
        if isinstance(node, ast.AnnAssign):
            self._collect_store(node.annotation)
            if node.value is not None:
                self._collect_store(node.value)
            if isinstance(node.target, ast.Name):
                if node.value is not None:
                    self._bind_from_value(node.target.id, node.value)
                else:
                    self._bind(node.target.id, None)
            else:
                self._collect_store(node.target)
            return
        if isinstance(node, ast.NamedExpr):
            self._collect_store(node.value)
            if isinstance(node.target, ast.Name):
                # `:=` binds in the scope AROUND a comprehension; see
                # _walrus_scope.
                self._bind(node.target.id, None, scope=self._walrus_scope())
            else:
                self._collect_store(node.target)
            return
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                self._bind(node.id, None)
            return
        if isinstance(node, ast.arg):
            # A parameter belongs to the body's own scope; only the
            # annotation is evaluated here.
            if node.annotation is not None:
                self._collect_store(node.annotation)
            return
        # `except E as name`, `case name:` and `case [*name]` all keep
        # the bound name in a plain string field called `name`.
        if isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)):
            if node.name is not None:
                self._bind(node.name, None)
        elif isinstance(node, ast.MatchMapping):
            if node.rest is not None:
                self._bind(node.rest, None)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            # Both are refused by their visitors; the names are recorded
            # anyway so that nothing downstream reads a stale origin.
            for name in node.names:
                self._bind(name, None)
        self._collect_scope_stores(list(ast.iter_child_nodes(node)))

    def _collect_argument_stores(self, args: ast.arguments) -> None:
        """Walk the parts of a parameter list that are evaluated where
        the def or lambda stands: default values and annotations. The
        parameter NAMES belong to the body's own scope."""
        for default in list(args.defaults) + [
            d for d in args.kw_defaults if d is not None
        ]:
            self._collect_store(default)
        for parameter in _parameters_of(args):
            if parameter.annotation is not None:
                self._collect_store(parameter.annotation)

    def _collect_comprehension_stores(self, node: _Comprehension) -> None:
        """Walk a comprehension for bindings that land in THIS scope.

        The iteration targets are not among them: they live in the
        comprehension's own scope and are bound there. A walrus is,
        which is the whole point of walking in here -- a generator
        expression is read long after the scope around it has finished,
        so a `:=` inside one has to be in the origin set before that
        happens.
        """
        for generator in node.generators:
            self._collect_store(generator.iter)
            self._collect_scope_stores(list(generator.ifs))
        if isinstance(node, ast.DictComp):
            self._collect_store(node.key)
            self._collect_store(node.value)
        else:
            self._collect_store(node.elt)

    def _bind_definition(self, node: "_Definition") -> None:
        """Record what a def, async def, or class statement stores.

        The statement binds its name to the definition -- unless a
        decorator sits above it, because a decorator is handed the
        definition and the NAME then holds whatever it hands back. Only
        the enumerated decorators that give the definition itself back
        leave the name readable as that definition; after any other
        decorator the name carries the unknown member as well, so
        calling through it is rejected (review item P1-R6-F4).
        """
        self._bind(node.name, ("def", node.name))
        for decorator in node.decorator_list:
            if not self._decorator_keeps_definition(decorator):
                self._bind(node.name, None)
                return

    def _decorator_keeps_definition(self, decorator: ast.AST) -> bool:
        """True when a decorator is one of the enumerated few that hand
        the decorated definition back (_DEFINITION_PRESERVING_DECORATORS).
        Every other decorator -- above all one this audit cannot trace
        at all -- is treated as replacing the decorated name's value."""
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Name) and self._trust_lookup(target.id) is None:
            # An unshadowed built-in decorator name.
            return target.id in _DEFINITION_PRESERVING_DECORATORS
        parts = _chain_parts(target)
        if parts is None:
            return False
        resolved = self._resolve_exclusively(parts)
        return bool(resolved) and all(
            dotted in _DEFINITION_PRESERVING_DECORATORS for dotted in resolved
        )

    # -- bodies that run later ---------------------------------------

    def _defer_body(self, node: _DeferredNode) -> None:
        """Postpone one function, lambda, or generator-expression body
        until its surrounding scope has been walked to the end (review
        item P1-R6-F4)."""
        self.deferred.append(
            (
                node,
                list(self.scopes),
                list(self.trust_scopes),
                list(self.class_scopes),
                list(self.comprehension_scopes),
            )
        )

    def _walk_scope_body(self, body: "list[ast.stmt]") -> None:
        """Walk the statements of a scope, complete the scope's set of
        bindings, and only then read every body that was postponed
        inside it.

        The middle step is the ordering rule of review item P1-R6-F4,
        and it is one step of this method rather than a rule each
        binding form has to remember: whatever the walk did or did not
        record, EVERY name this scope binds is in the origin set before
        the first postponed body is read.
        """
        mark = len(self.deferred)
        for statement in body:
            self.visit(statement)
        self._collect_scope_stores(list(body))
        self._read_deferred_bodies(mark)

    def _read_deferred_bodies(self, mark: int) -> None:
        """Read the bodies postponed since `mark`, oldest first, each
        with the scope stack it was written in restored."""
        while len(self.deferred) > mark:
            (
                node,
                scopes,
                trust_scopes,
                class_scopes,
                comp_scopes,
            ) = self.deferred.pop(mark)
            outer_scopes = self.scopes
            outer_trust_scopes = self.trust_scopes
            outer_class_scopes = self.class_scopes
            outer_comp_scopes = self.comprehension_scopes
            self.scopes = scopes
            self.trust_scopes = trust_scopes
            self.class_scopes = class_scopes
            self.comprehension_scopes = comp_scopes
            if isinstance(node, ast.Lambda):
                self._read_lambda_body(node)
            elif isinstance(
                node,
                (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp),
            ):
                self._read_comprehension_body(node)
            else:
                self._read_function_body(node)
            self.scopes = outer_scopes
            self.trust_scopes = outer_trust_scopes
            self.class_scopes = outer_class_scopes
            self.comprehension_scopes = outer_comp_scopes

    # -- the positive policy -----------------------------------------

    def _policy_for(self, dotted: str, is_store: bool) -> "str | None":
        """Check a fully resolved dotted path against the D6.2 allowlist.

        Returns an explanation string when the path violates the policy,
        None when it is allowed.
        """
        top = dotted.partition(".")[0]

        if top in _FORBIDDEN_MODULES:
            return _forbidden_module_message(top, "uses " + repr(dotted) + " from")

        if top == "builtins":
            name = dotted.split(".")[1]
            return _primitive_message(name) + " (reached through an alias)"

        if is_store and "." in dotted:
            return (
                "writes to '" + dotted + "', an attribute of an imported "
                "module. Module state must stay exactly as Python ships it; "
                "changing it can change what code runs later. Remove the "
                "write."
            )

        prefix, rest = self._module_prefix(dotted)
        if prefix is None:
            return (
                "uses '" + dotted + "', which does not resolve to any "
                "allowlisted API. " + _ALLOWLIST_NOTE
            )
        if not rest:
            return None

        if top == "sys":
            for banned in _SYS_BANNED:
                if dotted == banned or dotted.startswith(banned + "."):
                    return (
                        "touches '" + dotted + "', part of Python's import "
                        "machinery. Reading or changing it can smuggle in "
                        "code this offline audit never sees; it is banned "
                        "in synthtwin source."
                    )

        if prefix == "os":
            if rest[0] == "environ":
                if len(rest) == 1:
                    return None
                if len(rest) == 2 and rest[1] in _ENV_READ_METHODS:
                    return None
                return (
                    "changes or misuses os.environ ('" + dotted + "'). The "
                    "allowlist permits reading environment variables only; "
                    "remove the write."
                )
            if rest[0] in {"system", "popen", "fork", "posix_spawn"} or rest[
                0
            ].startswith(("exec", "spawn")):
                return (
                    "uses '" + dotted + "', which can start or replace "
                    "programs on this computer. synthtwin promises never to "
                    "do that; remove it."
                )

        for part in rest:
            if part in _MODULE_ATTR_BLOCK:
                return _module_hop_message(dotted, part)
            if part.startswith("_"):
                return _private_hop_message(dotted, part)

        if len(rest) > 1:
            return _deep_chain_message(dotted, prefix)

        if prefix in self.module_exports:
            defined, imported_names, unsettled = self.module_exports[prefix]
            if rest[0] in imported_names:
                return _reexport_message(prefix, rest[0])
            if rest[0] not in defined:
                return _undefined_export_message(prefix, rest[0])
            if rest[0] in unsettled:
                return _unsettled_export_message(prefix, rest[0])

        if prefix == "os":
            if dotted in _OS_ALLOWED_EXACT:
                return None
            return (
                "uses '" + dotted + "'. From the os module only the os.path "
                "functions, os.fspath, os.getcwd, os.lstat, and reading "
                "os.environ are allowed."
            )

        if prefix in ("importlib", "importlib.metadata"):
            if dotted == "importlib.metadata.version":
                return None
            return (
                "uses '" + dotted + "'. From importlib only "
                "importlib.metadata.version() is allowed (it reads the "
                "installed version string); everything else can load code "
                "chosen while the program runs."
            )

        if prefix in _ALLOWED_MODULE_ATTRS:
            if prefix == "typing" and rest[0] in _TYPING_EVALUATORS:
                return _typing_evaluator_message(dotted)
            if rest[0] in _ALLOWED_MODULE_ATTRS[prefix]:
                return None
            return _module_surface_message(dotted, prefix)

        return None

    # -- shared identifier checks ------------------------------------

    def _check_name(self, node: ast.AST, name: str) -> None:
        if name in _BANNED_BUILTINS:
            self._flag(node, _primitive_message(name))
        elif name in _FORBIDDEN_MODULES:
            self._flag(node, _forbidden_module_message(name, "refers to"))
        elif name in _ENTRY_POINT_TOKENS:
            self._flag(
                node,
                "refers to '" + name + "'. Package entry points can "
                "load arbitrary code from any installed package "
                "(EntryPoint.load is a dynamic loader), so any "
                "reference is banned.",
            )
        elif _is_dunder(name) and name not in _ALLOWED_DUNDER_NAMES:
            self._flag(
                node,
                "uses the double-underscore name '" + name + "'. These "
                "names expose Python's internal machinery; only "
                "__name__, __doc__, __file__, __version__ and __all__ "
                "are allowed in synthtwin source.",
            )

    def _check_attr_component(
        self, node: ast.AST, name: str, dotted: "str | None"
    ) -> bool:
        """Check one attribute name in a chain. Returns True if it was
        flagged."""
        message = _attr_component_message(name, dotted)
        if message is not None:
            self._flag(node, message)
            return True
        return False

    # -- imports -----------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        self._handle_import(node, report=True)

    def _handle_import(self, node: ast.Import, report: bool) -> None:
        for alias in node.names:
            name = alias.name
            top = name.partition(".")[0]
            bound_name = alias.asname or top
            origin = name if alias.asname else top

            if report and bound_name in _ALLOWED_CALL_BUILTINS:
                self._flag(node, _builtin_shadow_message(bound_name))
            if top == _FIRST_PARTY_ROOT:
                self._register_module_path(name)
                self._bind(bound_name, ("module", origin))
                continue
            if name in {"argparse", "csv", "dataclasses", "json", "math",
                        "pandas", "pathlib", "typing", "sys", "os"}:
                self._bind(bound_name, ("module", name))
                continue
            if name in {"os.path", "importlib.metadata"}:
                self._bind(bound_name, ("module", origin))
                continue

            # Not allowed. Bind anyway so later uses are reported too.
            self._bind(bound_name, ("module", origin))
            if not report:
                continue
            if top in _FORBIDDEN_MODULES:
                self._flag(node, _forbidden_module_message(top, "imports"))
            elif top == "importlib":
                self._flag(
                    node,
                    "imports '" + name + "'. Only 'import "
                    "importlib.metadata' is allowed, and from it only "
                    "the version() function may be used.",
                )
            elif top == "os":
                self._flag(
                    node,
                    "imports '" + name + "'. From os only 'import os' "
                    "or 'import os.path' is allowed. " + _ALLOWLIST_NOTE,
                )
            else:
                self._flag(
                    node,
                    "imports '" + name + "', which is not on the "
                    "Phase 0 allowlist. " + _ALLOWLIST_NOTE,
                )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._handle_import_from(node, report=True)

    def _handle_import_from(self, node: ast.ImportFrom, report: bool) -> None:
        if node.level and node.level > 0:
            base = _FIRST_PARTY_ROOT
            if node.module:
                base = base + "." + node.module
            self._register_module_path(base)
            for alias in node.names:
                if alias.name == "*":
                    if report:
                        self._flag_star(node, base)
                    continue
                self._first_party_from_alias(node, base, alias, report)
            return

        module = node.module or ""
        top = module.partition(".")[0]

        if top == _FIRST_PARTY_ROOT:
            self._register_module_path(module)
            for alias in node.names:
                if alias.name == "*":
                    if report:
                        self._flag_star(node, module)
                    continue
                self._first_party_from_alias(node, module, alias, report)
            return

        for alias in node.names:
            if alias.name == "*":
                if report:
                    self._flag_star(node, module)
                continue
            if report and (alias.asname or alias.name) in _ALLOWED_CALL_BUILTINS:
                self._flag(
                    node, _builtin_shadow_message(alias.asname or alias.name)
                )
            dotted = module + "." + alias.name
            problem = _attr_component_message(alias.name, dotted)
            if problem is not None:
                if report:
                    self._flag(node, problem)
                continue
            message = self._policy_for(dotted, False)
            if message is not None:
                if report:
                    self._flag(node, message)
                continue
            kind = "module" if dotted in self.module_paths else "api"
            self._bind(alias.asname or alias.name, (kind, dotted))

    def _first_party_from_alias(
        self, node: ast.ImportFrom, module: str, alias: ast.alias, report: bool
    ) -> None:
        """Handle one name in a first-party `from` import.

        The name must be a submodule of the scanned tree or a name the
        sibling module genuinely defines. A name the sibling itself
        imported is rejected: importing it would launder the sibling's
        own imports past this audit (plan D6.2).
        """
        bound_name = alias.asname or alias.name
        dotted = module + "." + alias.name

        if report and bound_name in _ALLOWED_CALL_BUILTINS:
            self._flag(node, _builtin_shadow_message(bound_name))
        if dotted in self.first_party_modules:
            self._register_module_path(dotted)
            self._bind(bound_name, ("module", dotted))
            return

        exports = self.module_exports.get(module)
        if exports is not None:
            defined, imported_names, unsettled = exports
            if alias.name in defined:
                self._bind(bound_name, ("api", dotted))
                if alias.name in unsettled:
                    # The sibling binds this name more than once, or
                    # through a form whose value cannot be read. Which
                    # binding is in force is not settled by the text, so
                    # the unknown member joins and trust is withdrawn
                    # here rather than at the sibling's last line
                    # (review item P1-R6-F4).
                    self._bind(bound_name, None)
                    if report:
                        self._flag(
                            node, _unsettled_export_message(module, alias.name)
                        )
                return
            if report:
                if alias.name in imported_names:
                    self._flag(node, _reexport_message(module, alias.name))
                else:
                    self._flag(node, _undefined_export_message(module, alias.name))
            self._bind(bound_name, ("api", dotted))
            return

        # The sibling module's source is not part of this scan, so its
        # exports cannot be verified. A name that matches a known
        # module name would hand over a whole module; reject it.
        if alias.name in _MODULE_ATTR_BLOCK:
            if report:
                self._flag(node, _unverified_reexport_message(module, alias.name))
            self._bind(bound_name, ("api", dotted))
            return

        # The alias may itself be a module; register it so the
        # one-step rule counts from it, not through it.
        self._register_module_path(dotted)
        self._bind(bound_name, ("module", dotted))

    def _flag_star(self, node: ast.AST, module: str) -> None:
        self._flag(
            node,
            "uses 'from " + module + " import *', which creates names "
            "this audit cannot enumerate. Import each name explicitly.",
        )

    # -- expressions -------------------------------------------------

    def visit_Name(self, node: ast.Name) -> None:
        self._check_name(node, node.id)
        if isinstance(node.ctx, ast.Load) and id(node) not in self.call_targets:
            # Missing a fenced reference would let the reader be stored
            # or passed unremarked, so the identities are the
            # position-blind ones (review item P1-R6-F4).
            for dotted in self._trust_resolve([node.id]):
                if dotted in _FENCED_APIS:
                    self._flag(node, _fenced_reference_message(dotted))
                    return
        if isinstance(node.ctx, ast.Load):
            bound = self._lookup(node.id)
            if bound:
                seen: set[str] = set()
                for kind, origin in sorted(bound):
                    if kind in (
                        "def",
                        "instance",
                        "literal",
                        "localpath",
                        "result",
                        "str",
                        "unknown",
                    ):
                        # Reading a scanned definition, an api-instance,
                        # a literal, a scanned call's result, a
                        # gate-checked string, or an untraced value is
                        # fine; only CALLS through them are restricted.
                        continue
                    if kind == "module" and not origin.startswith(
                        _FIRST_PARTY_ROOT
                    ):
                        message: str | None = _bare_module_message(origin)
                    else:
                        message = self._policy_for(origin, False)
                    if message is not None and message not in seen:
                        seen.add(message)
                        self._flag(node, message)
        elif isinstance(node.ctx, (ast.Store, ast.Del)):
            if node.id in _ALLOWED_CALL_BUILTINS:
                self._flag(node, _builtin_shadow_message(node.id))
            # Record that the name is bound to something untraced here.
            # Every origin the name already had is kept: a store on one
            # path never proves the old value is gone on another path,
            # and the unknown member this store adds is never discarded.
            self._bind(node.id, None)

    def _check_restricted_attribute(self, node: ast.Attribute) -> bool:
        """Reject an unenumerated attribute of a pandas/numpy value.

        Letting the read through GRANTS -- `frame.style` reaches a whole
        unenumerated capability with no call in sight -- so the receiver
        is read position-blind. From the walk's own view, a name that
        holds the library's object on a binding written BELOW the read
        carried no library origin there at all and every attribute of it
        was allowed (review item P1-R6-F4).
        """
        if id(node) in self.call_targets:
            # A method call; the method rule governs it.
            return False
        for kind, origin in sorted(self._trust_origins(node.value)):
            if kind != "instance":
                continue
            library = origin.partition(".")[0]
            if library not in _RESTRICTED_INSTANCE_ATTRIBUTES:
                continue
            if node.attr in _RESTRICTED_INSTANCE_ATTRIBUTES[library]:
                continue
            self._flag(node, _restricted_attribute_message(node.attr, library))
            return True
        return False

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if self._check_restricted_attribute(node):
            return
        parts = _chain_parts(node)
        if parts is not None and id(node) not in self.call_targets:
            # Position-blind, for the reason given in visit_Name.
            for dotted in self._trust_resolve(parts):
                if dotted in _FENCED_APIS:
                    self._flag(node, _fenced_reference_message(dotted))
                    return
        if parts is None:
            # Attribute on a computed value (call result, subscript,
            # literal): only the attribute-name bans apply to the READ;
            # calling the attribute is checked in visit_Call.
            self._check_attr_component(node, node.attr, None)
            self.generic_visit(node)
            return

        candidates = self._resolve(parts)
        primary = candidates[0] if len(candidates) == 1 else None
        flagged = False
        for part in parts[1:]:
            if self._check_attr_component(node, part, primary):
                flagged = True
        if flagged:
            return
        if not candidates:
            self._check_name(node, parts[0])
            return
        is_store = isinstance(node.ctx, (ast.Store, ast.Del))
        seen: set[str] = set()
        for dotted in candidates:
            message = self._policy_for(dotted, is_store)
            if message is None and not is_store and dotted in self.module_paths:
                # The chain resolves to a module object used as a plain
                # value (for example passing os.path into a function).
                message = _bare_module_message(dotted)
            if message is not None and message not in seen:
                seen.add(message)
                self._flag(node, message)
        # A pure chain has no other children worth visiting; skipping
        # them avoids reporting the same chain twice.

    def _check_fenced_call(self, node: ast.Call) -> None:
        """A fenced API may only be called with a validated local path.

        The identities are the ACCUMULATING position-blind ones: if the
        callee might be the fenced reader on any binding the scope
        makes, the argument rule applies. Asked exclusively, a callee
        with a second possible origin named the fenced API on neither
        answer and the call went unchecked; asked from the walk's own
        view, a callee named above its binding did the same (review
        item P1-R6-F4).
        """
        parts = _chain_parts(node.func)
        if parts is None:
            return
        for dotted in self._trust_resolve(parts):
            if dotted not in _FENCED_APIS:
                continue
            if not node.args or isinstance(node.args[0], ast.Starred):
                self._flag(node, _fenced_argument_message(dotted))
                return
            if self._trust_origins(node.args[0]) != {_LOCALPATH}:
                self._flag(node, _fenced_argument_message(dotted))
            return

    def _check_type_parameters(self, node: ast.AST) -> None:
        """Refuse a PEP 695 type-parameter list.

        `def name[T](...)`, `class Name[T]:` and `type X[T] = ...` bind
        T in a lazily evaluated scope of its own, wrapped around the
        definition. The name lives in a plain string field there, so no
        store is recorded, and inside the body T wins over anything of
        the same name from the module -- `def fetch[Path](...)` makes
        every `Path` in the body the type parameter, not the import.
        This audit does not model that scope, so it refuses the form
        instead of reading the body under a binding it cannot see
        (review item P1-R6-F4).
        """
        if getattr(node, "type_params", ()):
            self._flag(node, _type_parameter_message())

    def visit_TypeAlias(self, node: ast.AST) -> None:
        """Refuse `type X = ...`: its right-hand side is evaluated
        lazily, on first use, in a scope of its own (review item
        P1-R6-F4)."""
        self._flag(node, _type_alias_message())
        self._check_type_parameters(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._flag(node, _scope_escape_message("global"))

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self._flag(node, _scope_escape_message("nonlocal"))

    def visit_Call(self, node: ast.Call) -> None:
        self._check_fenced_call(node)
        # A CLOSED GRAMMAR for call targets (review item P1-R3-F7). A
        # call target is either a bare name or a pure dotted chain, and
        # nothing else. Every other shape -- a conditional expression, a
        # boolean expression, a walrus, a starred or awaited value, a
        # comparison -- is a target this audit cannot resolve, and each
        # of those forms was found invoking a caller-supplied callback
        # through a receiver whose identity the slot rules then could not
        # see. Rejecting the shape outright is the only version of this
        # rule that does not need a new case for every syntax Python
        # gains.
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            self._flag(
                node,
                "calls a target written in a form this audit does not "
                "resolve. A call must name its function directly -- a "
                "plain name, or a dotted path -- so that reading the "
                "source shows what runs. Conditional, boolean, "
                "assignment and unpacking expressions in the function "
                "position hide the receiver, and with it the rules "
                "about what may be handed to it.",
            )
            self.generic_visit(node)
            return
        if isinstance(node.func, ast.Attribute) and not isinstance(
            node.func.value,
            (
                ast.Name,
                ast.Attribute,
                ast.Call,
                ast.Constant,
                ast.Subscript,
                ast.JoinedStr,
            ),
        ):
            self._flag(
                node,
                "calls a method on a value written in a form this audit "
                "does not resolve (a conditional, boolean, assignment "
                "or unpacking expression). The receiver decides which "
                "rules apply to the call, so it must be written as a "
                "name, a dotted path, or a call whose target this audit "
                "can read.",
            )
            self.generic_visit(node)
            return
        if isinstance(node.func, (ast.Subscript, ast.Call)):
            self._flag(
                node,
                "calls a target that is computed while the program "
                "runs (the result of a lookup or of another call), so "
                "this audit cannot tell what would run. Call the "
                "function by its direct dotted name.",
            )
        elif isinstance(node.func, ast.Name):
            self._check_call_target(node, node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self._check_method_call(node)
        self._check_callable_arguments(node)
        self._check_callback_slots(node)
        self.generic_visit(node)

    def _check_call_target(self, node: ast.Call, name: str) -> None:
        """Reject a bare-name call unless EVERY possible origin of the
        name is something this audit can check (plan D6.2: callback
        parameters are banned in Phase 0 source). The unknown member is
        never discarded, so a name that might still hold an untraced
        value is rejected even when another branch rebound it to an
        allowed API. Traced origins are checked where the name is read.
        """
        # Accepting this call GRANTS something, so both halves of the
        # decision read the position-blind view: whether the name is
        # bound in this scope at all, and which origins it may hold.
        # Asking the walk's own view whether the name was bound YET let
        # a call above every binding of a shadowing name fall through to
        # the built-in branch below -- the built-in is what Python runs
        # only if no binding of that name exists anywhere in the scope,
        # which is a scope-wide question and never a positional one
        # (review item P1-R6-F4).
        bound = self._trust_lookup(name)
        if bound is None:
            if (
                name in _ALLOWED_CALL_BUILTINS
                or name in _BANNED_BUILTINS
                or name in _FORBIDDEN_MODULES
                or name in _ENTRY_POINT_TOKENS
                or _is_dunder(name)
            ):
                # Either an accepted builtin, or already flagged by the
                # name checks that run on the same node.
                return
            self._flag(node, _unknown_call_message(name))
            return
        for kind, _origin in bound:
            if kind not in ("def", "module", "api"):
                self._flag(node, _unknown_call_message(name))
                return

    def _check_method_call(self, node: ast.Call) -> None:
        """Apply the two-case method-call policy from the module
        docstring: api-instances accept any method (with the
        callable-accepting ones enumerated as slots); values this
        audit reads as plain built-in constants -- a literal, or a
        parameter behind the exact isinstance type gate -- accept
        only the enumerated str data methods, and then only with
        literal or fully resolved known-safe arguments. EVERY other
        receiver is rejected: there are no method calls on untraced
        values. The type gate raises confidence that a receiver is a
        string; it does not settle that the receiver is a built-in
        str, so an accepted call target is resolved under this
        enumerated policy rather than shown to be exact (the
        best-effort scope ratified as D6 Amendment A3, whose residual
        is caller-supplied code -- see the module docstring).
        Module and api-rooted chains are checked by the dotted-path
        policy in visit_Attribute."""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        method = func.attr
        receiver = self._trust_origins(func.value)
        kinds = {kind for kind, _origin in receiver}
        if kinds <= {"module", "api", "instance", "localpath"}:
            for kind, origin in sorted(receiver):
                if kind != "instance":
                    continue
                library = origin.partition(".")[0]
                if library not in _RESTRICTED_INSTANCE_METHODS:
                    continue
                if method in _RESTRICTED_INSTANCE_METHODS[library]:
                    continue
                self._flag(node, _restricted_instance_message(method, library))
                return
            return
        if not kinds <= {
            "module",
            "api",
            "instance",
            "localpath",
            "literal",
            "str",
        }:
            self._flag(node, _unknown_method_message(method))
            return
        if method not in _STR_METHODS:
            self._flag(node, _str_method_message(method))
            return
        # An enumerated str data method on an accepted string receiver:
        # every argument must be a plain literal or a value this audit
        # fully resolved as safe -- no unknowns, no callables.
        # str.format invokes the formatting protocol of what it is
        # handed.
        values = list(node.args) + [keyword.value for keyword in node.keywords]
        for value in values:
            inner = value.value if isinstance(value, ast.Starred) else value
            if isinstance(inner, ast.Constant):
                continue
            origins = self._trust_origins(inner)
            if all(kind in _SAFE_DATA_ARGUMENT_KINDS for kind, _origin in origins):
                continue
            self._flag(node, _unknown_method_argument_message(method))

    def _callee_is_first_party(self, func: ast.AST) -> bool:
        """True when every possible call target is defined in the
        scanned tree (a scanned def/class or a first-party module
        member)."""
        if isinstance(func, ast.Name):
            # True here GRANTS -- it lets a callable be handed over
            # unquestioned -- so the whole decision reads the
            # position-blind view and nothing else. A second, positional
            # test for "is the name bound yet" used to stand in front of
            # this one; it is gone (review item P1-R6-F4).
            bound = self._trust_lookup(func.id)
            if not bound:
                return False
            for kind, origin in bound:
                if kind == "def":
                    continue
                if kind in ("module", "api") and (
                    origin == _FIRST_PARTY_ROOT
                    or origin.startswith(_FIRST_PARTY_ROOT + ".")
                ):
                    continue
                return False
            return True
        if isinstance(func, ast.Attribute):
            parts = _chain_parts(func)
            if parts is None:
                return False
            candidates = self._resolve_exclusively(parts)
            if not candidates:
                return False
            for dotted in candidates:
                if dotted != _FIRST_PARTY_ROOT and not dotted.startswith(
                    _FIRST_PARTY_ROOT + "."
                ):
                    return False
            return True
        return False

    def _check_callable_arguments(self, node: ast.Call) -> None:
        """Reject a function or lambda passed as an argument to a
        callee that is not defined in the scanned tree. Outside code
        could keep the callable and run it at any time; a scanned
        callee is fine because every call site inside it is scanned
        under the same rules."""
        if self._callee_is_first_party(node.func):
            return
        values = list(node.args) + [keyword.value for keyword in node.keywords]
        for value in values:
            inner = value.value if isinstance(value, ast.Starred) else value
            if isinstance(inner, ast.Lambda):
                self._flag(node, _callable_argument_message("a lambda function"))
            elif isinstance(inner, ast.Name):
                bound = self._lookup(inner.id)
                if bound and any(kind == "def" for kind, _origin in bound):
                    self._flag(
                        node,
                        _callable_argument_message(
                            "the function '" + inner.id + "'"
                        ),
                    )

    def _callee_slot_identities(self, node: ast.Call) -> "set[str]":
        """The call target's possible identities for the callback-slot
        table: a bare accepted built-in name, an allowlist-traced
        dotted API, or an api-instance method (the producing API's
        dotted path plus the method name).

        An identity MISSING from this set silently skips the slot rules
        for that callee, which is a grant of silence, so the whole set
        is drawn from the position-blind view: every binding the scope
        makes, wherever it stands. Read from the walk's own view, a
        callee named above the binding that gives it its identity
        carried no identity at all and its callable-accepting slots
        went unchecked (review item P1-R6-F4).
        """
        func = node.func
        identities: set[str] = set()
        if isinstance(func, ast.Name):
            bound = self._trust_lookup(func.id)
            if bound is None:
                if func.id in _ALLOWED_CALL_BUILTINS:
                    identities.add(func.id)
            else:
                for kind, origin in bound:
                    if kind == "api":
                        identities.add(origin)
        elif isinstance(func, ast.Attribute):
            parts = _chain_parts(func)
            if parts is not None:
                identities.update(self._trust_resolve(parts))
                for kind, origin in self._trust_origins(func.value):
                    if kind == "instance":
                        identities.add(origin + "." + func.attr)
                    elif kind == "localpath":
                        # A validated path is a pathlib.Path. The
                        # fence repair must not cost Path its slot
                        # rules (review item P1-R2-F10).
                        identities.add("pathlib.Path." + func.attr)
        return identities

    def _callback_slot_ok(self, value: ast.AST) -> bool:
        """True when a value placed in a callback slot is cleared: a
        plain literal, an unshadowed accepted built-in named directly
        (str, int, ...), or a directly named non-first-party
        allowlisted API. Everything else -- a caller-supplied
        parameter above all -- would run outside scanned control."""
        if isinstance(value, ast.Constant):
            return True
        if isinstance(value, ast.Name) and self._trust_lookup(value.id) is None:
            return value.id in _ALLOWED_CALL_BUILTINS
        for kind, origin in self._trust_origins(value):
            if kind != "api":
                return False
            top = origin.partition(".")[0]
            if top == "builtins" or top == _FIRST_PARTY_ROOT:
                return False
            if self._policy_for(origin, False) is not None:
                return False
        return True

    def _slot_flagged_elsewhere(self, value: ast.AST) -> bool:
        """True when the any-position callable-argument rule already
        rejects this slot value (a lambda, or a name bound to a
        scanned def), so a second message would only repeat it."""
        if isinstance(value, ast.Lambda):
            return True
        if isinstance(value, ast.Name):
            bound = self._lookup(value.id)
            if bound and any(kind == "def" for kind, _origin in bound):
                return True
        return False

    def _check_callback_slots(self, node: ast.Call) -> None:
        """Reject an untraceable value in a callable-accepting slot of
        an allowed external API (the enumerated _CALLBACK_SLOTS table).
        The API would invoke whatever sits there, so an unknown or
        parameter-derived value in such a slot is a call target this
        audit cannot see."""
        keyword_slots: set[str] = set()
        positional_slots: dict[int, str] = {}
        names: list[str] = []
        for identity in sorted(self._callee_slot_identities(node)):
            slots = _CALLBACK_SLOTS.get(identity)
            if slots is None:
                continue
            if identity == "iter" and len(node.args) < 2:
                # One-argument iter takes plain data; only the
                # two-argument form calls its first argument.
                continue
            names.append("'" + identity + "'")
            keyword_slots |= slots[0]
            positional_slots.update(slots[1])
        if not names:
            return
        callee = " or ".join(names)
        for keyword in node.keywords:
            if keyword.arg is None:
                if keyword_slots:
                    self._flag(node, _unpacked_slot_message(callee, "**"))
                continue
            if (
                keyword.arg in keyword_slots
                and not self._slot_flagged_elsewhere(keyword.value)
                and not self._callback_slot_ok(keyword.value)
            ):
                self._flag(node, _callback_slot_message(callee, keyword.arg))
        for index, argument in enumerate(node.args):
            if isinstance(argument, ast.Starred):
                if positional_slots:
                    self._flag(node, _unpacked_slot_message(callee, "*"))
                continue
            slot = positional_slots.get(index)
            if slot is None or self._slot_flagged_elsewhere(argument):
                continue
            if not self._callback_slot_ok(argument):
                self._flag(node, _callback_slot_message(callee, slot))

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        # `case path:` and `case X() as path:` bind `path`. The name is a
        # plain string field here, not a Name node, so no ordinary store
        # was ever recorded and the captured value inherited the old
        # origin -- which let a data frame be captured under a name that
        # still looked like a validated path (review item P1-R5-F1).
        if node.name is not None:
            self._bind(node.name, None)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self._bind(node.name, None)
        self.generic_visit(node)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self._bind(node.rest, None)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        parts = _chain_parts(node.value)
        candidates = self._resolve(parts) if parts else []
        if "os.environ" in candidates and isinstance(
            node.ctx, (ast.Store, ast.Del)
        ):
            self._flag(
                node,
                "changes os.environ. The allowlist permits reading "
                "environment variables only; remove the write.",
            )
        self.generic_visit(node)

    # -- statements that bind names ----------------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._check_name(target, target.id)
                if target.id in _ALLOWED_CALL_BUILTINS:
                    self._flag(target, _builtin_shadow_message(target.id))
                self._bind_from_value(target.id, node.value)
            else:
                self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self._check_name(node.target, node.target.id)
            if node.target.id in _ALLOWED_CALL_BUILTINS:
                self._flag(node.target, _builtin_shadow_message(node.target.id))
            if node.value is not None:
                self._bind_from_value(node.target.id, node.value)
            else:
                self._bind(node.target.id, None)
        else:
            self.visit(node.target)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        self.visit(node.target)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        """`name := value` binds like any other store -- the value is
        left untraced, exactly as an ordinary Name store leaves it --
        but inside a comprehension it binds in the scope AROUND the
        comprehension, not in the comprehension's own scope. Recording
        it in the comprehension scope would have hidden the rebinding
        from the surrounding code, which would go on trusting the origin
        the name held before (review item P1-R6-F4)."""
        self.visit(node.value)
        target = node.target
        if isinstance(target, ast.Name):
            self._check_name(target, target.id)
            if target.id in _ALLOWED_CALL_BUILTINS:
                self._flag(target, _builtin_shadow_message(target.id))
            self._bind(target.id, None, scope=self._walrus_scope())
        else:
            self.visit(target)

    # -- scopes ------------------------------------------------------

    def visit_Module(self, node: ast.Module) -> None:
        self._collect_scope_bindings(node.body)
        self._build_trust_scope(list(node.body), None)
        self._walk_scope_body(node.body)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_function(node)

    def _handle_function(self, node: "ast.FunctionDef | ast.AsyncFunctionDef") -> None:
        """Check everything a def statement does WHERE IT STANDS, and
        postpone the body, which runs later (review item P1-R6-F4)."""
        self._check_name(node, node.name)
        if node.name in _ALLOWED_CALL_BUILTINS:
            self._flag(node, _builtin_shadow_message(node.name))
        self._check_type_parameters(node)
        for decorator in node.decorator_list:
            self.visit(decorator)
        args = node.args
        for default in list(args.defaults) + [
            d for d in args.kw_defaults if d is not None
        ]:
            self.visit(default)
        for arg in _parameters_of(args):
            if arg.arg in _ALLOWED_CALL_BUILTINS:
                self._flag(arg, _builtin_shadow_message(arg.arg))
            if arg.annotation is not None:
                self.visit(arg.annotation)
        if node.returns is not None:
            self.visit(node.returns)
        self._bind_definition(node)
        self._defer_body(node)

    def _read_function_body(
        self, node: "ast.FunctionDef | ast.AsyncFunctionDef"
    ) -> None:
        all_args = _parameters_of(node.args)
        # Parameters hold caller-supplied values: the explicit unknown
        # member, never discarded when other origins join.
        self._enter_scope({arg.arg: {_UNKNOWN} for arg in all_args}, False, False)
        self._collect_scope_bindings(node.body)
        self._upgrade_gated_parameters(node.body)
        self._build_trust_scope(list(node.body), node.body)
        self._walk_scope_body(node.body)
        self._leave_scope()

    def _upgrade_gated_parameters(self, body: "list[ast.stmt]") -> None:
        """Upgrade parameters checked as str by a leading type gate.

        Recognizes the exact shape 'if not isinstance(name, str):
        raise ...' (no else branch), or the equivalent positive branch
        'if isinstance(name, str): ... else: raise ...', appearing
        before any other statement (the docstring and further gate
        statements may precede it). The raise makes everything after
        the gate unreachable unless the parameter is a str instance,
        so replacing the parameter's pristine unknown origin with the
        checked-str origin is warranted -- and it is the ONE
        sanctioned narrowing in this otherwise accumulate-only origin
        lattice. isinstance also passes for a str subclass, so the
        upgrade raises confidence in the value rather than settling
        that it is a built-in str; the module docstring records that
        as the best-effort scope ratified as D6 Amendment A3.
        The upgrade never applies when the gate could mean something
        else: a binding of 'isinstance' or 'str' in any scope blocks
        it (and such a binding is a violation in its own right), and a
        parameter already carrying other origins is left alone.
        """
        index = 0
        if body:
            head = body[0]
            if isinstance(head, ast.Expr) and isinstance(head.value, ast.Constant):
                index = 1
        scope = self.scopes[-1]
        while index < len(body):
            name = self._gated_parameter(body[index])
            if name is None:
                return
            slot = scope.get(name)
            if slot == {_UNKNOWN}:
                scope[name] = {("str", "")}
            index += 1

    def _gated_parameter(self, stmt: ast.stmt) -> "str | None":
        """The parameter name a statement checks as str, or None.

        Matches exactly 'if not isinstance(name, str): raise ...'
        (with no else branch), or 'if isinstance(name, str): ...
        else: raise ...'.
        """
        if not isinstance(stmt, ast.If):
            return None
        test = stmt.test
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if stmt.orelse:
                return None
            if len(stmt.body) != 1 or not isinstance(stmt.body[0], ast.Raise):
                return None
            return self._isinstance_str_target(test.operand)
        if len(stmt.orelse) == 1 and isinstance(stmt.orelse[0], ast.Raise):
            return self._isinstance_str_target(test)
        return None

    def _isinstance_str_target(self, test: ast.AST) -> "str | None":
        """The name checked by a genuine 'isinstance(name, str)' call,
        or None. The call must reach the real built-ins: a binding of
        'isinstance' or 'str' in any scope blocks recognition (Python
        would not run the built-in there either)."""
        if not isinstance(test, ast.Call) or test.keywords or len(test.args) != 2:
            return None
        func = test.func
        if not isinstance(func, ast.Name) or func.id != "isinstance":
            return None
        if (
            self._trust_lookup("isinstance") is not None
            or self._trust_lookup("str") is not None
        ):
            return None
        target, type_name = test.args
        if not isinstance(target, ast.Name):
            return None
        if not isinstance(type_name, ast.Name) or type_name.id != "str":
            return None
        return target.id

    def visit_Lambda(self, node: ast.Lambda) -> None:
        args = node.args
        for default in list(args.defaults) + [
            d for d in args.kw_defaults if d is not None
        ]:
            self.visit(default)
        for arg in _parameters_of(args):
            if arg.arg in _ALLOWED_CALL_BUILTINS:
                self._flag(arg, _builtin_shadow_message(arg.arg))
        # A lambda body runs later too, for the same reason a def body
        # does (review item P1-R6-F4).
        self._defer_body(node)

    def _read_lambda_body(self, node: ast.Lambda) -> None:
        all_args = _parameters_of(node.args)
        self._enter_scope({arg.arg: {_UNKNOWN} for arg in all_args}, False, False)
        self._build_trust_scope([node.body], None)
        mark = len(self.deferred)
        self.visit(node.body)
        # The same ordering step _walk_scope_body performs for a
        # statement body: complete this scope before anything postponed
        # inside it is read.
        self._collect_scope_stores([node.body])
        self._read_deferred_bodies(mark)
        self._leave_scope()

    # -- comprehensions ----------------------------------------------

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._handle_comprehension(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._handle_comprehension(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._handle_comprehension(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._handle_comprehension(node)

    def _handle_comprehension(self, node: _Comprehension) -> None:
        """Read one comprehension where Python would evaluate it.

        The FIRST iterable is the one part evaluated where the
        comprehension stands, in the surrounding scope, so it is read
        here. Everything else belongs to the comprehension's own scope.

        A GENERATOR EXPRESSION is the third form whose body runs later,
        beside a def and a lambda: nothing in it runs until something
        draws from it, which can be long after the surrounding scope has
        finished. Reading it where it stands read the surrounding scope
        half-built, so a name rebound below the expression kept the
        origin it had above it -- the same temporal error the def repair
        closed (review item P1-R6-F4). Its body is therefore postponed.
        A comprehension carrying an `async for` is postponed for the
        same reason. A list, set, or dict comprehension without one is
        evaluated on the spot, so its body is read on the spot.
        """
        if node.generators:
            self.visit(node.generators[0].iter)
        deferred = isinstance(node, ast.GeneratorExp) or any(
            generator.is_async for generator in node.generators
        )
        if deferred:
            self._defer_body(node)
        else:
            self._read_comprehension_body(node)

    def _read_comprehension_body(self, node: _Comprehension) -> None:
        """Read a comprehension's body in a scope of its own.

        A comprehension is its own scope in Python 3 and its iteration
        variables live only inside it. Two things follow, and neither
        held before: a target name SHADOWS the surrounding name for
        everything inside the comprehension, so `[Path(v) for Path in
        items]` calls whatever `items` yields rather than the imported
        `Path` and every target starts as the unknown member; and the
        binding does not leak out, so the surrounding scope keeps the
        name it had. The first iterable was already read in the
        surrounding scope by the caller.
        """
        locals_: dict[str, set[tuple[str, str]]] = {}
        for generator in node.generators:
            for name in self._comprehension_target_names(generator.target):
                locals_[name] = {_UNKNOWN}
        self._enter_scope(locals_, False, True)
        self._build_trust_scope(self._comprehension_parts(node), None)
        mark = len(self.deferred)
        for index, generator in enumerate(node.generators):
            self.visit(generator.target)
            if index:
                self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        # The same ordering step _walk_scope_body performs: complete the
        # bindings before anything postponed inside is read. A
        # comprehension binds only its targets, which were bound above;
        # a walrus written inside it lands in the scope around it, where
        # this records it a second time and harmlessly.
        self._collect_comprehension_stores(node)
        self._read_deferred_bodies(mark)
        self._leave_scope()

    def _comprehension_parts(self, node: _Comprehension) -> "list[ast.AST]":
        """The expressions a comprehension evaluates inside its own
        scope: every iterable but the first, every condition, and the
        element (or the key and value of a dict comprehension). The
        first iterable belongs to the surrounding scope."""
        parts: list[ast.AST] = []
        for index, generator in enumerate(node.generators):
            if index:
                parts.append(generator.iter)
            parts.extend(generator.ifs)
        if isinstance(node, ast.DictComp):
            parts.append(node.key)
            parts.append(node.value)
        else:
            parts.append(node.elt)
        return parts

    def _comprehension_target_names(self, target: ast.AST) -> "list[str]":
        """Every plain name a comprehension target binds.

        A target that is not a plain name or a nesting of tuples, lists,
        and starred names -- `for obj.field in items`, `for row[0] in
        items` -- stores into an object that outlives the comprehension,
        at a moment this audit cannot place. It is refused rather than
        read (review item P1-R6-F4).
        """
        names: list[str] = []
        stack: list[ast.AST] = [target]
        while stack:
            current = stack.pop()
            if isinstance(current, ast.Name):
                names.append(current.id)
            elif isinstance(current, ast.Starred):
                stack.append(current.value)
            elif isinstance(current, (ast.Tuple, ast.List)):
                stack.extend(current.elts)
            else:
                self._flag(current, _comprehension_target_message())
        return names

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            if node.name in _ALLOWED_CALL_BUILTINS:
                self._flag(node, _builtin_shadow_message(node.name))
            # `except OSError as error:` BINDS `error` (and unbinds it
            # again at the end of the handler). The name lives in a
            # plain string field here, not in a Name node, so no
            # ordinary store was ever recorded and a name that had held
            # an allowlisted API went on looking like one -- the same
            # omission the match-capture repair closed in round 5.
            self._bind(node.name, None)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_name(node, node.name)
        if node.name in _ALLOWED_CALL_BUILTINS:
            self._flag(node, _builtin_shadow_message(node.name))
        self._check_type_parameters(node)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        self._bind_definition(node)
        self._enter_scope({}, True, False)
        self._collect_scope_bindings(node.body)
        self._build_trust_scope(list(node.body), None)
        # A class body RUNS while the class is being built, so its
        # statements are read here and now. The method bodies written
        # inside it run later still and stay on the postponed list, to
        # be read once the surrounding module or function has finished
        # (review item P1-R6-F4).
        for statement in node.body:
            self.visit(statement)
        # The class scope is then completed, before the surrounding
        # scope reads those postponed bodies -- the same ordering step
        # _walk_scope_body performs, done here because a class body's
        # statements are walked here rather than there.
        self._collect_scope_stores(list(node.body))
        self._leave_scope()


def scan_source(
    source_text: str,
    module_exports: "dict[str, tuple[set[str], set[str], set[str]]] | None" = None,
    first_party_modules: "set[str] | None" = None,
) -> "list[tuple[int, str]]":
    """Scan one module's source text. Returns (line, message) pairs.

    ``module_exports`` and ``first_party_modules`` carry the per-module
    export records for the surrounding scanned tree (see scan_files);
    without them, first-party `from` imports fall back to rejecting
    known module names only.
    """
    try:
        tree = ast.parse(source_text)
    except SyntaxError as error:
        line = error.lineno if error.lineno else 1
        detail = error.msg if error.msg else "invalid syntax"
        return [
            (
                line,
                "could not be parsed as Python (" + detail + "). Fix "
                "the syntax so the file can be audited.",
            )
        ]
    checker = _Checker(module_exports, first_party_modules)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            checker.call_targets.add(id(node.func))
    checker.visit(tree)
    return sorted(checker.violations)


def _python_files(root: pathlib.Path) -> "list[pathlib.Path]":
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.py"))


def scan_files(files: "list[pathlib.Path]") -> "list[str]":
    """Scan the given files. Returns formatted 'file:line: message'
    violation lines (empty list = clean).

    Before any file is judged, every first-party module in the batch is
    parsed and its top-level names are recorded, so that first-party
    `from` imports and one-step attribute references can be verified
    against what the named sibling module really defines.
    """
    lines: list[str] = []
    texts: dict[pathlib.Path, str] = {}
    module_exports: dict[str, tuple[set[str], set[str], set[str]]] = {}
    first_party_modules: set[str] = set()
    for path in files:
        try:
            texts[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.append(
                str(path) + ":1: could not be decoded as UTF-8 text. "
                "Source files must be plain UTF-8; re-save the file "
                "with UTF-8 encoding."
            )
            continue
        module_name = _first_party_module_name(path)
        if module_name is None:
            continue
        try:
            tree = ast.parse(texts[path])
        except SyntaxError:
            # scan_source reports the parse failure for this file below.
            continue
        module_exports[module_name] = _module_bindings(tree)
        pieces = module_name.split(".")
        for length in range(1, len(pieces) + 1):
            first_party_modules.add(".".join(pieces[:length]))
    for path in files:
        if path not in texts:
            continue
        for lineno, message in scan_source(
            texts[path], module_exports, first_party_modules
        ):
            lines.append(str(path) + ":" + str(lineno) + ": " + message)
    return lines


def scan_tree(root: "pathlib.Path | str") -> "list[str]":
    """Scan every .py file under root (or a single .py file)."""
    return scan_files(_python_files(pathlib.Path(root)))


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scan_imports",
        description=(
            "Check a Python source tree against synthtwin's offline "
            "allowlist (plan D6.2) without running any of it. Prints "
            "one line per violation and exits 1 if any were found, 0 "
            "when the tree is clean."
        ),
    )
    parser.add_argument(
        "source",
        help=(
            "folder that holds the Python source to audit (for "
            "synthtwin CI this is src/), or a single .py file"
        ),
    )
    args = parser.parse_args(argv)

    root = pathlib.Path(args.source)
    if not root.exists():
        parser.error(
            "the path '" + args.source + "' does not exist. Give the "
            "folder that holds the Python source to audit, for "
            "example src/."
        )
    files = _python_files(root)
    if not files:
        parser.error(
            "no Python files were found under '" + args.source + "'. "
            "Check that you gave the right folder; an empty scan "
            "proves nothing."
        )

    violations = scan_files(files)
    for line in violations:
        print(line)
    print(
        "scan_imports: checked "
        + str(len(files))
        + " Python file(s) under '"
        + str(root)
        + "': "
        + str(len(violations))
        + " violation(s)."
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
