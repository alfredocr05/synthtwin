"""Gate file of lane LEDGER: a keyed pair's pool of rare keys is the rows its key column pools, dates held included.

THE KV3 REFUSAL (carried at batch 4zz's landing, the same on its base): at 100,000 rows of the scale harness's dense
table described with `--code n10`, the key column `n10` held 28 of its cells as blank -- values that read as dates,
held until its Safe Harbor question is answered `no` (plan P4-D446) -- and the keyed pairs read those 28 rows as
rare keys, so the value column's pool of rare keys held 8,682 rows against the key column's 8,654 pooled, and the
loader's rule KV3 refused the description at `generate`. The keyed pairs now read the key column's cells as its own
block read them (`profile._key_cells_as_described`).

WHAT IT HOLDS (red on its mutant: the key cells read raw): on a small invented long table (a test device below the
owner's table floor) whose key column writes forty dates beside its common keys and twenty rare ones, the pool holds
exactly the rows the key column pools, and the description loads.
"""

from __future__ import annotations

import pathlib
import random

import fixtures
import test_key_value as K
from synthtwin import contract


def _long_with_dated_keys() -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(11)
    rows: "list[list[str]]" = []
    for person in range(400):
        for _visit in range(3):
            rows += [[f"Q{person}", "pulse", f"{draw.randint(50, 120)}"]]
            rows += [[f"Q{person}", "resp_rate", f"{draw.randint(8, 40)}"]]
            rows += [[f"Q{person}", "pain_score", f"{draw.randint(0, 10)}"]]
        if person < 40:
            rows += [[f"Q{person}", f"2024-03-{1 + person % 28:02d}", f"{draw.randint(1, 9)}"]]
        if person < 60:
            rows += [[f"Q{person}", f"rare_question_{person // 3:02d}", f"{draw.randint(1, 9)}"]]
    return ["person_id", "item_key", "item_value"], rows


def test_the_pool_of_rare_keys_is_the_rows_the_key_column_pools(tmp_path: pathlib.Path) -> None:
    header, rows = _long_with_dated_keys()
    table = K._table(tmp_path, header, rows)
    dated: "list[str]" = []
    document = K._described(table, [], dated_values=dated, dated_held=("item_key",), safe_harbor_no=["item_value"])
    assert dated == ["item_key"]
    key = K._block(document, "item_key")
    pool = K._block(document, "item_value")["by_key"]["pool"]  # type: ignore[index]
    assert isinstance(pool, dict)
    assert key["suppressed_rows"] == 60 and key["n_missing"] == 40
    assert pool["n_present"] + pool["n_missing"] == key["suppressed_rows"]
    written = fixtures.write_profile(tmp_path, "long-profile.json", document)
    contract.load_profile(str(written))
