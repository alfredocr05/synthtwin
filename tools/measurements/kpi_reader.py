"""K-S3-52: Excel's hour and the 12-hour clock come back as written (landing T1).

PLAN P4-D370. The twenty spellings of `tests/clock_spellings.py` -- eleven
slashed stamps, seven clocks alone and the two all-midnight exports -- at
1,000 rows (seeds 0 to 2) and 10,000 rows (seed 0), a floor of eleven,
through the real producer, generator and checker:

* `spellings`: how many were measured (twenty);
* `read`: how many were read -- a date and time or a clock time, with no
  cell left over;
* `twin_cells_unread`: twin cells the source's own `strptime` format
  refuses (for the two dotted markers, which Python has no directive
  for, cells that do not wear the published style);
* `missed`: twins of which validation MISSES a checkable obligation;
* `rewrites_held`: twins rewritten in the two-figure 24-hour clock that
  validation does NOT miss -- the check that sees the written clock.

Before T1 (668f276, the designer's baseline and its skeptic's): none of
the twenty read; the one-figure hours read 758 of 1,000 (hours 10 to 23
only), every AM/PM spelling 0, and of the twins only the clock-alone
`h:mm` and `h:mm:ss` parsed at all, 255 and 165 of 1,000 by accident.

    .venv/bin/python tools/measurements/kpi_reader.py --kpi
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

import clock_spellings as spellings  # noqa: E402
import fixtures  # noqa: E402
import kpi_rules  # noqa: E402

from synthtwin import parsing  # noqa: E402
from synthtwin.cli import main as cli  # noqa: E402

RUNS = ((1000, (0, 1, 2)), (10000, (0,)))


def _quiet(argv: "list[str]") -> int:
    held = io.StringIO()
    with contextlib.redirect_stdout(held), contextlib.redirect_stderr(held):
        return cli(argv, small_tables_refused=False)


def _column(path: pathlib.Path) -> "list[list[str]]":
    return list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))


def _style(block: "dict[str, object]") -> str:
    if block["role"] == "time_of_day":
        return parsing.clock_style_of(f"{block['clock_form']}")
    for word in block["datetime_separators"]:
        style = parsing.stamp_style(f"{word}")
        if style is not None:
            return style
    return parsing.DEFAULT_CLOCK_STYLE


def _half(cell: str, kind: str) -> str:
    return parsing.stamp_halves(cell)[1] if kind == "stamp" else cell


def _wears(cell: str, kind: str, style: str) -> bool:
    parts = parsing.clock_parts(_half(cell, kind))
    if parts is None:
        return False
    second = parsing.clock_second(parts, parsing.clock_face(style))
    return second is not None and parsing.written_clock(second, parts[3], style) == _half(cell, kind)


def measure(home: pathlib.Path) -> "tuple[dict[str, int], list[str]]":
    """Every spelling at every size and seed; the totals and what failed."""
    totals = {"spellings": len(spellings.SPELLINGS), "read": 0, "twin_cells_unread": 0, "missed": 0, "rewrites_held": 0}
    notes: "list[str]" = []
    read_everywhere = {name: True for name in spellings.SPELLINGS}
    for rows, seeds in RUNS:
        for name in sorted(spellings.SPELLINGS):
            folder = home / f"{name}-{rows}"
            folder.mkdir()
            table = folder / "real.csv"
            names, built = fixtures.rows_at_the_floor("seen_at", spellings.cells(name, rows))
            table.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="")
            if _quiet(["profile", str(table), "--out-dir", str(folder), "--replace"]) != 0:
                read_everywhere[name] = False
                notes += [f"{name} at {rows}: not described"]
                continue
            profile = folder / "real-profile.json"
            block = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
            kind = spellings.kind_of(name)
            wanted = "datetime" if kind == "stamp" else "time_of_day"
            if block["role"] != wanted or block["n_unparsed"] != 0:
                read_everywhere[name] = False
                notes += [f"{name} at {rows}: read as {block['role']}"]
                continue
            style = _style(block)
            fmt = spellings.format_of(name)
            for seed in seeds:
                out = folder / f"seed-{seed}"
                out.mkdir()
                _quiet(["generate", str(profile), "--seed", str(seed), "--out-dir", str(out), "--replace"])
                twin = out / "real-twin.csv"
                lines = _column(twin)
                for row in lines[1:]:
                    if not row or not row[0]:
                        continue
                    good = spellings.parses(row[0], fmt) if fmt is not None else _wears(row[0], kind, style)
                    if not good:
                        totals["twin_cells_unread"] += 1
                if _quiet(["validate", str(profile), "--twin", str(twin), "--out-dir", str(out), "--replace"]) != 0:
                    totals["missed"] += 1
                    notes += [f"{name} at {rows}, seed {seed}: MISSED"]
                if seed != seeds[0] or style == parsing.DEFAULT_CLOCK_STYLE:
                    continue
                for row in lines[1:]:
                    if not row or not row[0]:
                        continue
                    parts = parsing.clock_parts(_half(row[0], kind))
                    if parts is None:
                        continue
                    second = parsing.clock_second(parts, parsing.clock_face(style))
                    if second is None:
                        continue
                    clock = parsing.written_clock(second, parts[3], parsing.DEFAULT_CLOCK_STYLE)
                    row[0] = parsing.stamp_halves(row[0])[0] + clock if kind == "stamp" else clock
                rewritten = out / "rewritten.csv"
                rewritten.write_text(fixtures.rows_to_csv(lines[0], lines[1:]), encoding="utf-8", newline="")
                checked = out / "rewritten-check"
                checked.mkdir()
                if _quiet(["validate", str(profile), "--twin", str(rewritten), "--out-dir", str(checked), "--replace"]) == 0:
                    totals["rewrites_held"] += 1
                    notes += [f"{name} at {rows}: the 24-hour rewrite HELD"]
    totals["read"] = sum(1 for name in read_everywhere if read_everywhere[name])
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = measure(pathlib.Path(folder))
    kpi_rules.emit(
        "K-S3-52", totals, "; ".join(notes) if notes else "every spelling read, written back and checked"
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
