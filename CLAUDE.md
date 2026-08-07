# CLAUDE.md - synthtwin implementer brief

This is the canonical brief for the implementing agent. It lives in the
repository and replaces the earlier private parent-folder brief.
Historical note: the project's working name changed to `synthtwin` before
the first commit, after the original name was found taken on PyPI; older
private planning documents may use the previous name.

## The goal

Researchers who hold sensitive tabular data cannot paste it into an AI
assistant, and often cannot move it off a compliant machine at all.
synthtwin gives them a synthetic twin of their table: the same columns,
the same types, the same distributions, the same relationships between
columns, and the same missing-data patterns - and not one real record.
They develop their analysis with AI assistance on the twin, freely and
quickly, then run the finished code on the real data inside their
compliant environment.

## The six principles

1. **Open source from day one.** Every line is public from the first
   commit. There is no private core, and nothing in the public tree
   depends on anything a contributor cannot see.
2. **Zero-code UX.** A researcher who has never programmed can run the
   whole workflow. No configuration files to hand-write, no flags that
   require reading source, and every message written for a human.
3. **Secure by architecture, fully offline.** The product code contains
   no construct that initiates network I/O, no subprocess execution, no
   native-code calls, no dynamic code loading; it accepts only local
   filesystem paths and is fully functional air-gapped. This is enforced
   by the layered checks in the Phase 0 plan (D6), not merely promised.
4. **Decontaminated.** No trace of the private prototype study's
   vocabulary, enforced by the hashed decontamination manifest in
   `tools/decontamination` and the process in the Phase 0 plan. Do not
   enumerate, hint at, or paraphrase the private vocabulary anywhere -
   in code, comments, tests, docs, commit messages, or branch names. If
   the scanner flags text you wrote, change the text; never change the
   scanner to make it pass.
5. **Comprehensive column handling.** Every column in the user's table
   is either handled correctly by an appropriate type path or declined
   with a plain-language explanation. Columns are never silently
   dropped, silently miscast, or silently approximated.
6. **Statistical fidelity is the product.** The twin is only worth
   using if code developed against it runs unchanged and meaningfully
   on the real table. A twin that misstates distributions or
   relationships fails the product's one job, even when nothing crashes.

## The four outputs

1. **The synthetic twin table** - same shape and statistical behavior,
   zero real records.
2. **The schema description** - columns, detected types, and how each
   was handled.
3. **The relationship summary** - which columns move together and how
   that structure was preserved.
4. **The plain-language quality report** - how well the twin matches,
   stated honestly, in words a non-statistician can read.

## Honest limits

- Numbers computed on the twin are not scientific results. The twin is
  for developing code; conclusions come from running that code on the
  real data.
- Fidelity is bounded. Modeled structure (per-column distributions,
  declared relationships, missing-data structure) is preserved; higher-order
  structure that was never modeled is not guaranteed.
- synthtwin is not a formal privacy mechanism and claims no
  differential-privacy property. The profile is computed from real data
  and must be handled under the institution's rules for real-derived
  material.
- The offline guarantee is a property of the code, verified by source
  audit and scans - it is not an OS-level sandbox. Institutions that
  require enforcement run the tool inside their own network-isolated
  environment.

## Rules of the road

- **The profile/generator boundary.** The profiler is the only code
  path that reads the real table. The generator never reads the real
  table - it consumes only the profile file. No debugging convenience,
  test helper, or one-time exception crosses that line, ever.
- **Determinism.** One RNG, created once from the user's seed, threaded
  explicitly through every consumer. No module-level randomness; sorted
  iteration wherever randomness is consumed; output column order a
  fixed function of the schema. Same profile, seed, version, and locked
  environment produce the same bytes on the same platform (plan D12).
- **Built-in validation.** The tool measures its own output and reports
  the result plainly. A check that cannot fail is a defect; a passing
  report must mean what it says.
- **Docstrings state guarantees.** Every public function's docstring
  says what it promises: accepted inputs, determinism behavior, errors
  raised, and any boundary it upholds. Review holds code to its stated
  word.
- **Errors speak human.** Every user-facing error names what went wrong
  and what to do next, in words a non-programmer can act on. "Invalid
  input" is a bug report against us, not an error message.
- **Open-source hygiene.** Small pushed increments; CI green before
  merge; GitHub is the source of truth; actions pinned by commit SHA;
  changelog kept current; nothing enters the tree that the
  decontamination, provenance, or offline scans would flag. Test
  fixtures are built by seeded neutral scripts at runtime - committed
  data-format files are forbidden outside the fixture manifest.

## The phase process

Plan first, always: every phase begins with a written plan in
`docs/plans/`, reviewed adversarially before any code. Code is then
reviewed against the ratified plan; deviations amend the plan, they do
not silently outgrow it. A freeze gate named in a plan (for example the
Phase 0 Class-A freeze) is blocking. Numeric machinery ports from the
private prototype only behind a ratified public method specification
with frozen neutral reference vectors, checked by the reviewer before
the implementation they anchor exists.

- **Phase 0 - public skeleton and security baseline:** repository, MIT
  license, CI, decontamination system, provenance guard, offline
  guarantee. (Current phase; see
  `docs/plans/phase-0-public-skeleton.md`.)
- **Phase 1 - the profiler:** read a local table, emit the profile;
  first runtime dependencies enter under the reviewed dependency
  protocol.
- **Phase 2 - the generator:** build the twin from the profile alone;
  the public method specification and frozen reference vectors are a
  blocking deliverable here.
- **Phase 3 - the end-to-end product:** profile, generate, and validate
  through one zero-code CLI; earliest possible first PyPI release.
- **Phase 4 - comprehensive column handling:** the full range of column
  types, rare categories, and missing-data patterns.
- **Phase 5 - relationships and fidelity depth:** cross-column
  structure and the quality report at full strength.
- **Phase 6 - standalone build:** hardened, fully offline distribution
  for institutional machines.
