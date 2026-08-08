# Contributing to synthtwin

Thank you for looking under the hood. This project runs on a small number
of hard rules. They exist because the tool's entire value is trust, and
every rule below is checked - by CI, by review, or by both.

## The plan-first process

No code is written without a plan, in every phase:

1. **Written plan.** Each phase begins with a written plan in
   `docs/plans/` that enumerates its decisions and acceptance criteria.
2. **Adversarial review before code.** The plan is reviewed adversarially
   - the reviewer's job is to break it - and revised until ratified.
   Review artifacts live in `docs/plans/reviews/`.
3. **Code review against the plan.** Implementation is reviewed against
   the ratified plan text. A deviation is either fixed or taken back to
   the plan as an explicit amendment; it is never waved through.

If you want to propose a feature, propose it at the plan level first. A
pull request that adds unplanned capability will be closed with a pointer
to this section, however good the code is.

## Standing rules

These apply to every change, in every phase:

- **All file input goes through the path validator.** Product code never
  passes a raw, user-supplied path to a filesystem call. The path
  locality rules (URL, UNC, and device-form rejection; Windows link
  rejection without resolution) are a standing obligation, not a Phase 0
  detail.
- **Literal constants carry a provenance line.** Any commit that adds
  literal string or numeric constants to `src/` or `tests/` must carry
  the checklist line "no value copied from private artifacts" in its
  commit or pull-request description. Reviewers check it. This is the
  human control behind the source-exposed-maintainer residual named in
  `SECURITY.md`.
- **Imports in `src/` are allowlisted.** Only the exact APIs enumerated
  in the current phase plan may be used - standard library and runtime
  dependency alike, name by name; `tools/offline_scan` enforces the list
  in CI. Membership in an allowed library grants nothing on its own, and
  objects returned by `pandas` or `numpy` may not be called through at
  all: read them with an attribute, a subscript or an operator and pass
  them back to an enumerated function. Needing a new API is a
  plan-level decision with a capability audit - do not work around the
  scanner.
- **Text handling has a shape the scanner accepts.** A function that
  calls string methods on a value it was handed opens with the exact
  type check `if not isinstance(text, str): raise ...`; after that the
  value's own data methods, slices and f-strings may be used freely. A
  value from anywhere else - a list element, a library object, a
  computed result - is not text as far as the audit is concerned, and no
  method may be called on it.
- **No data-format files, ever.** No `.csv`, `.xlsx`, `.parquet`,
  archives, or similar files are committed. Test fixtures are created at
  runtime by seeded, neutral code inside the test (in `tmp_path`). A
  committed fixture is allowed only if it is tiny and listed in the
  fixture manifest that binds path, generating script, seed, and SHA-256;
  CI (`tools/provenance`) rebuilds every committed fixture and
  byte-compares it.
- **Inbound = outbound.** Contributions are accepted under the MIT
  license, the same license the project is released under. No CLA. By
  submitting a change you agree to this.
- **Small, single-concern commits.** One logical change per commit, so
  review and history stay honest and any commit can be reverted alone.

## Determinism obligations

These bind every phase that touches randomness or writes output files:

- **One RNG, literally.** A single seeded `numpy.random.Generator`
  instance is created once from the seed and threaded explicitly through
  every consumer. No module-level randomness, no second generator, no
  hidden reseeding.
- **No unordered iteration on randomness paths.** Any iteration that
  consumes randomness runs over an explicitly sorted sequence. Sets and
  dict views are sorted before use on those paths.
- **Schema-driven output order.** Output column order is a fixed function
  of the schema, with derived columns appended in documented order.
  Internally selected special elements are chosen by a fixed rule, never
  by an extra draw.
- **Reference vectors precede implementation.** On every rebaseline path,
  neutral reference vectors are reviewer-checked and frozen before the
  implementation they anchor exists. Newly generated goldens are never
  their own oracle.

## Practicalities

- **Environment.** Python >= 3.10. Install with `pip install -e .` and
  the dev tools with the `dev` dependency group. Tests run with `pytest`
  against the installed package (src layout).
- **Checks.** CI runs lint (`ruff`), types (`mypy --strict` on `src/`),
  tests across the platform matrix, the packaged build, and the three
  guard suites (decontamination, offline-static, provenance) behind one
  aggregate check named `gate`. While the repository is private no branch
  ruleset is applied, so `gate` is the standing rule rather than a
  mechanically enforced one; it becomes the required context when the
  ruleset is applied at the visibility flip (see SECURITY.md). Run `ruff check .`, `mypy`, and
  `pytest` locally before pushing; the guard scanners in `tools/` can be
  run locally too.
- **Error messages.** Every error message must be actionable by a
  non-programmer: say what happened, in plain words, and what to do
  next.
- **Security issues.** Never report a suspected vulnerability in a public
  issue - use the private reporting path in `SECURITY.md`.
