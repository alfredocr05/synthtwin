# Phase 2 — The generator: a twin from the profile alone

**Status:** revision 5 — after all five plan review rounds, and after
seven owner decisions taken on 2026-08-11. Round 1 rejected revision 0
with seventeen blocking items; round 2 rejected revision 1 with nine;
round 3 rejected revision 2 with six; round 4 rejected revision 3 with
eight; round 5, the final authorized round, rejected revision 4 with
ten items and — at the implementer's request — separated them into six
that must be settled before the contract artifact, three carryable to
later bounded checkpoints, and one audit repair. Revision 5 settles the
six. **Phase 2 is built from this revision under the owner sequencing
override recorded below**, with the five review rounds run against the
finished phase.

**What round 4 changed.** Three of its blocking items were consequences
of revision 3's own repairs, and each is now withdrawn or corrected
rather than defended. The ownership-proof mechanism revision 3 invented
to spare a repeat run is withdrawn: it proved less than it claimed and
it violated this plan's own read boundary. The producer-side size caps
revision 3 added are withdrawn: they contracted a domain Phase 1 already
promised, which is not an implementer's decision to take. And revision
3's numeric spelling pair was chosen on an implementer claim that
measurement disproved — the decimal form silently changes a whole-number
column into a decimal one — so the correction went back to the owner
rather than being applied quietly. Round 4 also found the identifier
decision traced through one disposition when it invalidates three, two
datetime dispositions reversed, and three origins in the scanner
policy where revision 3 named one. **Round 4's items P2-R4-F5 and F6
required owner dispositions, which were taken on 2026-08-11 as decisions
8 and 9, and its item P2-R4-F7 required the settled amendments to be
recorded in the antecedent plans, which has been done** — Phase 0 D12
now carries a dated amendment record and the Phase 1 plan carries its
own beside the all-different obligation.

**Scope:** one new command path — `synthtwin generate <profile>` — that
consumes a profile document and produces the synthetic twin: a CSV table
with the same columns, the same row count, and the same published
statistical behaviour as the profiled table, together with a
plain-language generation report. The phase also delivers the profile v4
contract and the strict loader that enforces it.

**Non-goals:** no validator and no quality report (Phase 3); no
relationship CONTENT; no new roles or subtypes (Phase 4); no row-count
override; no reproduction of absent-value spellings; no Excel/parquet/
database input or output; no PyPI release.

## Sequencing — four artifacts, ratified in order

1. **This plan.** Ratification fixes every decision below.
2. **`docs/spec/profile-contract-v4.md`** — the complete normative
   contract. **Blocking**: ratified before any method text or code.
3. **`docs/spec/generation-method-v1.md` plus the frozen neutral
   reference vectors** — the exact transform from (profile, seed) to
   twin bytes. **Blocking**: ratified before the implementation it
   anchors exists.
4. **The implementation**, reviewed against all three ratified
   documents.

Artifacts 2 and 3 carry out decisions this plan makes; neither may
introduce a mechanism this plan left open.

**Sequencing — owner decision, 2026-08-11.** The standing process
reviews each artifact before the one it anchors, and this plan's own
gate says no implementation may begin until artifacts 2 and 3 are
ratified. **The owner directed that Phase 2 be BUILT first and reviewed
afterwards**, in five review rounds against the finished phase. This is
an owner override of a plan-held condition, recorded here for the audit
trail by the same mechanism as the Phase 1 sequencing override and the
Phase 0 D2 waiver. The implementer's caveat was given and is recorded:
a specification reviewed only after the code exists loses the cheapest
place to catch a design error, so any design item those reviews reject
is repaired in code rather than only in prose. Two things reduce that
cost and are part of the override: artifacts 2 and 3 are still WRITTEN
first, before any code, so the implementation is built against a written
contract; and the plan's own review record is complete through round 5,
so the design has already absorbed five adversarial passes. Nothing else
changes — the reviewer's verdict governs, and no Phase 2 claim rests on
any artifact being pre-ratified.

**Round 5's own ruling on what may proceed.** The final plan review
returned reject and, at the implementer's request, separated its items:
six must be settled before the contract artifact (its F1, F2, F3, F5,
F6, F7), and three may be carried to later bounded checkpoints (F4, F8,
F9), with one audit repair (F10). Revision 5 settles the six — two of
them by the owner decisions 10 and 11 above — and records the carried
three as conditions on the artifacts that own them, so a later reviewer
can see exactly what was carried and where it must be closed.

---

## P2-D0. Owner decisions taken for this phase

Four were taken on 2026-08-10 and seven on 2026-08-11. The 2026-08-11
decisions were each required by a review round ruling that an
implementer may not trade away a published fact or amend a ratified
rule: decisions 5-7 by round 3, decisions 8-9 by round 4, and decisions
10-11 by round 5.

1. **Additive axes in v4** (P2-D3).
2. **Multiplicity parity** for `free_text` and `numeric_unrepresentable`
   (P2-D4).
3. **Relationship manifest reserved**, eight null slots (P2-D5).
4. **Exact-count allocation** (P2-D6), with the blanket claim replaced
   by the disposition matrix and the forced-row-equality consequence
   disclosed (P2-D11).
5. **Twin dates keep the shape the real table had — an amendment to
   D12** (2026-08-11; closes P2-R3-F4). D12 fixes dates and times to ISO
   8601 with an explicit offset. The producer legitimately publishes
   offsetless dates and quarters, recording their offset as `(none)`, so
   no output could satisfy both D12 and the published facts. **The owner
   amended D12 for twin CSV cells**: a twin datetime cell is written in
   the ISO form matching the precision the profile records — a date-only
   column writes `2024-03-15`, a quarter column writes `2024-Q1`, and an
   offset is written only where the profile records a real one. The
   amendment is scoped to twin CSV cells; the profile document's own
   canonical serialization is unchanged. Gain: the twin re-profiles to
   the same precision and offset state, so date-handling code developed
   on the twin behaves the same on the real table.
6. **When a declared identifier's published length and its
   all-different fact cannot both hold, LENGTH WINS and invented
   identifiers may repeat** (2026-08-11; closes P2-R3-F7). The
   implementer recommended the opposite — relaxing length to keep every
   value distinct — and the owner chose length. **The cost is stated
   here, not softened:** in that corner the twin's identifier column
   contains duplicate values where the real column had none, so a join
   or a de-duplication developed against the twin can fan out or
   collapse differently than on the real table. The report names the
   column, the number of duplicates and that consequence, every run.
   What the decision buys is that the twin's identifiers keep the exact
   width the real ones had, so width-dependent validation and
   fixed-width parsing developed on the twin still hold. **Scope, stated
   precisely:** this governs ONLY the case where the published facts are
   jointly infeasible. The general all-different obligation inherited
   from P1-D4 item 8 — that a column publishing
   `n_distinct == n_present` generates all-different values, on every
   role — is unchanged and still binding wherever it is feasible, which
   is the ordinary case and includes every undeclared key column
   arriving as free text.
7. **Twin numeric cells may use more than one spelling of the same
   value — an amendment to D12** (2026-08-11; closes P2-R3-F6),
   **with its permitted family corrected by decision 8 below.**

8. **The permitted numeric spelling family is the leading-zero family,
   not the decimal-point pair** (2026-08-11, superseding decision 7's
   spelling set; closes P2-R4-F5). Decision 7 was taken on an
   implementer statement that proved false on measurement, and the
   correction was put back to the owner rather than applied quietly.
   Measured with the reader researchers use:

   | twin cells | column type inferred | values read back |
   |---|---|---|
   | `0`, `1`, `2` | whole number | 0, 1, 2 |
   | `0`, `00`, `000` | **whole number** | 0, 0, 0 |
   | `0`, `+0`, `00` | **whole number** | 0, 0, 0 |
   | `0`, `0.0` | **decimal** | 0.0, 0.0 |
   | `1E5`, `1e5` | decimal | 100000.0, 100000.0 |

   The decimal-point form of decision 7 silently changes a whole-number
   column into a decimal one; the leading-zero and leading-plus forms do
   not, and they have **no ceiling** — `0`, `00`, `000`, … supply as
   many distinct spellings of one value as a profile can ask for, which
   also removes the capacity shortfall round 4 found in the two-spelling
   set. **The permitted family is therefore:** the canonical spelling,
   leading-zero forms, and the leading-plus form. Case-varied exponent
   forms (`1E5`/`1e5`) are permitted for one purpose only — supplying
   fold collisions where the profile records fewer folded than raw
   spellings — and are noted as changing the inferred type, which is
   faithful because a real column containing them is read the same way.
   Never thousands separators (the comma breaks the CSV row itself) and
   never parentheses. **An alternate spelling is used ONLY where the
   published counts require it**, so an ordinary all-canonical integer
   column stays byte-plain and is read as a whole-number column exactly
   as the real one is.

   **Scope, after decision 10** (code review item P2-C1-F8): this family
   is what the twin INVENTS from where a published count needs more
   spellings of one value than the description accounts for. It is not a
   ban on writing a form the description itself publishes — decision 10
   made the form of each cell a published fact, and the record under
   that decision says which clause governs where the two read
   differently.

9. **The profile records the spelling variants of a published label, so
   label columns keep their distinctness** (2026-08-11; closes
   P2-R4-F6). The producer folds case and trims spacing before
   publishing a label, so a column holding `A`, `a`, `B`, `b` publishes
   two labels of two rows each, and a twin built from that record writes
   `a, a, b, b` — repeating where the real column never did, and
   breaking the inherited all-different rule for every label role, not
   only for identifiers. The implementer recommended accepting the
   repeats and disclosing them; **the owner directed the opposite** —
   the profile records the variants so the twin can keep the values
   distinct.

   **This is a new published fact and is treated as one.** The variants
   of an already-published label are recorded with their counts, and
   **each variant is governed by the same small-cell floor as any other
   published label**: a variant shared by fewer rows than the floor is
   withheld and pooled into a counted remainder, exactly as a rare label
   is. So the disclosure delta is bounded to the capitalization and
   edge-spacing forms of labels the profile already publishes, and no
   variant crosses the boundary that a whole label would not. It
   advances the contract with the rest of v4, appears in the disclosure
   battery, and is named in `SECURITY.md` and the summary as a fact the
   profile now carries.

10. **The profile records HOW a numeric column's values were written, so
    the twin can be read as the same type** (2026-08-11; closes
    P2-R5-F1). Round 5 demonstrated that three source families — `0`,
    `00`, `000`; `0.0`, `00.0`, `000.0`; and `0e0`, `00e0`, `000e0` —
    produce **byte-for-byte identical** column blocks today: role
    `count`, three present, three raw and folded identities, all
    numeric, all zero, `integer_valued: true`. An ordinary reader
    infers a whole-number column from the first family and a decimal
    column from the other two, so no profile-only generator could
    preserve the reader's type for all three, and decision 8's
    leading-zero family silently chose the whole-number shape for all of
    them. The owner directed that the missing fact be published rather
    than the fidelity abandoned.

    **The fact is about FORM, not values.** Each numeric column records
    `numeric_styles`: a map from a spelling style to the number of cells
    written that way, over the enumerated styles `plain`,
    `leading_zero`, `leading_plus`, `decimal`, `exponent_lower`,
    `exponent_upper`. It carries no value, no magnitude and no spelling
    — only how many cells used each form. **The small-cell floor governs
    it** like any published fact: a style used by fewer rows than the
    floor is withheld and pooled into a counted remainder, so a single
    oddly-written cell cannot be singled out. The twin writes each style
    in its published count, which restores both the inferred type and
    much of the raw-distinctness capacity, and the styles it may write
    are exactly decision 8's family.

    **Which of those last two clauses governs, recorded here because
    they conflict** (code review item P2-C1-F8, 2026-08-11). "Writes
    each style in its published count" and "the styles it may write are
    exactly decision 8's family" cannot both be obeyed on a column
    publishing eleven `decimal` cells: decision 8's family holds no
    decimal form at all. **The first clause governs, and decision 8's
    family keeps the job it was taken for.** The two decisions answer
    different questions, and separating them keeps both of them true:

    - decision 8 fixes what a twin may INVENT — the spellings it reaches
      for where a published count needs more spellings of one value than
      the style map accounts for. That family is the leading-zero one:
      no ceiling, and no change to the type a reader infers.
    - decision 10 fixes what a twin REPRODUCES — the form of each cell,
      now that the form is published. Writing a `decimal` cell with a
      point is not the harm decision 8 named; the harm decision 8 named
      was a decimal form chosen where nothing published asked for one,
      which turned a whole-number column into a decimal one. Where the
      description says the real cell had a point, writing one is the
      only way decision 10's own purpose is served.

    This is the reading the shipped producer, loader, generator and
    reference vectors already carry, and both specifications now state
    it in one form (contract 7.5.7, method G6.1). It is a reading of
    decisions 8 and 10 as taken, not a new decision; it is written down
    here so the owner can see the clause that was set aside and say so
    if the other reading was meant.

11. **Label spelling variants get a complete contract, and the
    disclosure is described accurately** (2026-08-11; closes P2-R5-F2).
    Decision 9 authorized recording variants; round 5 found the plan
    stated neither a wire shape nor an honest delta, and that the
    implementer's description of the delta to the owner had been too
    narrow. Both are corrected, and the owner confirmed the broader
    reading.

    - **The delta, stated accurately:** the producer folds with a
      Unicode `casefold()` after trimming, not merely capitalization. So
      recording variants publishes every exact spelling that differs
      before that fold — which includes pairs a reader may not expect,
      such as `ß` and `SS` normalizing together. The owner confirmed
      this broader reading.
    - **The wire shape:** each PUBLISHED label carries `variants`, a map
      from the exact spelling to its count. Every variant is bound to
      one already-visible parent label; the keys are forbidden on a
      withheld parent and on every non-label role. Invariants: each
      variant's count is at most its parent's, and the variant counts
      plus the withheld pool sum exactly to the parent's count.
    - **Withheld variants keep their shape** (the owner confirmed this
      too): where a spelling is below the floor it is not shown, and the
      parent carries `variants_withheld`, an anonymous map from an
      occurrence count to how many distinct spellings occurred that
      often — the same class of fact as the identifier repetition
      multiset. Without it, a parent of eleven rows cannot be told apart
      from eleven one-off spellings versus two spellings occurring ten
      and one times, and the twin would not know how many spellings to
      invent.
    - **Consequences carried:** the contract text saying case and edge
      spacing are not preserved is corrected; the matrix row for label
      raw distinctness is reconciled (P2-D6); the generator writes
      variants rather than only normalized labels; the disclosure
      battery scans the COMPLETE profile and profiler summary as well as
      the twin and report, because the new fact appears first in the
      profile; and `SECURITY.md` gains the entry the plan previously
      claimed it already had.

Inherited owner decisions, unchanged: numpy returns as a direct
dependency; `identifier` is declared-only, never inferred; the first row
is taken by convention and disclosed; a declared identifier publishes
the anonymous count multiset.

**Still flagged for the owner, and NOT assumed:** whether to publish
width facts for `numeric_unrepresentable` (residual R-P2-1). The plan
proceeds without it.

## P2-D1. The boundary: what is checked, from which instant

The generator never reads the real table. Round 3 (P2-R3-F1) showed
revision 2's extent began too late: Python executes `synthtwin.cli`'s
top-level imports before any branch exists, and that module
unconditionally imports the table reader for the `profile` command, so a
graph including module initialization can never pass and one excluding
it leaves module-level work outside the boundary entirely.

**The checked extent begins at process start from the installed entry
point**, and the fork is closed by construction rather than by argument:

- **command modules are imported lazily**, inside the branch that needs
  them, so importing the entry point initializes no reader-bearing
  module. The generate invocation must be provably free of `reading` at
  every instant, not merely after dispatch;
- the closure covers module initialization, the parser prologue, the
  generate branch, and everything reachable from them — imports,
  first-party calls, re-exports, aliases;
- **the allowed read set is enumerated**: the profile document through
  the loader, and nothing else. **The forbidden target set is
  enumerated**: `reading` and every function it exposes, `pandas`, and
  any first-party helper whose own closure reaches either;
- **red mutations at four positions**: a module initializer, the command
  prologue, the generation body and a post-write step must each fail the
  suite, and so must reaching a forbidden target through an alias or a
  re-export;
- **every neutral move is named.** The write transaction and the profile
  serializer both live in `profile.py`, which imports the real-table
  type; both move to modules importing neither, and the transaction's
  fault-injection measurement is re-run against the moved code rather
  than inherited;
- no generation-path layer may accept or construct a table path, handle,
  table object or raw cell collection; signature mutations assert this
  at every layer.

## P2-D2. The contract gate: profile v4, its normative spec, its strict loader

**Wire-shape decisions**, all matching the shipped producer: role keys
are FLAT; positions are ONE-BASED with a producer-to-loader round trip
fixing the base; published label identity is NORMALIZED — the producer
trims and case-folds before pooling, so a published label may never have
appeared byte-for-byte in the table. The contract calls it a normalized
identity everywhere, and the report says case and edge spacing are not
preserved.

**The normative spec** states, for the whole document and every role:
required keys, forbidden keys, type and range, enums, null meanings,
publication class, and the invariants — `n_present + n_missing ==
n_rows`; each multiplicity map's entries summing to `n_distinct` and its
count-weighted keys to `n_present`; every ladder non-decreasing;
positions forming exactly `1..n_columns`;
`len(levels) + suppressed_levels == n_distinct_folded`;
`sum(level counts) + suppressed_rows == n_present`. The last two were
verified against real producer output.

**The strict loader** is the first implemented artifact and the only way
generation receives a profile:

- `profile_version` must be exactly 4, with direction-correct advice: an
  older profile is re-made by re-running `synthtwin profile`; a NEWER
  one means this generator is behind and the advice is to update the
  generator, never to re-run a profiler on a machine that may not hold
  the table;
- **duplicate keys and every non-canonical form are caught by canonical
  round-trip**: parse with plain `json.loads`, re-serialize under the
  canonical rules, require byte equality. A duplicated key cannot
  round-trip. Verified before being written here; no callback slot is
  involved, and reordered keys and non-canonical numbers are refused
  too;
- **the limits are fixed here, and they contract nothing** (P2-R3-F8,
  P2-R4-F10, P2-R4-F11). Revision 3 set a 64 MiB document cap and gave
  the shipped profiler the same bounds. Round 4 was right that this
  withdrew part of a domain Phase 1 already promised — wide tables
  supported within available memory — which is a product decision, not
  an implementer one. **No size cap and no producer-side cap are
  imposed.** A profile too large for the machine fails on the
  catalogued memory-exhaustion path, exactly as Phase 1's own reader
  does, so the two phases promise the same thing. What IS bounded are
  the three structural quantities that protect the parser rather than
  the domain. Round 5 (P2-R5-F7) showed revision 4's container-entry
  limit was still a domain cap in disguise: every column contributes one
  entry to `columns`, so a ten-million-entry ceiling is a ten-million-
  COLUMN ceiling, which Phase 1 never promised to stop at. **The
  container-entry limit is therefore removed.** Exactly **two** bounds
  remain, and neither is reachable by any producible profile because
  neither scales with the table: maximum nesting depth **32** (the
  document is six deep, and depth is a function of the contract's shape,
  not of the data), and maximum length of a single JSON NUMERIC TOKEN
  **64 characters**, because an arbitrarily long numeric literal costs
  quadratic parse time while the producer's longest published number is
  far shorter. Both are checked by a bounded first-party structural
  pre-scan over the text using only string operations, before parsing.
  Near-limit-valid and one-over-limit tests are required for each. **No
  other limit exists anywhere in this phase**: no document-byte cap, no
  container cap, no producer-side cap, and no string-length cap beyond
  the reader's own shipped field limit — a profile too large for the
  machine fails on the catalogued memory-exhaustion path exactly as
  Phase 1's reader does. A producer-to-loader boundary test asserts that
  a genuine wide-table profile loads;
- **the failure surface is catalogued**: invalid UTF-8, escaped lone
  surrogates, non-finite numbers the parser would accept, and each of
  the two bounds have their own plain-language message. No message on
  this path quotes `n_rows`, because allocation can fail before any
  field is validated;
- unknown keys, missing required keys, wrong types, out-of-range values
  and violated invariants are refusals naming the key and the rule;
- the loader returns typed objects and performs **no** generation
  feasibility check — that is a separate stage (P2-D6), so a
  contract-valid document never becomes unloadable.

**The publication guard covers the FINISHED DOCUMENT** (P2-R3-F3).
Revision 2 chose a recursive whitelist over the completed column
mapping; round 3 showed `build_document` lifts `publication_notes` to
the top level after `_column_block` returns, so a future note
interpolating a source spelling would pass the column-level recursion
and be serialized anyway, with the matrix completeness assertion still
green because no new key appeared. The recursion therefore runs over the
finished document tree, top-level notes included.

**Its acceptance mechanism is chosen here, not delegated** (P2-R5-F5).
Revision 4 said the leaf classes would be "fixed in the spec", which is
the deferral round 4 already rejected, and a path-and-type whitelist
cannot in any case tell a fixed first-party note from a source spelling
formatted into the same note path. **The mechanism is origin tagging
with an enumerated note grammar.** Every string that may appear in the
finished document is one of exactly two kinds: a value the matrix
authorizes for publication, or a note built by an enumerated
first-party constructor from a fixed grammar of literal fragments plus
already-authorized values. Notes are not free strings: each is
constructed by a named function that takes only enumerated arguments,
and the guard accepts a note leaf only when it carries that
constructor's origin. A future note that interpolates a source spelling
therefore fails at construction, not at pattern-matching, because the
spelling is not an authorized argument. Required mutations: a source
spelling formatted into an existing note path with an unchanged type; a
concatenation that assembles the same text from fragments; a nested
container smuggling one; and a note lifted to the top level.

**Documentation gate — three corrections, not two** (P2-R3-F10):
`SECURITY.md` must stop saying generically that attributes on
enumerated-library results are enumerated, and must count ONE run-time
reader control; the Phase 1 plan must say no other pandas NAME can
appear in executable source; **and the scanner's own accepted-built-in
paragraph must stop saying every other accepted built-in takes data and
never invokes an argument** — length, truth, iteration, conversion,
formatting and hashing each disprove it. All three, plus the
non-exhaustive-example and decorator wording, are asserted by test.

## P2-D3. The axes beside the role (owner decision 1)

`role` stays as shipped. Every column block gains `statistical_type`
(`unknown`, `numeric`, `constant`, `binary`, `datetime`, `count`,
`continuous`, `categorical`, `code`, `text`), `quality_state` (`ok`,
`empty`, `unrepresentable`) and `structural_role` (`data`,
`identifier`), each derived by a fixed rule the contract states.
`structural_role` is `identifier` exactly when the column was named with
`--identifier`, including a declared column that ends `empty`. **The
generator dispatches on the axes, never on `role`.**

## P2-D4. Repetition multiplicity, and what it cannot carry (owner decision 2)

`free_text` and `numeric_unrepresentable` each gain
`n_distinct_by_occurrences` with the identifier field's exact shape and
serialization; distinctness is over raw present values; the publication
class is counts about unnamed groups, with no small-cell floor.

**What it cannot fix.** `numeric_unrepresentable` publishes no width or
magnitude fact — verified against the producer, whose block carries
`n_whole`, `n_fraction`, `n_whole_unknown`, `n_positive`, `n_negative`,
`n_sign_unknown`, `n_out_of_range` and the universal counts. Two columns
of overflowing values, one about 400 characters wide and one about
4,000, publish identically. Width fidelity is withdrawn, the facts that
exist are preserved exactly, and one canonical invented width is
disclosed (R-P2-1, still flagged for the owner).

## P2-D5. The relationship manifest (owner decision 3)

Profile v4 gains one top-level block with eight required keys, each
exactly `null`: `deterministic`, `grain`, `hierarchy`, `keys`,
`missing_data_process`, `statistical`, `temporal`,
`validation_targets`. The loader refuses non-null content. Filling any
slot advances `profile_version`. The generator carries one dispatch seam
that verifies the block is empty and generates columns independently.

## P2-D6. What "matches" means: the disposition matrix and the feasibility stage

**Five dispositions.** EXACT-OBSERVABLE (reproduced and independently
recounted from the written CSV); EXACT-CONTROL (a metadata or dispatch
decision CSV cannot evidence — `role`, the three axes, `position`, and
`name` when no header is written — evidenced by typed-object or
schema-order assertions plus a misrouting mutant); APPROXIMATED (a
stated rule and a two-sided finite-sample bound, measured and named in
the report); REPORT-ONLY (not reproduced; stated in the report);
LOADER-ONLY (validated on input, never an output obligation).

**Equality per path**: `n_distinct` counts RAW present spellings;
`n_distinct_folded` counts folded identities; numeric statistics
describe PARSED values; level facts use the FOLDED identity; datetime
facts use the parsed instant at the recorded resolution.

**The matrix is derived from genuine producer shapes, per role, not
written from memory** (P2-R3-F5). Round 3 found three contradictions
with the producer, each now fixed:

- **`n_rows` is two different things and revision 2 conflated them.**
  The DOCUMENT-level `n_rows` is universal and EXACT-OBSERVABLE. The
  per-column `n_rows` echo appears **only inside numeric blocks**
  (count, continuous) — verified — and is LOADER-ONLY. The contract
  names them separately.
- **`empty` gets its own dispositions.** It is neither a label,
  invention nor distribution role, and revision 2's partition omitted
  it. An empty column publishes `n_distinct = n_distinct_folded = 0` and
  no per-column `n_rows`; both counts are EXACT-OBSERVABLE and trivially
  met by an all-absent column.
- **Datetime cardinality has its own explicit bound.** Revision 2 sent
  "distribution roles" to a row sitting under a numeric heading, so one
  implementation could bound datetime distinctness and another ignore
  it. `n_distinct` and `n_distinct_folded` on datetime columns are
  APPROXIMATED under the same two-sided envelope as the numeric roles,
  stated in the datetime table.

**Raw versus folded, reconciled after owner decisions 9 and 11.** The
earlier text rested on a premise those decisions removed — that the twin
must write only normalized identities — and the plan was not reconciled
when they were taken. Corrected: for **label roles**
`n_distinct_folded` is EXACT-OBSERVABLE, and raw `n_distinct` is
**EXACT-OBSERVABLE where the published variants and the withheld-variant
multiset supply enough spellings**, which is the ordinary case, and
APPROXIMATED under the two-sided envelope only where they do not, with
the report naming the profile's count beside the twin's — the same shape
as the numeric rule below. For **invention roles** raw `n_distinct` is
EXACT-OBSERVABLE and `n_distinct_folded` is EXACT-OBSERVABLE too, which
obliges the invention alphabet to REPRODUCE FOLD COLLISIONS when the
profile shows folded below raw. That obligation is binding and
non-trivial: a real 200-row single-character identifier profile
publishes 200 raw and **122** folded, so 78 values must fold onto a
partner. For **numeric roles** the raw count is reproduced using the
spellings owner decision 7 permits.

**Top-level dispositions**, including the structural containers round 4
found missing (P2-R4-F9). A sixth class exists for them: **STRUCTURAL**
— a container whose own key carries no VALUE obligation, but which does
carry membership and order obligations, because round 5 (P2-R5-F6)
showed that "no obligation" left the schema itself ambiguous. For every
STRUCTURAL object the contract states exact membership, and for
`columns` specifically: **`len(columns) == n_columns`; `columns[i]` has
`position == i + 1`; and LIST ORDER is the schema order, the twin's
output column order, and the order in which the single RNG stream is
consumed.** Without that, two conforming implementations could serialize
the blocks in different order and route names, type paths, values and
RNG bytes differently while every set invariant passed. `columns` and
`source` are STRUCTURAL; the completeness assertion accepts a container
only when every leaf under it is disposed AND its membership rule is
stated; STRUCTURAL appears in the disposition battery and in acceptance
criterion 3 alongside the other five; and swapped, duplicate, omitted
and extra column-block mutations must each fail. Leaves: `profile_version`, `settings`, `created_with`,
`publication_notes`, `relationships` and the per-column `n_rows` echo
are LOADER-ONLY; document `n_rows` and `n_columns` are EXACT-OBSERVABLE;
`source.encoding` and `source.used_fallback_encoding` are REPORT-ONLY;
`source.header_source` is EXACT-CONTROL; and
`source.header_by_convention` and `source.header_evidence` are
REPORT-ONLY **with a required sentence**, because Phase 1's R1 residual
means those names may actually be a first data row and a report saying
only "a header was written" hides a warning the profile carries.

**Universal fields** (on every role: `name`, `position`, `role`, three
axes, `n_present`, `n_missing`, `missing_by_class`, `missing_by_source`,
`n_distinct`, `n_distinct_folded`, `n_numeric`, `n_not_numeric`,
`n_out_of_range`, `n_contradictory`,
`n_sentinel_candidates_unpublished`, `sentinel_verdicts`,
`detection_evidence`, `remarks`):

| field | disposition |
|---|---|
| `n_present`, `n_missing`, document `n_rows`, `n_columns` | EXACT-OBSERVABLE |
| `name` | EXACT-OBSERVABLE when a header is written, else EXACT-CONTROL |
| `position`, `role`, the three axes | EXACT-CONTROL |
| `missing_by_class`, `missing_by_source` | REPORT-ONLY — every absent cell is written empty |
| `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory` | EXACT-OBSERVABLE by class-preserving construction |
| `n_sentinel_candidates_unpublished`, `sentinel_verdicts`, `detection_evidence`, `remarks` | REPORT-ONLY |

**Numeric (count, continuous)**: `percentiles` endpoints
EXACT-OBSERVABLE, interior rungs APPROXIMATED inside a rung-by-rung
two-sided envelope; `n_zero`, `n_negative`, `std_unrepresentable`,
`n_negative_unrepresentable`, `n_used_in_statistics`,
`n_left_out_of_statistics`, `numeric_share` EXACT-OBSERVABLE;
`integer_valued` EXACT-OBSERVABLE, routed by the published FACT and not
by role; `mean`, `std`, `skew` APPROXIMATED with fixed formula and
two-sided bound; `n_distinct` and `n_distinct_folded` EXACT-OBSERVABLE
using the spellings of owner decision 7, falling back to the two-sided
envelope only where even those cannot supply the count, which the report
then names.

**Label roles (categorical, binary, constant)**: `levels` (normalized
label and count), `suppressed_levels`, `suppressed_level_counts`,
`suppressed_rows` EXACT-OBSERVABLE; `level_ceiling` LOADER-ONLY.

**Datetime**: `earliest`, `latest` EXACT-OBSERVABLE in the
representation owner decision 5 fixes; `date_percentiles` endpoints
exact and interior rungs APPROXIMATED; `resolution`, `time_precision`,
`subsecond_digits`, `utc_offsets`, `earliest_utc_offset`,
`latest_utc_offset` EXACT-OBSERVABLE. Two dispositions revision 3 got
backwards are corrected here (P2-R4-F3):

- **`format` is REPORT-ONLY, not EXACT-OBSERVABLE.** It names the real
  file's parser family — `compact-date`, `month-first-date` and the
  rest — and owner decision 5 chooses ISO twin syntax at the recorded
  precision, not the source's lexical family. A month-first column's
  twin therefore reprofiles as `iso-date`, so the field cannot be
  reproduced and must not be claimed. **R-P2-7 is reinstated** for
  exactly this narrowed loss: the twin keeps the precision and offset
  state but not the source's date spelling, so code that parses dates
  with an explicit source format needs that argument changed. Revision
  3 withdrew the residual wholesale and thereby hid this.
- **`datetimes_read_at` is EXACT-OBSERVABLE, not EXACT-CONTROL.** It is
  derived from the offset diversity present in the cells, so it is
  recomputable from the written twin and must be checked that way; a
  dispatch assertion cannot detect a twin that reprofiles from `utc` to
  `local` because one invented rare offset changed the diversity while
  the pooled offset map and endpoints still matched.

`n_unparsed` is EXACT-OBSERVABLE as counted neutral stand-ins,
explicitly OUTSIDE the parsed-value representation obligation.

**Free text**: `length.min`, `length.max`, `words.min`, `words.max`,
`n_all_digits`, `n_code_alphabet`, `n_distinct_by_occurrences`
EXACT-OBSERVABLE; `length.mean`, `length.p50`, `words.mean`
APPROXIMATED with two-sided bounds.

**Identifier**: `min_length`, `max_length`, `all_whole_numbers`,
`n_all_digits`, `n_code_alphabet` EXACT-OBSERVABLE in every case, since
owner decision 6 keeps the length. **In that decision's infeasible
corner, THREE distinctness facts are REPORT-ONLY, not one**
(P2-R4-F4, and the same gap found independently in an implementer
probe): raw `n_distinct`, `n_distinct_folded`, and
`n_distinct_by_occurrences`. Computed for the real 200-row
single-character case, a twin holding length 1 can offer at most 95
distinct characters and 69 distinct folded identities against 200 and
122 published, and 200 values drawn from at most 95 cannot be
all-singleton — so the multiplicity map is necessarily violated too.
That last one deserves naming: the multiplicity map exists precisely so
a generator never invents a repetition pattern, and in this corner it
must. What the identifier column then preserves is `n_present`,
`n_missing`, the length range, `all_whole_numbers`, `n_all_digits` and
`n_code_alphabet` — and nothing about distinctness or repetition. The
report names all three lost facts with the achieved value beside the
published one, and the feasibility battery asserts all three. Outside
that corner every one of them is EXACT-OBSERVABLE.

**Numeric unrepresentable**: `n_whole`, `n_fraction`, `n_whole_unknown`,
`n_positive`, `n_negative`, `n_sign_unknown`, `n_out_of_range`,
`n_distinct_by_occurrences` EXACT-OBSERVABLE; width not published.

**Enforced by a test, not by care.** A completeness assertion enumerates
every key the producer emits for every role plus every top-level key and
FAILS when any key has no disposition. It must pass against the ratified
matrix as written — it may not acquire exceptions during implementation.

**The generation-feasibility stage.** Separate from the loader, run
after loading and before generation; every outcome fixed here:

1. **Domains are widened first**: identifier and text alphabets include
   upper and lower case — which is also what lets fold collisions be
   placed — and the full printable ASCII range.
2. **Identifier length versus distinctness**: owner decision 6 governs.
   Length is preserved; the fewest necessary values repeat; the report
   names the column, the duplicate count and the join consequence.
3. **Numeric raw distinctness**: owner decision 7 governs. The permitted
   spellings reach the published count; where even they cannot, the
   two-sided envelope applies and the report names both counts.
4. **Published counts take precedence over ladder conformance** where a
   numeric conflict is otherwise resolvable; the residual deviation is
   measured and named.
5. **Refusal is reserved for documents no rule above can satisfy**, and
   is a refusal of GENERATION, never a claim that the profile is
   invalid: the message says the profile is valid, names the two facts
   that cannot both hold, and gives remediation that does not assume the
   person holds the table.

**Frozen genuine producer outputs**: the feasibility and conflict
batteries use profiles emitted by the Phase 1 producer itself, built by
seeded neutral fixture generators, not hand-built documents, and run
producer → loader → generator end to end. The two named cases are the
200-distinct single-character identifier (200 raw, 122 folded, all
singleton) and the 100-cell `0`/`0.0` numeric column.

## P2-D7. The method specification and its frozen reference vectors

No implementation until the specification and vectors are ratified. It
fixes: the RNG construction of P2-D8 including the order and count of
every draw; the numeric method (inverse transform over the 11-rung
ladder with piecewise-linear interpolation, the two extreme positions
pinned by fixed rule so the endpoints land, pinning never costing an
extra draw); the integer rule wherever `integer_valued` is published,
with its rounding direction; the permitted numeric spellings of owner
decision 7 and when each is used; the two-sided rung envelope, so a
mutant collapsing the nine interior rungs FAILS; the datetime method in
ordinal space at the recorded resolution, emitted in the representation
owner decision 5 fixes for every precision and offset state, `(none)`
and quarter included; the label methods; the invention alphabets and
their fold-collision construction; and the class-preserving stand-ins of
P2-D9.

**The reference vectors** are computed by a tool under `tools/reference/`
implementing the specification and importing nothing from `src/`. Exact
quantities are computed in integer or rational arithmetic and each
published binary64 is proved correctly rounded by midpoint comparison.
The tool walks the exact serialized tree it writes, tuples included
(P1-R8-F3's blind spot), and carries a full-generator mutant that must
fail. Vectors are committed, provenance-bound, rebuilt and byte-compared
in CI. Named cases: a date-only column, a quarter column, an
offset-bearing datetime column, and a mixed parsed/unparsed column.

## P2-D8. Determinism: ONE stream, one draw shape

- one `numpy.random.Generator`, created once from the seed and threaded
  explicitly; no module-level randomness; columns consumed in schema
  order; draws in the order the specification fixes;
- **one draw shape.** The specification fixes a single form — a
  full-width unsigned 64-bit draw — and derives uniforms, bounded ranges
  and arrangements from those words in first-party audited code.
  Measured across the floor and current versions (numpy 1.24.0 and
  2.5.1, seed 12345), power-of-two, non-power-of-two and uint64 draws
  all agree exactly, so nothing diverges today; fixing one shape narrows
  what the twin's bytes can ever depend on. **The claim revision 2 made
  here is withdrawn** (P2-R3-F2): using `integers` does NOT make the
  vectors independent of numpy, because `integers` is itself the
  retained random operation. First-party post-processing removes the
  additional surfaces, nothing more;
- the D12 consequence is documented: a schema change, or a method change
  altering a column's draw count, shifts every later column at the same
  seed. Regeneration after a method change is a changelogged event;
- **special elements are placed by fixed rule, never an extra draw**;
- **the seed's accepted set and its GRAMMAR are fixed** (P2-R3-F9). The
  value range is `0` through `2**64 - 1`. The accepted spelling is one
  or more ASCII decimal digits and nothing else: no sign, no
  underscores, no internal or surrounding whitespace, no non-ASCII
  digits. Leading zeros are accepted and do not change the value. Frozen
  boundary tests: `0` and `18446744073709551615` accepted;
  `18446744073709551616`, `-1`, `1_0`, a leading-space spelling, and a
  non-ASCII digit each refused with a catalogued plain-language message.
  The library accepts a wider set and refuses negatives with a raw
  exception, which is why synthtwin states its own range and never lets
  that exception reach a person;
- **the determinism battery asserts both directions**: identical inputs
  give identical bytes; a different seed changes interior values for a
  profile that HAS a random degree of freedom; and **twin bytes are
  seed-INVARIANT for a fully determined profile** — one whose published
  counts pin every cell — so a mutant letting the seed change quoting or
  ordering on such a profile fails;
- no `spawn`, so no numpy floor above pandas' own;
- **numpy returns as a direct runtime dependency** under the full D5
  protocol: justification, a tested floor proved by the `minimums` job,
  locks and hash-pinned install file regenerated.

## P2-D9. Generation semantics for every published class

- **Absent cells**: exactly `n_missing` per column, written EMPTY,
  positions seeded-random; spellings and classes not reproduced, and the
  report names the real table's published spellings.
- **Left-out numeric classes are partitioned**: ordinary non-numeric,
  out-of-range, contradictory and their sign intersections each get a
  class-preserving neutral construction, recounted from the written CSV.
- **Unrepresentable numbers**: invented digit strings themselves outside
  binary64 range, reproducing the whole/fraction and sign counts and the
  multiplicity map, at one disclosed canonical width.
- **Free text — the binding rule.** The generator INVENTS language:
  neutral synthetic words honoring the published length and word
  statistics, the digit and code-alphabet counts, and the multiplicity
  maps including fold collisions. **It never samples, quotes, templates
  from, or paraphrases source text.** Any future change carrying source
  language into the profile or twin is a charter change requiring an
  owner decision and a privacy review.
- **Identifiers**: invented neutral values honoring the length range,
  the whole-number and alphabet facts and the multiplicity map, with
  owner decision 6 governing the infeasible corner.
- **The all-different obligation, restated as one rule with named
  instances** (P1-D4 item 8; P2-R5-F3). Whenever a column publishes
  `n_distinct == n_present`, its present values are all different, on
  every role, in that column's own notion of equality — because an
  undeclared key column arrives as free text or a numeric role, not as
  an identifier. **The obligation can bind only on facts the profile
  actually publishes**, and stating it that way is what stops a fourth
  instance arriving undetected. Where the raw distinctness of a column
  was produced by something the disclosure rules WITHHELD, the twin
  cannot reproduce it without making up unpublished facts, so raw
  distinctness is REPORT-ONLY there and the report names the achieved
  count beside the published one. Three instances are known and each is
  tested:
  1. **Declared identifiers** whose published length range cannot supply
     as many distinct values as the column has rows (owner decision 6).
  2. **Label columns** whose values differ only before the fold —
     resolved by owner decisions 9 and 11, which publish the variants,
     so the obligation now HOLDS for labels wherever the variants are
     visible and falls back only beneath the floor.
  3. **Datetime columns whose offsets are withheld** (P2-R5-F3, verified
     against the producer). A 30-row column of ten rare offsets over 15
     dates publishes `n_present = n_distinct = 30` while
     `utc_offsets` collapses to `{"(withheld)": 30}`: the obligation
     fires, but the profile never says which offsets made those 30
     spellings distinct, so the twin holds only 15 instants and no
     published way to spell them apart. Where the same column's offsets
     ARE published, the obligation holds and the twin uses them.
- **Empty columns** generate as all-absent.
- **Labels**: published normalized labels at exact counts; withheld
  levels as invented neutral labels at their exact published sizes.

## P2-D10. Outputs, the command, and errors that speak human

**The command:** `synthtwin generate <profile>`, with `--seed` (default
0, grammar and range enforced), `--out-dir` and `--replace`.

**Exact output identities.** Default folder is the profile's folder;
names derive from the profile's stem, removing a trailing `-profile`:
`<stem>-twin.csv` and `<stem>-twin-report.txt`. These cannot collide
with the profiler's pair, verified against the shipped naming helper.
The input profile, twin and report must be three distinct files; an
output resolving to the input by path, link or alias is refused before
anything is written.

**Pre-existing targets: the run refuses unless `--replace` is explicit.**
Round 2 showed the inherited transaction replaces any ordinary file at a
target. Revision 3 tried to spare the commonest repeat action — running
`generate` again with a different seed — by proving ownership from a
marker line and a twin file name recorded in the existing report. **That
mechanism is withdrawn** (P2-R4-F1), for two reasons, and the withdrawal
is recorded rather than quietly dropped because it was an implementer
idea that failed on its own terms. First, it did not prove what it
claimed: a marker and a recorded name establish only that the report
once referred to a file of that name, not that the CSV now at that path
is that file — so a stale report beside a substituted, valuable CSV
would have authorized replacing it. Second, it violated this plan's own
boundary: P2-D1 permits the generate path to read the profile document
and nothing else, and recognizing the marker requires reading the
report, while binding it to the current twin would require reading the
twin too.

**So the rule is the simple one.** If either target exists, the run
refuses, naming both exact paths and what it would replace, and
`--replace` is the explicit action that permits it. The rule is
symmetric across both targets. The cost is one flag on a re-run, which
the refusal message teaches, and that is the right price for a rule that
cannot be argued into replacing someone's data. Tests: a renamed valid
profile with unrelated ordinary files at each derived target leaves
every byte unchanged on a default run; and link, alias and
between-check-and-write cases are covered.

**Two files, or neither.** The transaction is reused but MOVED to a
neutral module (P2-D1); its composed refusals name the profile and the
table by vocabulary (`errors.py` lines 570, 602-603, 610, 633), so the
artifact nouns become parameters and the exact-shape and reachability
tests extend to these INHERITED messages; and the statement and opcode
injection measurement is **re-run** against the moved, parameterized
transaction. Its residuals are inherited and restated.

**Bytes.** Both artifacts are UTF-8 with LF, no byte-order mark, with a
terminal newline; report bytes are part of the golden contract. Datetime
cells follow owner decision 5; numeric cells follow owner decision 7.

**The leading U+FEFF header exception.** Phase 1 can validly publish a
first column name beginning U+FEFF when that character sits inside a
quoted first field. Writing it unquoted would begin the twin with the
marker sequence, which the same reader then consumes, silently renaming
the column. **Such a name is always quoted**, as a canonical exception
to minimal quoting; the test asserts the exact bytes, the absence of a
leading marker, and a full profile → twin → reader round trip that reads
back the published name byte-for-byte.

**The header row follows `source.header_source`** — present when the
names came from the file, absent when generated by `--first-row data`,
verified against the producer. The report states which was written, and
when `header_by_convention` is true it states that the names may instead
be a first data row.

**One display boundary.** Every interpolated column name, normalized
label and published spelling passes through the shipped
`parsing.visible`, which escapes line, control and bidirectional
formatting characters, verified. (Round 1 cited `parsing.display_text`;
no such function exists.) The report is golden-tested with hostile
names.

**The formula-context policy.** A CSV cell beginning `=`, `+`, `-`, `@`,
tab or carriage return is treated as a formula by common spreadsheet
software. Exact allocation requires the published label unchanged, so
the twin is NOT altered; ordinary CSV quoting is never presented as a
mitigation; the hazard is counted and the columns named; and an
unavoidable plain-language warning appears in the report and command
output every run. **What the battery proves and does not**: it asserts
that an ordinary CSV reader reads back the exact published label, that
the counter fires for header and cell positions, and that the warning is
present — it executes NO spreadsheet, so the plan claims only that the
enumerated leading characters are the hazardous set by documented
behaviour.

**The failure catalog** extends to: a profile path missing, unreadable
or a folder; a document that is not JSON, with the parse position;
invalid UTF-8, lone surrogates, non-finite numbers, and each of the two
bounds; a non-canonical or duplicated-key document; a wrong
`profile_version` with direction-correct advice; every schema refusal;
every feasibility refusal, naming the conflicting facts and the
remediation; an existing output target when `--replace` was not given
(there is NO proof-of-ownership route, by P2-R5-F9); an output resolving to the input; a seed outside the
grammar or the range; an unwritable location; memory exhaustion. Each
has an exact-shape test and a reachability test.

## P2-D11. Honest limits, and what the twin actually is

- **The record claim is a provenance claim.** Generation reads no source
  table and samples and copies no source row, but exact allocation can
  FORCE a synthetic row to equal a real one: an 11-row single-column
  table whose one label clears the floor publishes it with count 11, so
  the twin holds it in all 11 rows. The qualified form replaces every
  categorical claim.
- **All three artifacts carry real-derived published facts** and the
  institutional handling and approval requirement; synthtwin claims no
  formal privacy guarantee.
- **The claim inventory is repository-wide**: `CLAUDE.md`, package and
  module docstrings, README, SECURITY.md, command help and status
  output, reports and any generated metadata, with exact assertions that
  REJECT the old categorical wording and the profile-only handling
  wording on every public surface. Amending `CLAUDE.md` is a charter
  text change and is flagged as such.
- **Identifier duplicates in the infeasible corner** (owner decision 6):
  the twin's identifier column can contain duplicates where the real one
  had none, so joins and de-duplication can differ. Named in the report
  every time it happens.
- **Columns are generated independently**; no cross-column structure is
  preserved. Said in every report; Phase 5 lifts it.
- **Rows are treated as independent and the grain is undescribed**, so a
  repeated-measures table yields marginals that misdescribe the
  subject-level truth. Faithful at ROW grain only; said in every report.
- **Approximated fields are approximated**, each achieved value named
  beside its published one.
- **Invented content is structure, not meaning.** Numbers computed on
  the twin are not scientific results, and nothing in this phase
  validates fidelity.

## P2-D12. Testing strategy

- **Loader mutation battery** with a vacuity floor; canonical
  round-trip tests including duplicated-key, reordered, invalid-UTF-8,
  lone-surrogate and non-finite documents; near-limit-valid and
  one-over-limit tests for each of the two bounds.
- **Matrix completeness assertion** over every producer-emitted key per
  role plus every top-level key, passing against the ratified matrix
  without exceptions.
- **Disposition battery**: EXACT-OBSERVABLE recounted from the written
  CSV; EXACT-CONTROL asserted at the dispatch boundary with a misrouting
  mutant; APPROXIMATED inside two-sided bounds; REPORT-ONLY asserted
  present in the report; LOADER-ONLY asserted to impose no output
  obligation.
- **Reference-vector tests** and **golden twin AND report hashes** on
  every CI cell, including the date-only, quarter, offset-bearing and
  mixed parsed/unparsed datetime vectors.
- **Rung mutants** (ignore, permute, swap) and the endpoints-only mutant
  must fail.
- **Feasibility battery** over frozen genuine producer outputs,
  producer → loader → generator, for both named conflict cases, each
  producing the outcome the owner decisions fix.
- **Boundary battery**: closure from process start, with red mutations
  in a module initializer, the command prologue, the generation body and
  a post-write step, through aliases and re-exports, plus signature
  mutations at every layer.
- **Ownership battery**; **U+FEFF round-trip battery**;
  **hostile-display battery**; **formula-context battery** as bounded
  above.
- **Determinism battery** including seed grammar boundaries, scoped
  sensitivity, and seed invariance for fully determined profiles.
- **Transaction battery** re-run against the moved, parameterized
  writer.
- **Disclosure battery** over complete twin and report files.

## P2-D13. Offline-scanner policy extensions (D6.2)

Round 3 (P2-R3-F2) ruled that naming methods without naming provenance
rules is not D6.2 granularity, and corrected revision 2's claim about
bare from-imports — the scanner binds an allowed from-import as an `api`
kind and accepts a bare call, verified independently (`from json import
dumps` with a bare call scans clean). That claim is withdrawn and no red
mutation may rest on it. The enumeration:

- **E7 — `numpy.random.default_rng`, and nothing else from numpy.** No
  `spawn`. Every other numpy attribute stays refused. The two-component
  module key follows the established `os.path` shape, verified.
- **E8 — the Generator, the array, and the scalar are THREE origins,
  each with its own surface** (P2-R4-F2). Revision 3 tracked the array
  and then declared values taken out of it originless, which would have
  let `word.data`, `word.dump` and `word.tofile` through the scanner's
  documented untraced-attribute residual on a value that is still a
  library scalar. It also assumed one library-keyed method set could
  express three different surfaces, when the shipped tables are keyed by
  the first module component alone. The policy:
  - **Generator origin**: exactly one permitted method, `integers`, in
    exactly the one draw form P2-D8 fixes; empty attribute set.
  - **Array origin**: empty method AND attribute sets. Subscription and
    iteration PRESERVE the origin rather than dropping it — the shipped
    scanner already does this for a subscript, and the new rule must not
    undo it.
  - **Scalar origin**: empty method and attribute sets, carried through
    indexing and iteration, until an explicitly checked conversion to a
    first-party Python integer, which is the ONLY permitted operation
    and is enumerated as the point where the origin ends.
  - **A type-sensitive restricted-instance lookup** is required, because
    the shipped tables cannot express three surfaces under one library
    key.
  - **The draw's own arguments are enumerated**: the exact positional
    and keyword form of `integers`, and a first-party origin rule for
    `low`, `high`, `size`, `dtype` and `endpoint`, because a
    caller-derived argument can invoke object protocols while the method
    name stays permitted.
  - **Correction**: revision 3 called this the first non-empty entry in
    the restricted-instance table; pandas already occupies a non-empty
    attribute table, so the claim is withdrawn. What is new is the
    type-sensitive lookup.
- **E9 — `csv.writer`, its handle, its rows and its dialect.** Permitted
  methods on the returned writer are exactly `writerow` and `writerows`,
  with an empty attribute set. **The handle origin is enumerated**: the
  writer may be constructed only over the transaction-owned, locally
  validated output target, never over a caller-supplied object, because
  the constructor invokes the object's write protocol and would
  otherwise send output elsewhere. **The row origin is enumerated**:
  those methods accept only first-party-constructed text sequences. **A
  `csv.writer` callback-slot entry is ADDED for the dialect parameter in
  both positional and keyword form** — revision 2 claimed the existing
  rule covered it, but the shipped callback table enumerates `csv.reader`
  only, and the generic callable check rejects functions and lambdas
  rather than caller-derived data objects.

Red mutations, one per capability: an unenumerated Generator method; any
attribute on a returned array; **any attribute on a scalar taken out of
that array, before conversion — the lost-origin route revision 3 would
have opened**; a numpy attribute outside E7; **a caller-derived value in
each `integers` argument slot, in each accepted argument form**; an
unenumerated writer method or attribute; a caller-derived output handle;
a caller-derived row source; and a caller-derived dialect in each
argument form.

## P2-D14. Residuals

Carried forward: **R1**, **R2**, **R3**, and the two transaction
residuals and third bound of P1-D5, whose evidence is re-measured.
P1-R8-**F6** is closed by the finished-document whitelist;
P1-R8-**F5** only when the three documentation corrections of P2-D2 are
made; P1-R8-**F7** by the contract gate.

- **R-P2-1.** Unrepresentable values have no published width; one
  canonical width is invented. Still flagged for the owner.
- **R-P2-2.** Absent-value spellings and classes are not reproduced.
- **R-P2-3.** Independent columns and undescribed grain.
- **R-P2-4.** Approximated fields are bounded, measured and reported.
- **R-P2-5.** The twin is always UTF-8 with LF regardless of source
  encoding.
- **R-P2-6.** A published label a spreadsheet reads as a formula is
  written unchanged; counted and warned, not altered.
- **R-P2-7. REINSTATED, narrowed** (P2-R4-F3). Owner decision 5 keeps
  the twin's date PRECISION and offset state, so revision 2's larger
  cost is gone — but the source's lexical date family is not kept: a
  month-first table yields ISO twin dates. Code that parses dates with
  an explicit source format needs that argument changed. `format` is
  REPORT-ONLY for this reason.
- **R-P2-8. REPLACED by owner decision 6, and larger than revision 3
  said.** Where an identifier's length and distinctness cannot both
  hold, length is kept and values repeat; raw distinctness, folded
  distinctness AND the repetition multiset are then reported rather than
  reproduced, and the report names all three.
- **R-P2-9.** Twin numeric cells may carry several spellings of one
  value from the leading-zero family (owner decisions 7 and 8), so a
  twin column can look less tidy than a table whose numbers were written
  one way. The inferred column type is preserved, which the
  decimal-point form of decision 7 would not have done.
- **R-P2-10. WITHDRAWN as a contraction** (P2-R4-F11). No document-size
  or producer-side cap is imposed, so Phase 1's promised domain is
  intact; the two bounds that remain — nesting depth 32 and
  numeric-token length 64 — protect the parser and are unreachable by
  any producible profile. This sentence counted three until round 5
  (P2-R5-F7) removed the container-entry limit as a column ceiling in
  disguise, and it was not corrected then.
- **R-P2-11.** Label spelling variants are now published facts (owner
  decision 9), floor-governed like any label. The profile therefore
  carries slightly more about real labels than it did in v3, and this is
  named in `SECURITY.md`, the summary and the report.
- **R-P2-12.** A default `generate` run refuses when either output name
  is already taken; re-running requires `--replace`. The refusal message
  teaches the flag.

## Acceptance criteria

1. The four artifacts are ratified in order.
2. Profile v4 ships with the axes, the two multiplicity maps, the
   relationships block, one-based positions and normalized label
   identity, and with NO producer-side cap, which P2-D2 withdrew as a
   contraction of a domain Phase 1 already promised; the loader enforces
   the contract fail-closed with canonical round-trip, the two bounds
   P2-D2 fixes — nesting depth 32 and numeric-token length 64 — and a
   catalogued failure surface.
3. The matrix completeness assertion passes against the ratified matrix
   with no implementation-time exceptions; every EXACT-OBSERVABLE field
   is recounted from the written CSV, every EXACT-CONTROL field is
   asserted at the dispatch boundary with a misrouting mutant, and every
   APPROXIMATED field is inside its two-sided bound.
4. The feasibility battery runs over frozen genuine producer outputs and
   produces the outcome the owner decisions fix for each case.
5. The ownership battery leaves unrelated files untouched on a default
   run; the U+FEFF round trip reads back the published name
   byte-for-byte with no leading marker.
6. Golden twin and report hashes verified on every CI cell; rung,
   endpoints-only and seed-invariance mutants fail.
7. numpy lands under the full D5 protocol with E7-E9 enumerated to the
   name AND the provenance rule, and every red mutation refusing.
8. The repository-wide claim and handling inventory is complete, with
   assertions rejecting categorical record wording and profile-only
   handling wording on every public surface, and the three documentation
   corrections of P2-D2 asserted by test.
9. Every artifact scans clean **as a tracked file** — the no-argument
   content check reads its list from the index.

## Closure trail

Round 3 noted the round-1 identifiers stopped being tracked once round
2's items replaced them, so the trail below covers all three rounds.
Round 2 verified each of the 22 round-1 items and recorded eight fully
closed; every item it left open is carried by a round-2 item here, and
none is dropped.

| item | answered in |
|---|---|
| R2-F1 boundary root | P2-D1, rooted at process start |
| R2-F2 datetime vs D12 | owner decision 5 |
| R2-F3 matrix | P2-D6, producer-derived, with `empty`, the two `n_rows` and datetime cardinality fixed |
| R2-F4 feasibility | P2-D6 stage; outcomes fixed by owner decisions 6 and 7 |
| R2-F5 ownership | P2-D10, refuse when either target exists unless `--replace`; no proof route exists |
| R2-F6 E7-E9 | P2-D13, with provenance rules |
| R2-F7 provenance surfaces | P2-D11 inventory |
| R2-F8 EXACT vs CSV | P2-D6 five dispositions |
| R2-F9 U+FEFF | P2-D10 quoting exception |
| R2-F10 loader bounds | P2-D2, exactly two bounds: nesting depth 32 and numeric-token length 64 |
| R2-F11 seed | P2-D8 grammar, range, invariance |
| R2-F12 publication guard | P2-D2 finished-document recursion |
| R2-F13 formula battery | P2-D10 bounded claim |
| R2-F14 P1-R8-F5 | P2-D2, three corrections |
| R2-F15 record | this status and closure trail |
| R3-F1 module initialization | P2-D1 lazy command imports plus initializer mutation |
| R3-F2 scanner provenance | P2-D13; numpy-independence claim withdrawn |
| R3-F3 publication route | P2-D2 finished-document recursion |
| R3-F4 datetime | owner decision 5 |
| R3-F5 matrix vs producer | P2-D6 |
| R3-F6 numeric conflict | owner decision 7 |
| R3-F7 identifier length | owner decision 6 |
| R3-F8 loader limits | P2-D2 |
| R3-F9 seed grammar | P2-D8 |
| R3-F10 accepted built-ins | P2-D2 third correction |
| R3-F11 reference drift | this closure trail |
| R4-F1 ownership proof | P2-D10, mechanism withdrawn; refuse unless `--replace` |
| R4-F2 scalar/argument origins | P2-D13, three origins, type-sensitive lookup, argument slots |
| R4-F3 datetime dispositions | P2-D6, `format` REPORT-ONLY, `datetimes_read_at` EXACT-OBSERVABLE, R-P2-7 reinstated |
| R4-F4 identifier multiplicity | P2-D6, all three distinctness facts REPORT-ONLY in the corner |
| R4-F5 numeric spelling domain | owner decision 8, leading-zero family |
| R4-F6 all-different for labels | owner decision 9, published spelling variants |
| R4-F7 antecedent plans | amendments recorded in Phase 0 D12 and the Phase 1 plan |
| R4-F8 traversal acceptance rule | P2-D2, leaf classes and container rule fixed |
| R4-F9 structural keys | P2-D6, STRUCTURAL class for `columns` and `source` |
| R4-F10 numeric-token length | P2-D2, 64-character token bound |
| R4-F11 producer caps | P2-D2, contraction withdrawn; R-P2-10 withdrawn |
| R4-F12 closure trail | this table, now covering rounds 2, 3, 4 and 5 by identifier |
| R5-F1 numeric identity/type | owner decision 10, published `numeric_styles` |
| R5-F2 label variant contract | owner decision 11, wire shape, invariants, withheld multiset, SECURITY entry |
| R5-F3 datetime all-different | P2-D9, one rule with three named instances; Phase 1 amendment corrected |
| R5-F4 finite invention domain | CARRIED to the method-specification gate, bounded: the domain and its capacity rule are fixed there, with a named refusal where capacity cannot be met |
| R5-F5 publication guard mechanism | P2-D2, origin-tagged note constructors with an enumerated grammar |
| R5-F6 STRUCTURAL order/membership | P2-D6, `len(columns) == n_columns`, `columns[i].position == i+1`, list order is schema, output and RNG order |
| R5-F7 residual producer cap | P2-D2, container-entry limit removed; exactly two parser bounds remain |
| R5-F8 scalar-only operation | CARRIED to the scanner-extension gate, bounded: the enforced conversion point and its mutations land with E8 |
| R5-F9 ownership contradiction | P2-D10 and the failure catalog; every proof-of-ownership route deleted |
| R5-F10 record consistency | this table and the status block |

## Review record

**Plan reviews.** Round 1 rejected revision 0 (seventeen blocking
items); round 2 rejected revision 1 (nine); round 3 rejected revision 2
(six); round 4 rejected revision 3 (eight blocking, four required
repairs); round 5, the last authorized plan round, rejected revision 4
(ten items, separated into six to settle before the contract artifact,
three carryable and one audit repair). Revision 4 was the repair of
round 4 and carried the owner decisions 5 to 9 of 2026-08-11 — three
required by round 3 and two by round 4 — together with the amendment
records those decisions require in Phase 0 D12 and the Phase 1 plan.
**Revision 5 is the repair of round 5**: it settles that round's six,
adds owner decisions 10 and 11, and records the carried three as
conditions on the artifacts that own them.

**Status of each Phase 2 artifact, corrected here** (code review items
P2-C1-F8, 2026-08-11; P2-C5-C1, 2026-08-12). An earlier revision closed
this section with one sentence denying both that any Phase 2 code
existed and that any of this plan was ratified. That sentence was true
when it was written and is now false in both halves, while the status
block at the head of this document says the opposite; it is described
rather than repeated, so that a test can ban it outright. A second
correction is recorded here for the same reason: this block stopped at
code review round 1 while four further rounds had run, so an owner
reading it during a release decision would have seen eight round-1
blockers and not the four the final round leaves open. One record is
what a reader needs, so it is this one:

- **This plan, revision 5** — the ratified design. The owner sequencing
  override recorded above directed that Phase 2 be built from it, and
  every Phase 2 code review has reviewed the code against it as the
  ratified plan text.
- **The two specifications** — WRITTEN, reviewed in all five code review
  rounds, and rejected in every one of them. Rounds 1 to 4 each found an
  obligation this plan ratifies stated more weakly in one of them, and
  round 5 found the machine-checked registry installed against that
  defeated by six of eight scratch attacks. They are not ratified.
- **The implementation** — BUILT, and REJECTED in all five adversarial
  code review rounds:
  - **round 1** (2026-08-11) — reject, eight blocking items, P2-C1-F1 to
    P2-C1-F8;
  - **round 2** (2026-08-11) — reject, eight blocking items, P2-C2-F1 to
    P2-C2-F8;
  - **round 3** (2026-08-11) — reject, blocked on P2-C3-F1 and
    P2-C3-F2, with P2-C3-F3 carried as a bounded condition;
  - **round 4** (2026-08-12) — reject, blocked on P2-C4-F1 to P2-C4-F4,
    with P2-C4-C1 to P2-C4-C4 carried as bounded conditions;
  - **round 5** (2026-08-12), the last authorized round — **REJECT,
    blocked on P2-C5-F1, P2-C5-F2, P2-C5-F3 and P2-C5-F4**, with
    P2-C5-C1 alone carryable and bounded to this status repair and its
    claim-inventory, provenance and content-gate checks.

  Neither the code nor either specification is ratified. Repairs made
  after round 5 do not change that: a repair is not a review, and no
  further review round is authorized, so what any of those repairs left
  open is what the record above leaves open.

This block records what reviews found. It claims no control that
`SECURITY.md` lists as DEFERRED — those wait on the repository being
public and none of them is in force today — and it passes no verdict of
its own on fidelity.

The reviews themselves are in `docs/plans/reviews/`, and the sentence
each of them ends with is the record of what was true on its own date.
