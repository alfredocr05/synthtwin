# Phase 1 review round 1 — implementer response

**Verdict received:** reject; 12 blockers, 5 majors, 1 minor.

**Position taken on the review as a whole: accepted in full.** Every one
of the eighteen items was independently reproduced before any repair was
written -- eight verification passes, one per area, each required to run
a probe rather than to read the code and agree. Not one item was
refuted. Three additional defects were found in the course of that
checking and are recorded below as R1-X1..X3; the first of them is worse
than anything in the review.

This round repairs eight items. The rest are open, with their repairs
specified rather than started, and are listed at the end so the next
round is not spent rediscovering them.

## Additional defects found while verifying (not in the review)

**R1-X1 — a linked output target destroyed the user's own table.**
The review stopped at exfiltration (F3). The same unvalidated write is
data loss: with `table-profile.json` a symbolic link to `table.csv`,
`synthtwin profile table.csv` overwrote the source table with the
profile, printed "written to", and exited 0. On POSIX the F3 repair does
not catch this -- the target resolves to a permitted local path -- so it
needs its own rule. For an audience holding data they cannot re-acquire,
this is the worst outcome the tool has. Repaired: the two output targets
are compared against the validated input path and the run is refused
before anything is written.

**R1-X2 — the decontamination scan was vacuous on this tree.**
`tools/decontamination/check.py` enumerates git-TRACKED files. Every
Phase 1 file was untracked, so each "decontamination: clean" result in
the build -- and the one this review reports in its own verification
section -- covered the Phase 0 tree only. After staging, five denied
tokens surfaced, one of them in this review artifact. Repaired: the tree
is staged before any scan is believed; the flagged wording is rewritten
(the manifest is never touched). The review artifact's own token was
rewritten in place, value-preserving, and this is the notice of that
edit.

**R1-X3 — a second reader divergence, with no NUL in it.**
F4's parser-divergence case rests on NUL. A differential fuzz of
`csv.reader` against pandas' C engine over identical bytes found a
second class: for `b'c0,c1\\n\\r,B\\nz,w\\n'` the standard reader yields
`['', 'B']` and the C engine yields `['B', '']`. Values move BETWEEN
columns, so both columns are profiled wrongly and nothing looks unusual.
It survives any "bind the two passes to the same bytes" repair, because
it is a pure parser disagreement. This is the strongest argument that
F4's value-comparison branch, not its byte-binding branch, is the
load-bearing repair. Open.

## Repaired in this round

**F6 — the numeric machinery.** Accepted entirely; the rule the review
attacked is withdrawn, not adjusted. Rounding every published number to
twelve significant digits made the profile contradict itself, and the
plan section that specified it (P1-D11) is rewritten to say so and to
record why the replacement is sound. Statistics are now computed so that
the answer cannot depend on the machine or on row order: sorted values,
`math.fsum`, a power-of-two rescale before any sum, deviations recentred
once, and the scale reapplied after the square root with `math.ldexp`.
`**` is used nowhere in the numeric path.

Four errors in the obvious version of that repair were caught before it
was written, and each is worth recording because each was independently
reproducible: `x ** 2` is not an IEEE-754 operation and disagrees with
`x * x` on this host for 255 of 200,000 random inputs; `s * s * fsum(...)`
reintroduces the overflow and underflow the scaling exists to prevent;
`math.fsum` on raw values RAISES on the near-overflow case, and whether
it raises depends on the order, so sorting first makes it more likely,
not less; and the deviations must be recentred once, which is what
actually fixes the 1e15 case.

Values outside the representable range are now refused by the parser at
both ends and counted in their own field rather than spending the
straggler budget -- the mirror case the review did not name, where three
out-of-range cells silently turned a 202-row measurement column into an
identifier.

`numpy` is imported nowhere in `src/` as a result, and has left the
scanner allowlist; `math` is enumerated in its place. The owner's
dependency decision is recorded as partially superseded by this item and
is flagged for the owner's confirmation.

**F6f — the oracle.** `tools/reference/make_numeric_reference_vectors.py`
computes sixteen cases from the exact rational values of the inputs with
`fractions` and `decimal`, importing neither this package nor any
numeric library, and proves every float64 correctly rounded by exact
integer comparison against the midpoints to its neighbours. Its output is
committed as a provenance-manifest fixture, so CI rebuilds it from the
generator and byte-compares it: the oracle cannot drift towards the
implementation without the provenance guard going red. The accuracy
contract is frozen in P1-D11. The golden hash is kept and demoted, in
the plan and in its own docstring, to the change detector it always was.

One test was written and then removed for being unfalsifiable: it
claimed the whole-number rung rule fixed an observable defect. Searched
exhaustively, the two ways of locating a rung agree for every table
length from 2 to 20,000 at all eleven probabilities. The rule removes a
class of error rather than fixing an observed one, and the test now says
exactly that.

**F1 — the `read_csv` fence.** Accepted, and the review understates it:
`pathlib.Path("https://host/f.csv")` still enters the library's URL
branch, because the library turns the object back into text before it
decides. The claim that handing it a Path rather than user text was a
control is therefore withdrawn from the plan, the scanner docstring, the
reader docstring and `SECURITY.md`. The scanner now enforces provenance:
a fenced API may appear only as the direct target of a call -- never
stored, passed, or placed in a callback slot -- and its first argument
must trace, inside the same function, to `validate_local_path`. The
reader re-validates immediately before the call, so the fence is visible
where it is enforced rather than resting on the order the file happens
to be written in. Four red mutations added: the URL call, the `map`
callback, the stored reference, and the bare Path.

**F2 — origins lost through value-preserving calls.** Accepted.
`typing.cast` now preserves the origins of its argument, so a frame
cannot shed pandas on the way to `to_sql`; `global` and `nonlocal` are
refused outright in `src/`, which closes the module-level and
class-scope routes at their source rather than modelling them; and
attribute READS on pandas values are enumerated (`columns` only), which
closes `frame.style` and every other attribute that reaches capability
with no call in sight.

**F13 (part).** The `numpy.errstate(call=...)` half is moot: numpy is no
longer importable from `src/`. The format-spec half is open.

**F3, F14 and R1-X1 — the output path.** Accepted. Every exact output
target passes `validate_local_path` immediately before the write, including
generated defaults and including the public writer; a folder sitting on
either name is refused before anything is written; the disclosure is
printed BEFORE the files exist, which is what P1-D6 always said and what
the code inverted; the two writes are one outcome, and a first file
newly created is removed if the second fails; and an output that would
replace the input table is refused.

**F10 (part) — the override that wrote first and warned afterwards.** An
option naming a column the table does not have is now refused with exit
2, before the document is built and before anything is written, with the
real column names in the message. The remaining parts of F10 -- the
forced role losing to the constant branch, and the leaks through
remarks and missing-source keys -- are open.

**F11 — the minimums job.** Accepted. The job could not pass: it
installed a floor lock with no build backend and then built from source.
It now consumes the wheel the network-none container already built,
exactly as the tests job does, so no project build hook runs on a
networked runner. The drift test compares the file the job actually
installs.

**F12 — the institutional install.** Accepted. `pip install --no-deps .`
does not disable build isolation, so the documented procedure fetched
and executed an unpinned backend and could not work air-gapped at all.
README and `SECURITY.md` now name the wheel-based, no-index procedure
that CI exercises, and say why the source route is not it.

## Open, with repairs specified

F4, F5, F7, F8, F9, F10 (remainder), F13 (format-spec half), F15, F16,
F17, F18, and R1-X3. Two of these are design changes rather than fixes,
and the specifications for them exist:

- **F5**: the rule sketched during repair was tested against nine
  headerless and headed shapes and misfires on ordinary pivoted year
  tables (`region,2019,2020,2021`) while missing all-text headerless
  files entirely. It is not shipped. The replacement uses a three-way
  verdict over the shape of each column's values.
- **F8**: the role order is wrong, not merely its thresholds, and the
  repair moves identifier to a last resort, adds a mixed-numeric role
  with a structured unparsed remainder, routes fixed-width digit codes
  away from the numeric path, and caps the published level list instead
  of changing the role at the ceiling.

Two further defects found while verifying the taxonomy area are
recorded here so they are not lost: a binary column can publish three
labels, because the role is decided on case-folded values while the
levels are counted on raw ones -- and the case split can leave a
one-row attribute of one person visible; and the categorical ceiling
depends on the table's length, so profiling a subsample of a table can
change a column's role and destroy its levels.

## What the next round should hold against this work

Nothing in this response asks for an item to be reconsidered. The
verification standard used here -- reproduce before repairing, and
attack the repair before writing it -- found four errors in one repair
design and one unfalsifiable test, so the same standard should be
applied to the repairs themselves.
