# Phase 1 review round 2 — implementer response

**Verdict received:** reject; 9 blockers, 5 majors.

**Position: accepted in full.** Round 2 attacked the eight repairs from
round 1 and found holes in seven of them. That is the correct outcome
for repairs written under time pressure against a first review, and
nothing here argues with an item.

## Repaired in this round

**P1-R2-F1 — the fence still had direct bypasses.** Both were real.
`from pandas import read_csv` followed by `map(read_csv, paths)` scanned
clean, and a module-level redefinition of `validate_local_path` minted
the provenance the fence requires. The reference rule now applies to
bare names as well as attributes, and a shadowed validator no longer
counts as the validator. Both are red mutations.

**P1-R2-F2 — origins still lost.** All three routes were real. The
keyword form of `typing.cast` was uncovered (only the positional form
had a test); a subscript of a frame shed the library, so
`frame["x"].to_csv` wrote a file and `frame["x"].values.tofile` reached
numpy even though numpy cannot be imported at all. Casts now carry the
origin in every supported call form and refuse to retag anything else;
subscripts and enumerated attribute reads of a restricted object keep
that object's library. Red mutations for each.

**P1-R2-F3 — out-of-range accounting was dead code.** Correct: the
parser was repaired at round 1 and never wired into the routing. It now
feeds the numeric test, is excluded from the straggler budget, and is
published as `n_out_of_range` with its own remark.

**P1-R2-F6 — accounting notation reversed a sign.** A column of debts
written `(-1)`..`(-100)` published a positive mean. Contradictory
notation -- a sign inside parentheses -- is now refused rather than
interpreted. `(1)` is still negative one; `(-1)` and `(+5)` are not
numbers.

**P1-R2-F7 — hard links defeated identity.** Comparing path text was
the wrong test. Output targets are now compared to the input, and to
each other, by what the filesystem considers identity, and an existing
target that is not an ordinary file (a pipe, a device) is refused.

**P1-R2-F8 — the floor lock was not bound to the floors.** The lock the
job installs is now compared to the declared floor, and the job proves
the installed version before pytest runs rather than printing a listing.

**P1-R2-F9 — the institutional path.** Replaced with one copyable
two-machine procedure using `--no-index --find-links --require-hashes`
and `--no-deps`, matching what CI runs, and saying explicitly why
`pip install .` is not that path.

**P1-R2-F10 — the fence cost Path its slot rules.** A validated path is
a `pathlib.Path` again for the callback-slot table, so `walk(on_error=)`
is red once more.

**P1-R2-F12 — the plan authorized a surface the code no longer uses.**
P1-D2, P1-D2.1, P1-D10 E2, the declared floors, `pyproject.toml`,
`SECURITY.md` and the tests now describe one surface: pandas as the
single direct dependency reduced to `read_csv`, `math` enumerated in
place of numpy, and numpy recorded as a dependency OF pandas. The
withdrawn `numpy.errstate(call=...)` audit line went with it. The owner
decision that authorized numpy is marked as partially superseded and
flagged for the owner.

**P1-R2-F14 — table-controlled terminal instructions.** Everything that
came out of the table now passes through a visible-escaping function
before it reaches a screen or the written summary, so an escape
sequence in a header cannot clear the disclosure it follows.

## Open, and honestly so

**P1-R2-F4 and F5** — the accuracy contract and the oracle. F5 is the
more serious: an oracle that reports a negative standard deviation and
mishandles a half-even boundary cannot anchor acceptance, and it must be
repaired before F4's contract can be judged at all. Neither is repaired
here.

**P1-R2-F11** — the two writes are still not transactional. Same-file
and node-type checks landed; write-to-temporary-then-commit did not.

**P1-R2-F13** — the case-variant header warning is still absent.

Plus every round-1 item left open there: F4, F5, F7, F8, F9, F10's
remainder, F13's format-spec half, F15, F16, F17, F18, and R1-X3.

## Standing state

592 tests pass on Python 3.10 at the declared floor and on 3.13; the
offline scan, decontamination, attestation, provenance and all three
lock pairs are clean; ruff and mypy are clean.
