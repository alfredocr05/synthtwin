"""K-P2-07: approximated statistics stay inside their stated windows at twenty seeds.

`tests/test_p2c1f4_approximation_bounds.py` runs one seed. This builds
the every-role table at the shipped settings (record_code declared, the
pressure column a measurement), generates it at seeds 0 to 19, and
counts every approximated fact the twin's report places outside its
window, and every obligation its quality report MISSED. About a minute.

    .venv/bin/python tools/measurements/kpi_windows_20_seeds.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
from synthtwin import generation, rendering  # noqa: E402

kpi_rules.guard_this_tree()
facts = outside = missed = 0
with tempfile.TemporaryDirectory() as folder:
    described = kpi_shapes.every_role(pathlib.Path(folder), None)
    for seed in range(20):
        twin = generation.generate(described.loaded, seed)
        facts += len(twin.approximations)
        outside += sum(1 for fact in twin.approximations if not fact.inside)
        found = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
        missed += len(found)
        print(f"seed {seed}: {len(twin.approximations)} approximated facts, missed {found}", flush=True)
kpi_rules.emit("K-P2-07", {"facts": facts, "outside": outside, "missed": missed, "seeds": 20})
