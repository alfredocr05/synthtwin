"""Gate file of lane STATS-A (batch 4zz): a made-up run of figures at a named width is written at that width.

A key written as letters and two groups of figures (`AC-2022-600123`: the description names runs of four and of six
figures, `figure_openings`) is described as free text, and its twin writes made-up keys in its published form whose
runs of figures the generator renames so none is, or holds, a real run (`generation._renamed_run`, plan P4-D442).

THE DEFECT (the 302-column table, `tests/wide_table.py`'s col_292, at 20,000 rows): the walk wrote a run anew at the
NARROWEST width named alone. The six-figure groups, often led by a nought and so named by their five merged figures,
were written as three figures padded by noughts until that room was spent, then as noughts alone, then seven to twelve
figures wide: 15,402 of 20,000 twin cells left the published form, and validate missed the column's length (largest,
mean, median) and its one published form.

WHAT IT HOLDS (each clause red on its mutant, the new step (2b) of `_renamed_run` taken out):

* every twin cell of such a key is written in its one published form and at its one length, validate missing
  nothing of the column, and no twin cell is a real key or holds a real run of four figures or more;
* a made-up run of six figures, once the rooms under four figures are spent (lane HB's rules lead a run down there
  first, padded by noughts in its cell), is written at six figures, opening at every place a named width can start
  with a figure no real run of that width opens with (`_own_width_places`), so it holds no real run of either width
  whatever its filling -- never noughts alone or wider.
"""

from __future__ import annotations

import collections
import contextlib
import io
import pathlib
import random
import re

from synthtwin import cli, generation

ROWS = 3000


def _table(folder: pathlib.Path) -> "tuple[pathlib.Path, list[str]]":
    draw = random.Random(2)
    lines = ["person,sample_no,value"]
    keys: "list[str]" = []
    for row in range(ROWS):
        day = draw.randrange(1400)
        key = f"AC-{2022 + day // 365}-{600000 + row:06d}"
        keys += [key]
        lines += [f"P{1000000 + draw.randrange(600)},{key},{50 + draw.gauss(0, 9):.1f}"]
    path = folder / "keys.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path, keys


def _quiet(arguments: "list[str]") -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return int(cli.main(arguments))


def test_a_key_of_two_figure_groups_keeps_its_form_and_its_length(tmp_path: pathlib.Path) -> None:
    table, keys = _table(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    assert _quiet(["profile", str(table), "--out-dir", str(out), "--replace", "--person", "person",
                   "--identifier", "person"]) == 0
    description = str(out / "keys-profile.json")
    assert _quiet(["generate", description, "--out-dir", str(out), "--seed", "1", "--replace"]) == 0
    validated = _quiet(["validate", description, "--out-dir", str(out), "--replace"])
    report = (out / "keys-twin-quality.txt").read_text(encoding="utf-8").split("\n")
    missed: "list[str]" = []
    column = ""
    for line in report:
        if line.startswith("'") and line.rstrip().endswith("'"):
            column = line.strip()[1:-1]
        elif column == "sample_no" and line.rstrip().endswith(": MISSED"):
            missed += [line.strip()]
    assert missed == [] and validated == 0, missed
    twin = [line.split(",")[1] for line in (out / "keys-twin.csv").read_text(encoding="utf-8").split("\n")[1:] if line]
    forms = collections.Counter(re.sub(r"[A-Za-z]", "@", re.sub(r"[0-9]", "%", cell)) for cell in twin)
    assert forms == {"@@-%%%%-%%%%%%": ROWS}, forms.most_common(4)
    real_runs = {run for key in keys for run in re.findall(r"[0-9]{4,}", key)}
    assert not set(twin) & set(keys)
    assert sum(1 for cell in twin if any(run in cell for run in real_runs)) == 0


def test_a_run_of_six_figures_opens_where_no_real_run_of_four_or_six_does() -> None:
    openings = {4: "9|8|7|6|5|4|3|1", 6: "9|8|7|5|4|3|2|1"}
    places = generation._own_width_places(openings, [4, 6], 6)
    assert places == [list("9875431"), list("98765431"), list("98765431")]
    taken: "dict[str, bool]" = {}
    steps: "dict[int, int]" = {}
    written = [generation._renamed_run("12345", openings, taken, steps, generation._absent_spellings_read(()), [0, 0],
                                       0, False, 6) for _run in range(3000)]
    # ...led down under the narrowest width first, as lane HB's rules lead it (the 999 spellings of three figures and
    # fewer, padded by noughts in the cell), then at its own width, never noughts alone or wider.
    assert len(set(written)) == 3000
    assert [len(run) for run in written[:999]] == [3] * 900 + [2] * 90 + [1] * 9
    assert {len(run) for run in written[999:]} == {6}
    for run in written[999:]:
        assert run[0] in "9875431" and run[1] in "98765431" and run[2] in "98765431"
