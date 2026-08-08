# Phase 1 combined plan-and-code review — round 3

**Reviewed baseline:** the staged Phase 1 tree above
002bca35ce1562e1afe39b4d9987fa617a04ee38, including the amended Phase 1
plan, both prior review/response pairs, all product and test code, scanner
changes, workflows, dependency inputs and locks, and public documentation.

**Item count:** 9 — 6 blockers and 3 majors. Previously admitted-open items
are listed separately and are not counted again.

**Verdict: reject.** New blocking items: P1-R3-F1 through P1-R3-F6. The
previously admitted-open blocking items remain P1-R2-F4, P1-R2-F5,
P1-R1-F4, P1-R1-F5, P1-R1-F7, P1-R1-F8, P1-R1-F9, and the remainder of
P1-R1-F10; R1-X3 remains part of the P1-R1-F4 failure family.

The minimum-version repair is the one claimed round-2 repair that held under
this round's attacks. Most of the others fix the exact previous mutation but
leave the same control dependent on a neighboring syntax or state. Four clean
scanner mutations still hand a URL to the fenced reader, two still reach a
real pandas writer, out-of-range and signed-accounting columns still take
silently wrong roles, two absent output aliases collapse into one successful
write, and the institutional procedure hash-checks every dependency except the
project wheel it executes.

These are control and behavior defects. The stale dependency wording isolated
near the end is cosmetic by itself and does not contribute to the verdict.

## Disposition of the ten claimed repairs

| Claimed repair | Round-3 disposition |
| --- | --- |
| P1-R2-F1 | **Fails.** The exact module-level validator-shadow test is red, but class lookup, pattern capture, and a shadowed Path wrapper still manufacture or misapply locality provenance (P1-R3-F1). |
| P1-R2-F2 | **Fails.** Official cast forms and direct subscripts retain pandas, but a shadowed cast and a pattern capture still launder the frame to a writer (P1-R3-F2). |
| P1-R2-F3 | **Fails.** Mixed columns can publish n_out_of_range, but all-out-of-range input and neighboring routing/sentinel decisions still contradict the structured outcome (P1-R3-F3). |
| P1-R2-F6 | **Fails as an end-to-end repair.** The parser no longer reverses the sign, but the original debt column silently becomes an identifier with no warning or statistics (P1-R3-F4). |
| P1-R2-F7 | **Fails.** Existing hard links and special nodes are refused, but two names resolving to the same absent target are treated as different, and identity errors fail open (P1-R3-F5). |
| P1-R2-F8 | **Holds under the attacks performed.** The declared pandas floor agrees across metadata, minimum input, and minimum lock, and CI proves the installed version before pytest. |
| P1-R2-F9 | **Fails.** The locked machine uses no index and dependency hashes, but the project wheel is not hash-bound and the documented two-machine bundle is not target-complete (P1-R3-F6). |
| P1-R2-F10 | **Fails outside the one direct syntax tested.** A direct validated.walk call is red; equivalent computed Path receivers lose the callback-slot identity (P1-R3-F7). |
| P1-R2-F12 | **Partly holds, overall fails.** Source imports no numpy and the math surface is closed, but the institutional input still names numpy as a root (P1-R3-F8). |
| P1-R2-F14 | **Fails.** C0/C1 characters are escaped in the normal summary, but raw table text still reaches error output and Unicode display controls survive the escaping function (P1-R3-F9). |

## Blocking items

### P1-R3-F1 — Blocker — the fenced-reader provenance is still forgeable and scope-confused

**Location:** docs/plans/phase-1-profiler.md:124-140;
tools/offline_scan/scan_imports.py:1242-1292, 1451-1480, 1847-1853,
1950-1963, 2289-2330, 2429-2444; tests/test_offline_scan.py:1383-1421.

The new bare-name check and the validator-specific shadow check are real, but
the underlying resolution model is still not the rule the plan states.
Resolution keeps module/API origins while dropping simultaneous definition or
unknown origins; methods inherit the class scope in the scanner even though
Python does not use that scope for an unqualified name; the local-path marker
carries no producing-function identity; and the Path-wrapper branch does not
apply the validator branch's ambiguity check. Pattern captures are not bound
at all.

**Concrete failure scenario 1:** bare-import pandas.read_csv at module scope.
Inside a class, define a method also named read_csv, then have another method
call the unqualified name with a URL. The scanner resolves the class
definition and reports zero violations. Python skips the class namespace for
that unqualified lookup and calls the module-global pandas reader. The runtime
probe recorded:

    violations []
    reader_argument ['https://example.invalid/table.csv']

This directly defeats the repair that says a bare fenced reference is
covered.

**Concrete failure scenario 2:** import pathlib.Path as a bare name, then
redefine Path in the same module as a function returning a URL. Pass a genuine
validate_local_path result through that name and into pandas.read_csv. The
Path branch sees only the surviving pathlib API origin, mints the local-path
marker, and the scan is green; Python runs the local definition and hands its
URL to the reader. Class-scope/local-global disagreement and a match capture
of validate_local_path produced the same zero-violation URL handoff.

**Required repair:** make the provenance token carry the producing function
and require the consumer to be that function; model Python method lookup
without treating a class namespace as a closure; bind every pattern capture
conservatively; reject bare fenced calls as the plan currently requires; and
mint provenance only when every possible binding of both validator and
wrapper is the exact canonical API. Retain all four clean mutations as red
tests.

### P1-R3-F2 — Blocker — cast and pattern bindings still launder restricted objects

**Location:** tools/offline_scan/scan_imports.py:1255-1292, 1389-1421,
1516-1540, 1989-2050, 2255-2266, 2429-2444;
tests/test_offline_scan.py:1320-1340, 1423-1443.

The official positional, all-keyword, and mixed call forms of typing.cast now
carry the second argument's origins. The recognition of the function itself
is not honest: it uses the same dotted resolver that discards a simultaneous
definition. Pattern bindings remain absent from the binding model.

**Concrete failure scenario 1:** import cast from typing, then define a local
cast(typ, val) that returns typ. Read a frame through the fenced reader and
call the shadowed function with the frame first and a harmless Path second.
The scanner treats it as typing.cast and carries the Path origin; Python
returns the frame. Calling to_csv on the result scanned clean and wrote:

    ,secret
    0,3
    1,4

**Concrete failure scenario 2:** bind a module-global name to a Path, then use
that name as a match capture for the frame returned by read_csv. The scanner
keeps the old Path origin because it never records the capture; Python binds
the frame. frame.to_csv scanned clean and wrote a real CSV.

These are not exotic unsupported cast forms. They are ordinary Python name
bindings around the exact preservation rule the repair added.

**Required repair:** recognize value-preserving APIs only when every possible
binding is the canonical API; an ambiguous, shadowed, class-inherited, or
unknown binding must produce unknown. Implement conservative binding for all
match patterns and test it with real writer execution. More generally, the
origin lattice must model Python name semantics before another syntax-specific
origin is treated as a security token.

### P1-R3-F3 — Blocker — out-of-range values still have no single routing outcome

**Location:** docs/plans/phase-1-profiler.md:551-556;
src/synthtwin/parsing.py:259-340; src/synthtwin/taxonomy.py:560-595,
649-653, 836-899.

The parser now distinguishes an out-of-range spelling when asked, and a mixed
numeric column can carry n_out_of_range. Taxonomy nevertheless maintains
parallel lists and consults them differently. The sentinel gate uses only
representable numbers, the numeric guard uses representable plus out-of-range,
the final branch additionally requires at least one representable number, and
sign/integer facts come only from representable values.

**Concrete failure scenario 1:** profile 100 distinct values from 1e999
through 100e999. Every cell is recognized by number_out_of_range, but the CLI
exits zero with role free_text, no n_out_of_range, no numeric evidence, and no
remark. A repeated three-value form becomes categorical and publishes the
three numeric spellings as labels. Both contradict the plan's promise that
such a column is still described as numbers.

**Concrete failure scenario 2:** profile values 1 through 99 plus -1e999.
The result is role count with n_out_of_range 1 and n_negative 0. The profile
therefore says the column contains whole nonnegative counts even though its
hundredth numeric value is visibly negative.

**Concrete failure scenario 3:** profile values 1 through 197, two -999
values, and three out-of-range values. There are 202 present cells. The three
range failures lower the representable count below the sentinel-normalization
gate, so the two -999 values are never judged. The CLI exits zero with
n_missing 0, minimum -999, mean 87.96482412060301, and skew about -6.83. The
repair that excludes out-of-range values from one straggler budget has moved
them into the gate that decides whether real sentinels distort the statistics.

**Required repair:** classify each present cell once as representable numeric,
out-of-range numeric, contradictory numeric, or nonnumeric and carry that
structured result through every gate. Use one numeric population definition
for routing and sentinel evaluation; retain sign/integer evidence where it is
decidable; and define an explicit refusal or limited numeric profile when no
statistic can be represented. Add all-out-of-range, negative-range, and
sentinel-boundary end-to-end tests.

### P1-R3-F4 — Blocker — signed accounting input is no longer reversed, but is silently misrouted

**Location:** src/synthtwin/parsing.py:259-340;
src/synthtwin/taxonomy.py:649-732, 836-899; tests/test_parsing.py:38-62.

Returning None from parse_number stops the old sign reversal but makes the
contradictory notation indistinguishable from ordinary words. The automatic
taxonomy is then free to call it an identifier, constant, category, or free
text. That is not a visible refusal and does not preserve the column's
distribution.

**Concrete failure scenario:** run the original debt-shaped input, 100
distinct cells written as (-1) through (-100). The CLI exits zero. The column
is now role identifier, with no numeric fields and no remark explaining that
every value looked like contradictory accounting notation. The old positive
mean is gone, but the entire negative distribution is now silently discarded.

**Required repair:** give contradictory accounting syntax its own parse
outcome. Refuse the column with actionable wording, or visibly decline the
values before any ordinary identifier/free-text routing; do not turn a
numeric-looking error into generic text. Add the round-2 requested
end-to-end matrix, not only direct parser assertions.

### P1-R3-F5 — Blocker — filesystem identity still fails open for absent aliases and metadata errors

**Location:** src/synthtwin/profile.py:190-224, 242-275, 278-322;
src/synthtwin/cli.py:211-230.

Existing ordinary files are compared with Path.samefile, and existing special
nodes are refused. is_the_same_file returns false whenever either path is
absent and also converts every samefile OSError into “different.”
write_both_files has no equality check before that call.

**Concrete failure scenario 1:** on POSIX, create the two default output names
as dangling symbolic links to the same missing target. Local-path validation
resolves both names to the same absent Path. Identity returns false because it
does not exist yet. The CLI exits zero, writes the JSON, then overwrites that
same target with the summary. Both advertised output names lead to summary
text and there is no machine-readable profile.

**Concrete failure scenario 2:** if samefile reports a metadata error while an
output is a hard link to the input, the helper returns false and the CLI
continues. An injected transient error reproduced exit zero and replacement of
the source table with JSON. An identity control protecting irreplaceable input
must refuse when it cannot establish identity, not assume difference.

**Required repair:** reject normalized/resolved path equality regardless of
existence; use filesystem identity in addition when both entries exist; and
fail closed with an actionable error on identity/stat failures. Cover two
dangling aliases, a direct same absent path, every existing hard-link pairing,
and identity-query failure. This is independent of the admitted-open
transaction item P1-R2-F11.

### P1-R3-F6 — Blocker — the institutional installation is neither wholly hash-bound nor a complete two-machine procedure

**Location:** README.md:175-218; .github/workflows/ci.yml:199-218,
593-596, 742-762; requirements-install.lock:7-66, 142-247;
docs/plans/phase-1-profiler.md:23-28.

The dependency closure is installed with hashes and no index on the locked
machine. The next command installs the synthtwin wheel with --no-index and
--no-deps but no expected digest. A wheel's internal RECORD is not an external
integrity binding because a substituted wheel can carry a matching substituted
RECORD. CI prints a digest into one job log but does not publish, transfer, or
verify a governed manifest at installation.

**Concrete failure scenario 1:** replace the project wheel on release storage
or transfer media while leaving the dependency wheelhouse untouched. Every
requirements-install.lock hash passes. The second command installs and
executes the substituted project code because no command compares its bytes
with an expected project digest. The path advertised for a machine that must
install everything by hash omits the one artifact that contains this
project's executable code.

The connected-machine half is also host-specific. pip download resolves for
the connected host unless target platform, ABI, architecture, and Python
version are supplied. The lock itself selects different numpy versions below
3.11, at 3.11, and from 3.12, and different pandas versions below and from
3.11. The instructions say to copy the wheelhouse folder, but the locked
command also needs requirements-install.lock outside that folder.

**Concrete failure scenario 2:** prepare the wheelhouse on macOS/Python 3.13
and copy only that folder to an air-gapped Linux/Python 3.10 machine, exactly
as written. The connected download omits the target's compatible wheels and
the copied bundle omits the lock named by the install command, so installation
cannot complete. CI does not prove the split: acquisition and offline smoke
occur in one Ubuntu job and acquisition uses the development/build lock's
wheelhouse.

The plan also names no release as a Phase 1 deliverable, while the procedure
requires a wheel “from a release.” That makes the currently claimed built path
unavailable even before the two failures above.

**Required repair:** publish a governed project-wheel digest or attestation,
transfer it and the lock with the bundle, and verify the wheel before install.
Define acquisition for the exact target platform/architecture/ABI/Python
combination, name an artifact source that exists in this phase, and have CI
exercise the actual two-machine bundle boundary rather than a same-job
approximation.

## Major items

### P1-R3-F7 — Major — computed call shapes still invoke untraced callbacks

**Location:** tools/offline_scan/scan_imports.py:1971-1987, 2033-2050,
2135-2163, 2197-2240; tests/test_offline_scan.py:1468-1483.

The direct validated.walk(on_error=callback) regression is red. Callback-slot
identity derivation for an attribute receiver is nested under the condition
that the complete attribute is a simple name chain. An equivalent receiver
built by a conditional, Boolean expression, Path wrapping, or typing.cast has
the local-path origin for method acceptance but no pathlib.Path.walk identity
for the slot table. Separately, visit_Call rejects computed Subscript and Call
targets but not conditional, Boolean, or assignment-expression targets.

**Concrete failure scenario 1:** each of these scanned with zero violations:

    (validated if choose else validated).walk(on_error=callback)
    (validated or validated).walk(False, callback)
    pathlib.Path(validated).walk(on_error=callback)
    typing.cast(typ="object", val=validated).walk(on_error=callback)

At runtime, walking a missing path invoked the supplied callback with
FileNotFoundError.

**Concrete failure scenario 2:** the direct call callback("payload") is red,
but each computed equivalent below scans clean and invokes it:

    (callback if choose else print)("payload")
    (callback or print)("payload")
    (runner := callback)("payload")

This remains Major, consistent with the prior treatment of execution supplied
by the caller under the named residual; it is still a false claim about what
the scanner enforces.

**Required repair:** enforce a closed grammar for every call target, rejecting
any form not explicitly audited. Derive receiver-origin slot identities
independently of whether the syntax is a simple dotted chain, and test keyword
and positional callback slots through every accepted value-preserving receiver
form.

### P1-R3-F8 — Major — numpy remains a direct root of the institutional install

**Location:** docs/plans/phase-1-profiler.md:79-91;
requirements-install.in:1-9; requirements-install.lock:63-66, 139-142;
SECURITY.md:162-176; tests/test_dependencies.py:153-167.

The source-level part of the repair holds: src imports no numpy, numpy imports
are red, and math is closed to fsum, frexp, isfinite, ldexp, and sqrt.
pyproject.toml declares pandas alone. requirements-install.in nevertheless
names pandas and numpy as two independent roots; the generated lock annotates
numpy as coming both from that input and from pandas. The test asserts only
that numpy occurs somewhere in the closure, so it cannot distinguish
transitive presence from direct authorization.

**Concrete failure scenario:** a future supported pandas version removes
numpy, or excludes it for one environment with a marker. An ordinary install
then follows the sole-direct-dependency decision, but the supported
institutional install continues to install the native numpy package because
the input still requires it. That dependency survives without a new plan
decision, despite the recorded withdrawal and the security inventory calling
it transitive.

**Required repair:** remove numpy as an input root, regenerate the
institutional lock from pandas alone, and mechanically compare the direct
roots of every runtime input with project metadata. A separate closure check
may continue to require whatever pandas actually resolves. The owner
confirmation flagged in the plan remains a governance action.

### P1-R3-F9 — Major — table-controlled display instructions still reach human-facing sinks

**Location:** src/synthtwin/summary.py:54-78, 117-144, 197-257;
src/synthtwin/errors.py:38-52, 131-139, 297-305;
src/synthtwin/reading.py:214-236; src/synthtwin/cli.py:195-204, 298-303.

The summary-local function escapes C0, C1, and DEL. Error builders never call
it, even when they interpolate header names read from the table. The function
also passes Unicode format controls and line/paragraph separators unchanged.
Round 2 explicitly required byte-level coverage of error sinks, bidirectional
controls, and ordinary non-ASCII text.

**Concrete failure scenario 1:** give the CSV two identical header names
containing ESC followed by the terminal clear-screen command. Header checking
correctly refuses the duplicate, but stderr contains the raw ESC sequence.
The CLI exits 1 after handing the table-controlled terminal instruction to the
screen, so the same command class the repair blocked in the normal summary
still reaches a neighboring human-facing sink.

**Concrete failure scenario 2:** an otherwise valid header containing U+202E
(right-to-left override) or U+2028 (line separator) is accepted. Both code
points remain raw in captured stdout and the written summary. They can reorder
what the person sees or inject a visual line boundary inside the disclosure.

**Required repair:** route every table-derived value through one escaping
boundary before every human-facing sink, including all refusal and option
messages, or reject such schema text at input. Define and test the complete
display-control set, including Unicode Cc/Cf and line/paragraph separators,
while leaving ordinary printable non-ASCII text intact.

## Previously admitted-open items, confirmed but not re-derived

| Item | Standing state |
| --- | --- |
| P1-R2-F4 | **Blocker, open:** the finite-number accuracy contract is not met. |
| P1-R2-F5 | **Blocker, open:** the numeric oracle is not yet valid enough to freeze acceptance. |
| P1-R2-F11 | **Major, open:** the two output writes are not transactional. |
| P1-R2-F13 | **Major, open:** the required case-variant header warning is absent. |
| P1-R1-F4 and R1-X3 | **Blocker, open:** the two readers can accept different values despite matching dimensions. |
| P1-R1-F5 | **Blocker, open:** ambiguous headerless mixed input can lose and publish its first record. |
| P1-R1-F7 | **Blocker, open:** automatic sentinel decisions remain ambiguous and can delete or retain real values incorrectly. |
| P1-R1-F8 | **Blocker, open:** realistic measurements, codes, and categories still take information-destroying roles. |
| P1-R1-F9 | **Blocker, open:** the profile contract still loses generator-relevant distribution facts. |
| P1-R1-F10 remainder | **Blocker, open:** forced-role precedence and suppression across remarks/missing keys remain unresolved. |
| P1-R1-F13 format-spec half | **Major, open:** dynamic format specifications still reach caller-controlled formatting code. |
| P1-R1-F15 | **Major, open:** memory behavior and recovery advice still diverge from the plan. |
| P1-R1-F16 | **Major, open:** failure-catalog tests do not prove real trigger reachability or exact user-facing behavior. |
| P1-R1-F17 | **Major, open:** claimed per-spelling missing counts still merge source representations. |
| P1-R1-F18 | **Minor, open:** a valid leading Latin-1 byte can be mistaken for a UTF byte-order signal. |

## What held under attack

- The exact module-level redefinition of validate_local_path is red; a stored
  or callback bare read_csv reference is red; the current product reader call
  is direct and receives a freshly validated Path.
- Official typing.cast call forms preserve origins; one or repeated frame
  subscripts retain pandas; unenumerated frame attributes and visible pandas
  writer attributes are red.
- Direct parsing of unsigned accounting parentheses stays negative, and an
  inner plus/minus is no longer sign-reversed.
- Existing input/output and output/output hard links are refused on this POSIX
  host; FIFO and /dev/null targets are refused as non-regular; direct
  validated.walk callback slots are red.
- The pandas floor is 2.1.0 in pyproject.toml, requirements-min.in, and
  requirements-min.lock. The workflow compares the installed pandas version
  with that declaration before pytest. The eight dependency tests and the
  explicit minimum lock/input structural validation pass.
- Source imports no numpy. The scanner rejects a numpy import, and the exact
  math enumeration matches the five functions the source uses.
- The dependency half of the institutional install uses --no-index,
  --find-links, and --require-hashes; the project wheel uses --no-index and
  --no-deps. The remaining defects are the missing project-artifact binding
  and incomplete cross-machine bundle, not a return to the old source build.
- Normal-summary C0/C1/DEL bytes are rendered visibly; ordinary printable
  non-ASCII text is preserved.

## Verification and attack coverage

The complete staged baseline passed before this artifact was added:

    pytest -q
      592 passed, 4 skipped
    offline source scan
      9 files, 0 violations
    decontamination
      clean
    signed attestation
      verified
    provenance
      passed
    dev, institutional, and minimum input/lock validation
      all passed
    ruff
      passed
    mypy
      9 source files passed
    staged and unstaged whitespace checks
      passed

The required pre-publication sequence was also followed: git add -A, then a
clean decontamination scan, before this file was written. After this artifact
was staged, the full suite, all standing scanners/checkers, all three explicit
lock pairs, Ruff, mypy, and whitespace checking were rerun.

Targeted scanner work covered bare and qualified fenced names; stored,
callback, and direct uses; module/function/class lookup; validator, Path, and
cast shadowing; same-function identity; match captures; official positional,
keyword, and mixed casts; repeated subscripts; enumerated and unenumerated
attributes; conditional, Boolean, assignment-expression, subscript, and call
targets; and direct/computed Path callback receivers. The 75 repository
scanner tests pass while six independent green mutations reached a reader or
writer at runtime; seven additional computed-call forms invoked callbacks.

Targeted profiler work covered high and low range failures, all-out-of-range
columns, range sign, threshold neighbors, interaction with sentinel
normalization, unsigned/signed/grouped/exponent accounting forms, role
routing, disclosure bytes, error bytes, C0/C1, Unicode direction and line
controls, and ordinary non-ASCII text. The 208 targeted parsing, taxonomy,
summary, and scanner tests pass despite the failures above.

Filesystem work covered existing and missing targets, exact equality,
symbolic and hard-link aliases, input/output and output/output pairings,
directories, FIFOs, a device, and identity-query failure. This host is POSIX;
Windows reparse behavior was not independently exercised beyond the
repository's platform-mocked tests.

Supply-chain work traced project metadata, all requirement roots and compiled
annotations, every lock consumer, minimum-job artifact flow, installed-version
proof, project-wheel digest flow, the documented connected/locked-machine
commands, environment markers, and CI's actual wheelhouse acquisition/smoke
path. No real air-gapped second host was used; the documented bundle is
structurally incomplete before such a run can succeed.

The checked properties were: offline-fence soundness, origin honesty, Python
scope fidelity, single-outcome numeric routing, silent type misrouting,
input/output non-destruction, two-artifact identity, exact floor testing,
complete hash binding, target-complete offline installation, dependency-root
authorization, callback-slot closure, and safe human display. Attack classes
included aliasing, shadowing, scope disagreement, pattern binding, computed
calls, value-preserving syntax, threshold interactions, all-invalid
populations, linked filesystem names, metadata failure, artifact substitution,
cross-platform acquisition, and data-controlled terminal text.

## Cosmetic observations not counted as items

README.md still says there are exactly two runtime dependencies and that both
are scanner-reduced; the workflow's opening comment says the same; and
SECURITY.md still tells an auditor to confirm dependencies is empty. Those
sentences are stale and should be repaired. They are cosmetic by themselves.
P1-R3-F8 is different: requirements-install.in actually installs numpy as a
root, so that finding changes behavior and authorization rather than wording.

## What stands between this phase and ratification

This is not yet close to ratifiable. Before another ratification request:

1. close P1-R3-F1 through P1-R3-F6 and rerun every runtime mutation named
   above;
2. close the admitted-open blocker set: P1-R2-F4, P1-R2-F5, P1-R1-F4,
   P1-R1-F5, P1-R1-F7, P1-R1-F8, P1-R1-F9, P1-R1-F10 remainder, and R1-X3;
3. repair the new Major items P1-R3-F7 through P1-R3-F9 and the admitted-open
   Majors P1-R2-F11, P1-R2-F13, the format-spec half of P1-R1-F13,
   P1-R1-F15, P1-R1-F16, and P1-R1-F17; resolve P1-R1-F18;
4. obtain the owner confirmation still flagged for the withdrawn direct
   numpy decision, then align the actual institutional root set and only
   afterward clean up the cosmetic dependency prose.

## Verdict

**Verdict: reject.** Blocking items: P1-R3-F1 through P1-R3-F6, together with
the admitted-open blockers P1-R2-F4, P1-R2-F5, P1-R1-F4, P1-R1-F5,
P1-R1-F7, P1-R1-F8, P1-R1-F9, and P1-R1-F10 remainder; R1-X3 remains a
blocking member of the P1-R1-F4 family.
