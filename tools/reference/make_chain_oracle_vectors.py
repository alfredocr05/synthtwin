"""Frozen vectors of the chain's oracle and of the moments' exact route (lane CHo, plan P4-D421).

This script NEVER imports synthtwin, numpy, pandas or a solver. It runs
`tools/reference/oracle_cases.py`, which reads contract sections 4.6b
and 4.6d and method G16 from the pages alone through
`chain_oracle.py` and `moment_oracle.py`, and writes every case with
its mutant's outcome beside it:

- the chain (BC-ARCH 10.3's list): the stated exponential and the
  keyed choice; one column's ladder through the `L0` merge; a floor-36
  family; the second red team's P2, not offered; RULE W1's confined band
  (part C), where the corrected clause fires; the moved target on
  Codex's case with the units it places in a published nought; the walk
  on 40 rows; an empty-support cell; a label child; a rule word met by
  the walk; an order rule written as `A + D`; a derived family with its
  structural zeros; a pair's implied table and dealing spread; the
  score; a whole search for the test key;
- the moments (contract 4.6d.7): Codex's reference case, the small-atom
  cell, clause (c)'s case, cases `Q` and `S`, the band of the split
  union, the one-cell refusal, exception (i), two duplicate columns,
  a correlation cell, `CF1` against the exact route, and the class
  rule's boundary.

The vectors are a pure function of the numbers and the SplitMix64 seeds
written in `oracle_cases.py`; the seed argument is accepted and ignored,
as the provenance guard's convention asks.

Usage:  python3 make_chain_oracle_vectors.py --seed 0 --out <path>
"""

import argparse
import importlib.util
import json
import os

# `pathlib` is not imported: on Python 3.11 it reaches `ntpath`, whose
# import of `_winapi` the provenance guard refuses.
HERE = os.path.dirname(os.path.abspath(__file__))


def _cases():
    spec = importlib.util.spec_from_file_location("oracle_cases", os.path.join(HERE, "oracle_cases.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def document():
    cases = _cases()
    return {
        "generated_by": "tools/reference/make_chain_oracle_vectors.py",
        "never_imports": ["synthtwin", "numpy", "pandas"],
        "pages": [
            "docs/spec/profile-contract-v6.md 4.6b, 4.6d",
            "docs/spec/generation-method-v1.md G16",
            "docs/spec/validation-method-v1.md V12.2",
        ],
        "test_key": cases.TEST_KEY.hex(),
        "chain": cases.chain_cases(),
        "moments": cases.moment_cases(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    text = json.dumps(document(), indent=1, ensure_ascii=True) + "\n"
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
