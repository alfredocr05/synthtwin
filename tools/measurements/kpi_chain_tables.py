"""K-S6-08, the chain's tables part: no count of 1 to 10 any description of the draw can publish fixes or bounds (plan P4-D418).

Lane CHa's stamp of `K-S6-08` on the fixtures of the design's section 2.7
(contract 4.6b.10), by exact enumeration at the floor of 11
(`tests/chain_enumeration.py`):

- THE MARGIN-SET SCAN: every 2 x 2 x 2 table of the design's 24 margin sets
  (n from 100 to 124, every one-way total of the value 1 at least 2f,
  `n3d.py`'s seed 3), every description the draw can publish from each
  (every eligible option of every step, the product's RULES W3, NE, the
  floor and W1), its preimage streamed: `descriptions_leaking`, target 0;
- RULE W1'S PART C recast as the product's filter: `part_c_leaking`, target
  0; its mutant, the version 2.2 merge after the draw, must leak
  (`part_c_mutant_leaking` above 0, the case's discrimination);
- THE MIRROR: on `MIRROR_TABLES` tables sampled across the sets, the
  producer's own search reaches exactly the scan's descriptions
  (`mirror_mismatches`, target 0);
- THE STATED LIMITS, reported and never passed: two descriptions of one
  table (`two_key_pairs_leaking` of `two_key_pairs`, on the three smallest
  sets), and two different tables under one name (the design check's
  figure, cited: the product's keyed run of it is owed). Two tables under
  DIFFERENT names draw independent words, so a pair's preimage is the
  product of the two single ones and leaks exactly where a single
  description does: `different_names_leaking` equals 0 where
  `descriptions_leaking` does.

    PYTHONPATH=src:tests python tools/measurements/kpi_chain_tables.py --kpi

About 15 to 25 minutes on the reference machine; one process, a few tens of
megabytes.
"""

import json
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import chain_enumeration as enumeration  # noqa: E402

SETS = 24
SEED = 3
MIRROR_TABLES = 200
SAME_NAME = "136 of 29,018 targeted pairs (design check V23-repair, out/named-keys-seed3.json, cited)"


def measure() -> "dict[str, object]":
    started = time.time()
    sets = enumeration.scan_sets(100, 124, SETS, SEED)
    by_size = sorted(sets, key=lambda one: len(enumeration.tables_with_margins(*one)))
    ordered = by_size[:3] + [one for one in sets if one not in by_size[:3]]
    scan = enumeration.margin_scan(ordered, pairs_on=3)
    part_c = enumeration.part_c("filter")
    mutant = enumeration.part_c("merge")
    draw = random.Random(SEED)
    mismatches = 0
    for _sample in range(MIRROR_TABLES):
        n, a1, b1, c1 = sets[draw.randrange(len(sets))]
        tables = enumeration.tables_with_margins(n, a1, b1, c1)
        table = tables[draw.randrange(len(tables))]
        scales = [enumeration.binary_scale("a", n - a1, a1), enumeration.binary_scale("b", n - b1, b1), enumeration.binary_scale("c", n - c1, c1)]
        if not enumeration.mirror_agrees(table, scales):
            mismatches += 1
    return {
        "descriptions_leaking": scan["descriptions_leaking"],
        "descriptions": scan["descriptions"],
        "tables": scan["tables"],
        "margin_sets": scan["margin_sets"],
        "part_c_leaking": part_c["descriptions_leaking"],
        "part_c_descriptions": part_c["descriptions"],
        "part_c_mutant_leaking": mutant["descriptions_leaking"],
        "mirror_tables": MIRROR_TABLES,
        "mirror_mismatches": mismatches,
        "different_names_leaking": scan["descriptions_leaking"],
        "two_key_sets": scan["two_key_sets"],
        "two_key_pairs": scan["two_key_pairs"],
        "two_key_pairs_leaking": scan["two_key_pairs_leaking"],
        "same_name": SAME_NAME,
        "seconds": round(time.time() - started, 1),
    }


def main() -> int:
    value = measure()
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-08", "value": value, "detail": "the chain's tables part (lane CHa)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
