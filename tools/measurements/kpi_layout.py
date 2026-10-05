"""K-S3-58: spellings no named member read come back as written (landing R2a).

PLAN P4-D383. The thirty-nine spellings of `tests/layout_spellings.py` --
the thirty-two of the date half no named member read before R2a, and the
seven the R2 design skeptic added -- at 1,000 rows (seeds 0 to 2) and
10,000 rows (seed 0), a floor of eleven, through the real producer,
generator and checker:

* `spellings`: how many were measured (thirty-nine);
* `read`: how many were read under a layout of the closed grammar, with no
  cell left over;
* `twin_cells_unwritten`: twin cells not written exactly in the source's
  own spelling -- padding, case and marks -- or that the source's own
  `strptime` format refuses (where Python has a directive for it);
* `missed`: twins of which validation MISSES a checkable obligation;
* `iso_rewrites_held`: twins rewritten in ISO that validation does NOT
  miss -- the check that sees the written layout.

Before R2a (9cb2eb5, base 2, these thirty-nine spellings at 1,000 rows
and seed 0 through the base tree's own CLI): none read -- thirty-six
were free text, two counts and one an affixed number -- their twins were
in the source's spelling on at most 29.2 per cent of cells, by accident,
and validate exited 0 on all but one, free text publishing next to
nothing to miss.

    .venv/bin/python tools/measurements/kpi_layout.py --kpi
"""

import contextlib
import csv
import io
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures  # noqa: E402
import kpi_rules  # noqa: E402
import layout_spellings as spellings  # noqa: E402

from synthtwin import parsing  # noqa: E402
from synthtwin.cli import main as cli  # noqa: E402

RUNS = ((1000, (0, 1, 2)), (10000, (0,)))


def _quiet(argv: "list[str]") -> int:
    held = io.StringIO()
    with contextlib.redirect_stdout(held), contextlib.redirect_stderr(held):
        return cli(argv)


def _rows(path: pathlib.Path) -> "list[list[str]]":
    return list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))


def _in_iso(cell: str, items: "tuple[tuple[str, str], ...]") -> str:
    read = parsing.layout_reading(cell, items)
    if read is None:
        return cell
    canonical = read[0]
    return canonical if len(canonical) == 10 else f"{canonical[0:10]}T{canonical[11:]}"


def measure(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    """Every spelling at every size and seed; the totals and what failed."""
    totals = {
        "spellings": len(spellings.SPELLINGS),
        "read": 0,
        "twin_cells_unwritten": 0,
        "missed": 0,
        "iso_rewrites_held": 0,
    }
    notes: "list[str]" = []
    read_everywhere = {name: True for name in spellings.SPELLINGS}
    for rows, seeds in RUNS:
        for name in sorted(spellings.SPELLINGS):
            folder = home / f"{name}-{rows}"
            folder.mkdir()
            table = folder / "real.csv"
            names, built = fixtures.rows_at_the_floor("seen_at", spellings.cells(name, rows))
            table.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="\n")
            if _quiet(["profile", str(table), "--out-dir", str(folder), "--replace"]) != 0:
                read_everywhere[name] = False
                notes += [f"{name} at {rows}: not described"]
                continue
            profile = folder / "real-profile.json"
            block = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
            layout = f"{block.get('format', '')}"
            if block["role"] != "datetime" or not parsing.is_layout_format(layout) or block["n_unparsed"] != 0:
                read_everywhere[name] = False
                notes += [f"{name} at {rows}: read as {block['role']} {layout}"]
                continue
            items = parsing.layout_items(layout)
            fmt = spellings.format_of(name)
            for seed in seeds:
                out = folder / f"seed-{seed}"
                out.mkdir()
                _quiet(["generate", str(profile), "--seed", str(seed), "--out-dir", str(out), "--replace"])
                twin = out / "real-twin.csv"
                lines = _rows(twin)
                for row in lines[1:]:
                    if not row or not row[0]:
                        continue
                    if not spellings.written_as_the_source(name, row[0]) or not spellings.parses(row[0], fmt):
                        totals["twin_cells_unwritten"] += 1
                if _quiet(["validate", str(profile), "--twin", str(twin), "--out-dir", str(out), "--replace"]) != 0:
                    totals["missed"] += 1
                    notes += [f"{name} at {rows}, seed {seed}: MISSED"]
                if seed != seeds[0] or items is None:
                    continue
                for row in lines[1:]:
                    if row and row[0]:
                        row[0] = _in_iso(row[0], items)
                rewritten = out / "iso.csv"
                rewritten.write_text(fixtures.rows_to_csv(lines[0], lines[1:]), encoding="utf-8", newline="\n")
                checked = out / "iso-check"
                checked.mkdir()
                if _quiet(["validate", str(profile), "--twin", str(rewritten), "--out-dir", str(checked), "--replace"]) == 0:
                    totals["iso_rewrites_held"] += 1
                    notes += [f"{name} at {rows}: the ISO rewrite HELD"]
    totals["read"] = sum(1 for name in read_everywhere if read_everywhere[name])
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = measure(pathlib.Path(folder))
    kpi_rules.emit(
        "K-S3-58", totals, "; ".join(notes) if notes else "every spelling read, written back and checked"
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
