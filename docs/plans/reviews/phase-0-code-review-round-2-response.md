# Response to Phase 0 code review — round 2

Implementer's answers to `phase-0-code-review-round-2.md` (11 remaining
blockers R2-B1..B11, two majors, three minors). Every item is answered
with a fix; the one plan conflict is answered with a proposed amendment
put to this cycle for ratification. The history remains unpushed.

**R2-B1 — fixed.** The scanner builds a per-module export map by parsing
every first-party module: names bound by def/class/plain assignment are
genuine exports; names the module itself imported are not importable from
it. The exact laundering probe is a red test, with a fallback rejecting
known module names when sibling source is unavailable.

**R2-B2 — fixed.** The origin lattice carries an explicit unknown member
that union never discards. Bare calls require every possible origin to
resolve; method calls follow a documented two-case policy — an enumerated
data-method list on untraced values (with the stated threat-model
rationale: caller-supplied objects execute in the caller's own process;
the boundary controls what this code initiates) and api-instance tracking
for allowlisted API results. Callables passed to non-first-party callees
are violations. Four new red probes, all shown to scan clean under the
prior scanner.

**R2-B3 — fixed.** A non-executing lexical/structural lock validator
(`tools/supply_chain/validate_lock.py`) accepts only exact hashed pins,
markers, and the binary-only directive, refusing archives, file
references, VCS, editable, paths, and direct references — with a red test
per class. CI runs it before every pip invocation that consumes the lock.
The prefetch mutation now packs a self-contained PEP 517 backend with a
correct hash and proves refusal for the archive reason with both
sentinels absent.

**R2-B4 — fixed.** One strict shared manifest parser lives in the scanner
and is imported by the verifier: exactly one occurrence of each mandatory
header, 64-hex body lines, duplicates a hard error. The verifier enforces
the exact attestation-v2 schema (all keys, types, no extras), recomputes
every public file binding directly, requires header/binding agreement
including the snapshot digest, and each inner check is proven by a
temp-key re-signed mutation that isolates exactly that check.

**R2-B5 — fixed.** The bound coverage battery now runs the committed
public scanner end-to-end: it materializes every inventory entry as real
files in five modes (lines, UTF-16, CSV cells, syntax-tree constants,
filenames) and asserts detection through `check.py` itself. It cannot
pass when the scanner, decoder, surface producer, or manifest is missing
or broken. Current result: all applicable forms detected, zero misses.

**R2-B6 / R2-M1 — fixed.** The magic mutation parameterizes over every
signature read from the committed table at test time; the count mutation
re-signs consistent outer bindings under a temporary key so the inner
count comparison is isolated and proven.

**R2-B7 — fixed.** The format gate now covers YAML (allowed only under
`.github/` or via the manifest), XML, SQL dumps, DuckDB, DBF, and
transport files, with red tests per class and the real tree green.

**R2-B8 — fixed.** The all-objects tool is fail-closed: any non-text blob
anywhere in history is a violation reflected in the exit code, proven by
a scratch-repo mutation with an unreachable malformed blob.

**R2-B9 — fixed.** The signed note no longer cites absent evidence: the
post-attestation-commit verification artifact is produced, signed, and
named precisely, with its digest bound at the next attestation refresh
(the ordering is stated in both artifacts).

**R2-B10 — fixed via a proposed amendment.** The workflow now fails when
its own comparison errors while detection stays non-failing; SECURITY.md
describes the actual mechanism; and D14 Amendment A2 (appended to the
plan, pending this cycle's ratification) replaces the label control with
annotation + step summary + release-time history collection, because
applying labels would widen the deliberately read-only workflow token.

**R2-B11 — fixed.** The guard runner installs an irremovable audit hook
blocking socket, process, and native-load events before the generator
runs; red tests cover the low-level socket route and a subprocess
attempt.

**R2-M2 — fixed.** The hook installer refuses to overwrite a
non-identical existing hook and is idempotent for its own.

**R2-m1/m2/m3 — fixed.** The amendment heading states its ratified
status; the CLI docstring states the narrow truth about metadata reads
and error behavior; the decontam job comment describes the separate
steps.

**Request to round 3:** verify the resolutions, rule on Amendment A2, and
state whether the history may be pushed. The attestation is re-signed
over the final bytes after this response is committed, per the refresh
discipline.
