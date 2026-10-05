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
  miss -- the check that sees the written layout;
* `describe_ratio_100k` and `describe_ratio_300k`: the build gate's two
  scale nodes (the R2 design, section 7, and its skeptic, m2) -- the CPU
  time describing a column costs when it is written in a layout, over
  the time an ISO column of the same moments at the same precision
  costs, the largest of four such pairs (SPSS's DATETIME20, DB2's
  timestamp, HL7's fourteen figures, a Dutch `d-m-yyyy` date), at
  100,000 and at 300,000 rows. The bounds are 1.3 and 1.6: the skeptic
  measured the prototype's layouts costing 7 to 10 per cent more a cell
  each time the rows tripled while ISO stayed flat, so the larger node
  is what a million rows is projected from. Both times are taken in
  this process, side by side, so the ratio is judged on any machine.

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
import gc
import io
import json
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures  # noqa: E402
import kpi_rules  # noqa: E402
import layout_spellings as spellings  # noqa: E402

from synthtwin import parsing, taxonomy  # noqa: E402
from synthtwin.cli import main as cli  # noqa: E402

RUNS = ((1000, (0, 1, 2)), (10000, (0,)))

# THE BUILD GATE'S SCALE NODES: each layout beside the ISO spelling of the
# same moments at its own precision, and the key the largest ratio goes in.
SCALE_ROWS = ((100000, "describe_ratio_100k"), (300000, "describe_ratio_300k"))
SCALE_PAIRS = (
    ("spss_datetime20", "%Y-%m-%d %H:%M:%S"),
    ("db2_timestamp", "%Y-%m-%d %H:%M:%S.%f"),
    ("hl7_ts14", "%Y-%m-%d %H:%M:%S"),
    ("dutch_unpadded", "%Y-%m-%d"),
)
SCALE_SEED = 7


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


def _describe_seconds(cells: "list[str]") -> "tuple[float, str]":
    """CPU seconds `profile_column` takes over one column, and the format it read."""
    gc.collect()
    start = time.process_time()
    described = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    spent = time.process_time() - start
    return spent, f"{(described.details or {}).get('format', '')}"


def scale(notes: "list[str]") -> "dict[str, float]":
    """The two scale nodes: the largest layout-over-ISO ratio at each size."""
    ratios: "dict[str, float]" = {}
    for rows, key in SCALE_ROWS:
        moments = spellings.moments(rows, SCALE_SEED)
        worst = 0.0
        for name, iso in SCALE_PAIRS:
            writer = spellings.SPELLINGS[name][0]
            layout_seconds, read = _describe_seconds([writer(moment) for moment in moments])
            iso_seconds, iso_read = _describe_seconds([moment.strftime(iso) for moment in moments])
            if not parsing.is_layout_format(read) or not iso_read.startswith("iso-"):
                notes += [f"{name} at {rows}: read as {read}, its ISO twin as {iso_read}"]
            worst = max(worst, layout_seconds / max(iso_seconds, 1e-9))
        del moments
        ratios[key] = round(worst, 2)
    return ratios


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = measure(pathlib.Path(folder))
    value: "dict[str, object]" = {key: totals[key] for key in totals}
    value.update(scale(notes))
    kpi_rules.emit(
        "K-S3-58", value, "; ".join(notes) if notes else "every spelling read, written back and checked"
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
