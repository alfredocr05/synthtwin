# synthtwin

> **Status: pre-alpha skeleton (Phase 0).** synthtwin is **not on PyPI**
> and has **no data functionality yet**. What exists today is the public
> project skeleton and its security baseline. Every capability on this
> page is tagged **[built]** or **[planned]** so there is no ambiguity
> about which is which.

synthtwin will create a **synthetic twin** of a tabular dataset: a table
with the same shape and the same statistical behavior as yours, but
containing no real records - built entirely on your machine, with no
network access of any kind.

## What synthtwin will do [planned]

Given one table of real data, synthtwin will produce four outputs:

1. **A synthetic twin** - a table of the same shape whose columns look
   and behave statistically like the original, with zero real rows in it.
2. **A schema file** - a plain description of every column: its type, its
   range or its categories, and how the twin version of it was built.
3. **A relationships file** - the dependencies between columns that the
   profiler detected or that you declared, so the twin preserves them.
4. **A plain-language quality report** - how faithful the twin is,
   written so you can judge it without a statistics background.

## Who it is for

Researchers who work with records that must never go anywhere near AI
tooling, cloud services, or any network - and who are not programmers.
The tool is being designed to run from a single command, and every error
message is required to tell a non-programmer what happened and what to do
next.

## What exists today

- **[built]** The `synthtwin` command - prints version and status only.
- **[built]** The offline guarantee's layered checks: a strict import
  allowlist scanner for the source tree, a socket guard in the test
  suite, and a packaged build that runs with no network available at all.
- **[built]** The decontamination system: a scanner, a hashed manifest,
  and a signed attestation that together keep private-environment
  vocabulary out of this public repository (see `SECURITY.md`).
- **[built]** The data-provenance guard: no data-format file is tracked
  anywhere in the repository except a test fixture listed in the fixture
  manifest, and every such fixture must be rebuilt from its committed
  generating script and byte-compared in CI.
- **[built]** Continuous integration with a single aggregate required
  gate, and the public plans and review record in `docs/plans/`.
- **[planned]** Profiling, generation, validation, and the quality
  report - these arrive in later phases, each behind its own written
  plan and adversarial review.
- **[planned]** PyPI publication - earliest at the end of Phase 3, with
  signed, reproducible, attested releases.

## The security architecture, in plain language

**Offline by construction [built].** synthtwin's own code contains
nothing that can open a network connection, launch another program, call
native code, or load code dynamically. It accepts only local file paths,
and it is fully functional air-gapped. This is verified by source audit
plus layered automated checks - it is explicitly *not* an operating-system
sandbox. If your institution requires enforcement rather than assurance,
run synthtwin inside your own network-isolated environment; it will work
there unchanged.

**Profile and generator are separate [planned].** The future architecture
keeps the profiler and the generator apart: the profiler runs where the
real data lives and writes a profile file; the generator needs only that
profile. The real data never has to move.

**Dependencies are governed [built for Phase 0].** Phase 0 ships zero
runtime dependencies - there is nothing to audit but this repository.
When numeric libraries arrive in Phase 1, the policy distinguishes the
*direct* dependencies (declared with honest, tested lower bounds for an
ordinary `pip install`) from the *complete closure* (every package,
including build tooling and transitives, locked by hash and consumed
frozen in CI and in the supported institutional install path). Details in
`SECURITY.md`.

## Honest limits

These are design limits, stated up front so nobody discovers them late:

| Limit | What it means for you |
| --- | --- |
| One flat table at a time | synthtwin models a single table. Multi-table databases and cross-file joins are out of scope. |
| Only detected or declared structure is reproduced | The twin preserves what the profiler can see or what you explicitly declare. A pattern the profiler cannot detect, and that you did not declare, will not be in the twin. |
| No free text | Narrative or note columns are not synthesized. synthtwin will not invent sentences. |
| Small tables degrade | With few rows, the statistics the profiler measures are noisy, and the twin's fidelity drops accordingly. The quality report will say so plainly. |

## Determinism [planned]

The guarantee that will hold once generation exists, exactly as scoped:
the same profile, the same seed, the same synthtwin version, and the
same locked dependency set produce byte-identical output **on the same
platform**. Cross-platform equality
is verified empirically by golden-hash tests on every cell of the CI
matrix and is reported as a tested result - it is never promised beyond
the tested matrix. One documented consequence of the single-stream design:
changing the schema shifts the random streams that follow it at the same
seed, so byte-stability is promised only across identical inputs.

## Installing

synthtwin is **not on PyPI**. There is nothing useful to install yet. If
you want to inspect the skeleton:

```
git clone https://github.com/alfredocr05/synthtwin
cd synthtwin
pip install -e .
synthtwin --version
```

The command prints version and status only.

## License

MIT License. Copyright (c) 2026 Alfredo Camargo Rodrigues.

This work is released on the project owner's authority as non-commercial
research tooling (owner decision recorded 2026-08-07 in the Phase 0
plan). Contributions are accepted under the same license: inbound =
outbound MIT, no CLA. See `LICENSE` for the full text.

## Learn more

- `SECURITY.md` - the threat model, the offline guarantee, every named
  residual risk, and how an auditor verifies each layer.
- `CONTRIBUTING.md` - the plan-first process and the standing rules every
  change must follow.
- `docs/plans/` - the written plans and their adversarial review record.
