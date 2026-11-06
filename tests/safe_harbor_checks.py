"""The checks of lane SH's gate (plan P4-D427), shared by the suite and K-HZ-15's driver (plan P4-D444).

THE SUITE'S TIME (the orchestrator's rule of 2026-10-26; batch 4l OWES 3,
lane SPD): `tests/test_safe_harbor_numbers.py` took 2,705.8 s, most of it in
its 20,000-row grids. The suite keeps every 600-row case and ONE 20,000-row
case (`KEPT_AT_20000`, the floor-size proof); every other 20,000-row case
runs in `tools/measurements/kpi_safe_harbor_numbers.py` under
`kpi_run.py --slow` (K-HZ-15). Both call the checks below, so a moved case
keeps its exact check: one function, never two copies.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re

from synthtwin import asking, cli, taxonomy

import unanswered_identifier_shapes as shapes

# The one 20,000-row case of the Safe Harbor grid the suite keeps (every
# table here is written by one writer, the CSV of
# `shapes.write_safe_harbor_table`): ZIP codes of four and five figures
# and no word, read as a count and held whole.
KEPT_AT_20000 = "zip_mixed"

# The held block's validation limit at 20,000 rows (plan P4-D427, stated).
HELD_LIMITS_AT_20000 = shapes.SAFE_HARBOR_HELD_LIMITS_AT_20000
# A column held as record numbers: its real table misses the census of
# repetition its held block publishes absorbed, as every held block's
# real table does (plan P4-D401; measured on the held ZIP shapes, which
# no top-code reaches).
HELD_REAL_MISSES = {"distinct.n_distinct_by_occurrences"}
SUMMARY_LINE = "ages over 89: every value above 89 is read as 90"
MISSED = re.compile(r"^\s+(\S+) \[[^\]]+\]: MISSED", re.M)
# The padded case's one count: published numbers over the top-code.
OVER_THE_TOP_CODE = "published_over_the_top_code"


def check(seen: "dict[str, object]", kind: str, rows: int) -> None:
    """0 ZIPs, 0 ages over 89 in every file and the twin; the question put."""
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    if not (
        (rows >= 20000 and kind in HELD_LIMITS_AT_20000)
        or (rows < 20000 and kind in shapes.SAFE_HARBOR_HELD_LIMITS_AT_600)
    ):
        assert seen["validate_exit"] == 0, seen
    elif kind in shapes.AGES:
        # ...and a limit of the twin is the control table's own, never the
        # top-code's (the second repair: `ages4ph`, `agescomma`).
        assert shapes.held_limit_met(kind, seen), seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, seen
    offered = asked[0]
    assert isinstance(offered, list)
    harbor = [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]
    if kind in shapes.AGES and offered == harbor + list(asking.AGE_UNIT_ANSWERS):
        # ...a column of ages whose cells and name state no unit is asked
        # its unit inside the one question (lane SH3's repair, the
        # orchestrator's LANE SH3 RULINGS 2 (1)).
        offered = harbor
    if kind in shapes.AGES:
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        # THE SUMMARY SAYS SO (skeptic 1 of lane SH, item 11).
        assert SUMMARY_LINE in f"{seen['summary']}", seen
        # THE REAL TABLE MEETS ITS OWN DESCRIPTION, read under the top-code.
        if seen["role"] == taxonomy.ROLE_IDENTIFIER:
            assert set(MISSED.findall(f"{seen['real_quality']}")) <= HELD_REAL_MISSES, seen
        else:
            assert seen["validate_real_exit"] == 0, seen
        assert (
            offered == harbor and seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED]
            and "THE SAFE HARBOR QUESTION" in f"{seen['screen']}"
        ) or (
            asking.ANSWER_IDENTIFIER in offered
            and seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
            and seen["role"] == taxonomy.ROLE_IDENTIFIER
        ), seen
    else:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        # ONE QUESTION A COLUMN: the Safe Harbor question, or the question
        # offering `identifier` already put, which holds it meanwhile.
        assert (
            offered == harbor and seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES]
        ) or (
            asking.ANSWER_IDENTIFIER in offered
            and seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
        ), seen


def check_answered(seen: "dict[str, object]", kind: str) -> None:
    """Items 1 and 6 of the second repair: no other answer frees an age over 89 or a ZIP.

    NAACCR's Age at Diagnosis answered `measurement` printed 91 to 105
    and its twin wrote 606 cells over 90, and answered `code` 93 and 100
    to 105 with 572 cells over 90; ZIP codes answered `measurement`,
    `keep` or `code` printed 40 of 40 (the third repair: `code` too, the
    orchestrator's rulings R1 and R2). Each answer is kept, the
    Safe Harbor question is the one question put, and the column is
    top-coded (ages) or held (ZIPs) until `no`.
    """
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    # ...a column of ages whose cells and name state no unit is asked its
    # unit inside the one question (lane SH3's repair, RULINGS 2 (1)).
    assert seen["asked"] in (
        [[asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]],
        [[asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES] + list(asking.AGE_UNIT_ANSWERS)],
    ) and (kind not in shapes.ZIP_KINDS or len(seen["asked"][0]) == 2), seen  # type: ignore[index, arg-type]
    if kind in shapes.ZIP_KINDS:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        assert seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES], seen
    else:
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        assert seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED], seen
        assert seen["validate_real_exit"] == 0, seen
        # THE TOP-CODE COSTS THE TWIN NO FACT: it misses what the twin of
        # the table written with every age above 89 as `090` misses, which
        # no top-code touches -- answered `measurement`, the padding and
        # styles of the unpadded `999` (at 20,000 rows) -- a generation
        # limit outside lane SH (wave6/SH/r2, wave6/SH-verify.md).
        assert seen["twin_misses"] == seen["control_twin_misses"], seen


def check_zoo_zips(seen: "dict[str, object]") -> None:
    """The third repair (ruling R1; LANE SH ADDENDA 8 and 9): the zoo's own `zip5`, answered `code`.

    On 9a333e46 its answer `code` printed 11 of 12 real ZIPs at 600 rows
    and 12 of 12 at 20,000, written on every twin cell. Now the Safe
    Harbor question follows that answer in the next run, one question at
    a time; the zoo answers it truthfully, `yes` (a place smaller than a
    state), and the column stays held: 0 real ZIPs in any file and the
    twin, `zip4`'s heads among them, and the analyst's `levels zip5`
    fails, the HIPAA price K-HZ-02 counts.
    """
    assert seen["steps"] == {"profile": 0, "answers": 0, "generate": 0, "validate": 0}, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    roles = seen["roles"]
    assert isinstance(roles, dict)
    assert roles["zip5"] == roles["zip4"] == taxonomy.ROLE_IDENTIFIER, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 2, seen
    assert asked[0][1] == asking.ANSWER_CODE, seen
    assert asked[1] == ([asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES],
                        asking.ANSWER_SAFE_HARBOR_YES), seen
    assert "levels zip5" in f"{seen['analyst']}", seen


def profile(folder: pathlib.Path, name: str, lines: "list[str]", *typed: str) -> int:
    """`synthtwin profile` on a table written from its lines, scripted and quiet; its exit."""
    table = folder / f"{name}.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
                            + list(typed))


def block(folder: pathlib.Path, name: str, column: str) -> "dict[str, object]":
    """One column's block of the description `profile` wrote."""
    document = json.loads((folder / f"{name}-profile.json").read_text(encoding="utf-8"))
    return [one for one in document["columns"] if one["name"] == column][0]


def published_numbers(described: "dict[str, object]") -> "list[float]":
    """Every number the block publishes as a value: rungs, mode, tails."""
    found: "list[float]" = []
    for key in ("percentiles", "percentiles_between"):
        rungs = described.get(key)
        if isinstance(rungs, dict):
            found += [value for value in rungs.values() if isinstance(value, (int, float))]
    mode = described.get("mode")
    if isinstance(mode, (int, float)):
        found += [mode]
    tails = described.get("tails")
    if isinstance(tails, dict):
        for side in tails.values():
            if isinstance(side, dict):
                found += [one for one in side.get("values", []) if isinstance(one, (int, float))]
    return found


def check_a_padded_cell_answered_measurement(folder: pathlib.Path, seen: "dict[str, object] | None" = None) -> None:
    """Skeptic 1, item 5: one `07` took ages answered `measurement` out of the reach (20,000 rows).

    It writes no twin: the case is the description and the questions file.
    `seen`, K-HZ-15's holder, keeps the count before the asserts judge it.
    """
    table, _real = shapes.write_safe_harbor_table(folder, "ages", 20000)
    lines = table.read_text(encoding="utf-8").splitlines() + ["P999999,07"]
    assert profile(folder, "ages_long", lines, "--measurement", "ages") == 0
    described = block(folder, "ages_long", "ages")
    if seen is not None:
        seen[OVER_THE_TOP_CODE] = sum(number > taxonomy.TOP_CODE for number in published_numbers(described))
    assert described["top_coded"] == taxonomy.TOP_CODE
    assert max(published_numbers(described)) <= taxonomy.TOP_CODE
    asked = json.loads((folder / "ages_long-questions.json").read_text(encoding="utf-8"))
    assert [entry["read_as_now"] for entry in asked["asked"] if entry["column"] == "ages"] == [
        asking.SAFE_HARBOR_TOP_CODED
    ]
