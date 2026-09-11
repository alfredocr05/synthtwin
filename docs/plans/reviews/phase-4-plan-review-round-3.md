<!-- Phase 4 plan adversarial review, round 3. Reviewer: codex
(gpt-5.6-sol, high effort), 2026-08-19. Paths in this record are
repository-relative. The reviewer ran read-only and could not write
this file itself; its verdict is recorded verbatim below. Wording was
adjusted only where the repository's vocabulary scanner required it. -->

# Phase 4 plan review — round 3


Verdict: **REJECT**.

Blocking items:

- **P4-P3-F1:** Clock-time interpolation treats a circular day as linear, generating daytime observations from data clustered around midnight. Evidence: `docs/plans/phase-4-columns.md:619-648`; `CLAUDE.md:63-74`.
- **P4-P3-F2:** Fraction-width rounding occurs after existing endpoint, sign, zero, and distinctness safeguards, so it can violate EXACT-OBSERVABLE facts. Evidence: `docs/plans/phase-4-columns.md:723-748`; `docs/spec/generation-method-v1.md:652-722`, `1079-1107`; `docs/spec/profile-contract-v4.md:2058-2068`.
- **P4-P3-F3:** Affix-based sentinel eligibility can change an existing binary label column into a constant column, contradicting the plan’s universal no-regression rule. Evidence: `docs/plans/phase-4-columns.md:56-68`, `526-547`; `src/synthtwin/taxonomy.py:3713-3759`, `4518-4555`.
- **P4-P3-F4:** The four-argument hole-collision proof falsely says label roles write only published variants. Label generation also invents variants and `group-N` suppressed-level stand-ins, which can collide with a published hole spelling. Evidence: `docs/plans/phase-4-columns.md:921-940`; `docs/spec/generation-method-v1.md:1582-1643`; `src/synthtwin/generation.py:4375-4396`.

Serious items:

- **P4-P3-F5:** `resolution_mix` is required for every datetime block, but its claimed exact key vocabulary names only `iso-date` and `iso-datetime`, leaving other formats without a conforming representation. Evidence: `docs/plans/phase-4-columns.md:675-683`, `1025-1037`; `docs/spec/profile-contract-v4.md:914-926`.
- **P4-P3-F6:** The day-first remark shapes do not partition unequal evidence in both directions. A column with 97 ambiguous, two day-only, and one month-only cells is both evidence-decided and internally contradictory, but the conflict shape is tied to a declaration-broken tie. Evidence: `docs/plans/phase-4-columns.md:768-785`; `docs/plans/phase-1-profiler.md:368-379`.
- **P4-P3-F7:** First-row evidence is not specified for affixed-number or clock columns. A headerless column of unique prices or clock times can still lose its first record as a presumed header before the new taxonomy runs. Evidence: `docs/plans/phase-4-columns.md:448-464`, `1422-1426`; `src/synthtwin/reading.py:93-121`, `501-523`.

Round-2 repair status:

- P4-P2-F1: **NARROWED**
- P4-P2-F2: **NARROWED**
- P4-P2-F3: **CLOSED**
- P4-P2-F4: **CLOSED**
- P4-P2-F5: **NARROWED**
- P4-P2-F6: **CLOSED AS FRAMED**, with fresh P4-P3-F3
- P4-P2-F7: **CLOSED**
- P4-P2-F8: **CLOSED**
- P4-P2-F9: **STILL OPEN**, through P4-P3-F4
- P4-P2-F10: **CLOSED**
- P4-P2-F11: **CLOSED**

Checks completed:

- Entire revision-3 plan and all eleven repair claims.
- Ratified Phase 1–3 plans, the profile contract v4/v5, generation and validation methods.
- All requested shipped modules and guard machinery.
- Statistical, misrouting, privacy, determinism, settings, versioning, seal, migration, and acceptance-criteria attacks.
- Disposition seal: current.
- Draft exact-list and governing-surface assertions: passed by direct invocation.
- Staged whitespace check: passed.
- Tracked-tree decontamination scan: clean.
- Ordinary pytest could not start because the read-only environment had no writable temporary directory; no pytest result is claimed.