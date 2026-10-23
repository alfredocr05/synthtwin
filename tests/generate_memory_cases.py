"""The twin's assembly as it stood before plan P4-D415, frozen as text, and the gate's tables.

Plan P4-D415 (lane SG) holds each finished column of the twin
compactly, places the rows a column at a time (`dialect.placed_column`,
`dialect.arranged_columns`) and writes the delimited twin's text in
pieces (`dialect.twin_pieces`). Every twin must keep its bytes. The
assembly of 8a02faa3 is kept here as fixed text, the manner of
`tests/workbook_stream_cases.py`, so a change of meaning made to the
product cannot reach the reference too:

- `ARRANGED` is `dialect.arranged` exactly as 8a02faa3 shipped it, the
  whole grid of columns held as lists;
- `PLACE_EMPTY_ROWS` is `dialect._place_empty_rows` as 8a02faa3 shipped
  it, which this landing removes;
- `TWIN_TEXT` is `dialect.twin_text` as 8a02faa3 shipped it, the text
  grown a line at a time;
- `SCHEDULES` is `dialect.spread_places`, `dialect.spread_endings` and
  `dialect.closings_in_turn` as 8a02faa3 shipped them, each laying its
  schedule out a line or a record at a time, which repair 2 walks as the
  lines ask instead (the Codex review's item 2).

They are compiled into a COPY of `dialect`'s own names, so the helpers
they call (`_empty_targets`, `_permutation`, `data_line` and the rest,
which this landing does not change) are today's. `before_bytes` feeds
them the columns the generator makes, recorded where each finished
column is handed to `dialect.placed_column`, the cells 8a02faa3 put in
its grid; `after_bytes` is the command itself.
"""

import pathlib
import random
import sys

from synthtwin import cli, contract, dialect, generation

SCHEDULES = '''
def spread_places(spread: BlankSpread) -> "tuple[BlankPlace, ...]":
    places: list[BlankPlace] = []
    span = spread.last - spread.first
    for index in range(spread.lines):
        after = spread.first
        if spread.lines > 1:
            after = spread.first + (index * span) // (spread.lines - 1)
        last = len(places) - 1
        if last >= 0 and places[last].after == after:
            places[last] = BlankPlace(after=after, lines=places[last].lines + 1, text=spread.text)
        else:
            places += [BlankPlace(after=after, lines=1, text=spread.text)]
    return tuple(places)


def spread_endings(census: "tuple[EndingRun, ...]") -> "list[str]":
    total = 0
    most = 0
    for index in range(len(census)):
        total = total + census[index].lines
        if census[index].lines > census[most].lines:
            most = index
    if not census:
        return []
    endings = [census[most].ending for _line in range(total)]
    taken = [False for _line in range(total)]
    low = 0
    for index in range(len(census)):
        if index == most:
            continue
        count = census[index].lines
        cursor = 0
        for step in range(count):
            target = ((2 * step + 1) * total) // (2 * count)
            at = max(target, cursor)
            while at < total and taken[at]:
                at = at + 1
            if at >= total:
                while low < total and taken[low]:
                    low = low + 1
                at = low
            taken[at] = True
            endings[at] = census[index].ending
            cursor = at + 1
    return endings


def closings_in_turn(form: Dialect, n_rows: int) -> "list[bool]":
    if not form.rows_trailing_delimiter:
        return [False for _row in range(n_rows)]
    if not form.rows_closing_runs:
        return [form.rows_closing_quoted for _row in range(n_rows)]
    found: "list[bool]" = []
    last = False
    for run in form.rows_closing_runs:
        last = run.ending == CLOSING_QUOTED
        found += [last for _line in range(min(run.lines, n_rows - len(found)))]
    found += [last for _row in range(n_rows - len(found))]
    return found
'''

TWIN_TEXT = '''
def twin_text(
    names: "tuple[str, ...]",
    rows: "tuple[tuple[str, ...], ...]",
    write_header: bool,
    form: Dialect,
) -> str:
    """The whole twin in its source's written form, as text.

    Guarantees:

    - Inputs: the column names, the rows in their final order, whether
      a header is written, and the form.
    - Determinism: a fixed function of those, on every platform; the
      line endings are written into the text, so the caller writes it
      without translating any.
    - Errors raised: none.
    - Boundary: nothing is read and nothing is written.

    The lines are written in file order: the separator hint, the
    preamble, the header, the metadata rows, then the data records with
    the blank lines standing where the form places them. Each line takes
    the next ending from the form's runs; the last takes none where the
    source's last line had none. A byte-order mark leads where the form
    has one, and the end-of-file mark follows where it has one.
    """
    lines: list[str] = []
    if form.separator_line:
        lines += ["sep=" + form.delimiter]
    for before in form.preamble:
        for _line in range(before.lines):
            lines += [preamble_line(before)]
    if write_header:
        lines += [header_line(names, form)]
    for row in form.header_rows:
        alone = len(row) == 1
        parts = [
            written_field(cell, form.header_rows_quoting, form, alone)
            for cell in row
        ]
        lines += [_joined(parts, form)]
    blank_places = form.blank_lines
    if form.blank_lines_spread is not None:
        blank_places = spread_places(form.blank_lines_spread)
    blank_at = 0
    # Each record closed as the source closed it (plan P4-D387, lane R6).
    quoted_closings = closings_in_turn(form, len(rows))
    for index in range(len(rows)):
        while blank_at < len(blank_places) and blank_places[blank_at].after == index:
            place = blank_places[blank_at]
            for _line in range(place.lines):
                lines += [place.text]
            blank_at = blank_at + 1
        written = data_line(rows[index], form)
        if quoted_closings[index]:
            written = written + _closing_quotes(form)
        lines += [written]
    while blank_at < len(blank_places):
        place = blank_places[blank_at]
        for _line in range(place.lines):
            lines += [place.text]
        blank_at = blank_at + 1
    endings: list[str] = []
    for run in form.line_endings:
        for _line in range(run.lines):
            endings += [ENDING_TEXT[run.ending]]
    if form.line_endings_spread:
        endings = [ENDING_TEXT[word] for word in spread_endings(form.line_endings_spread)]
    text = _MARK if form.byte_order_mark else ""
    for index in range(len(lines)):
        text = text + lines[index]
        if index < len(endings):
            text = text + endings[index]
        elif index < len(lines) - 1 or form.final_line_ending:
            text = text + _LF
    if form.end_of_file_mark:
        text = text + _END_OF_FILE
    return text

'''

ARRANGED = '''
def arranged(
    columns: "list[tuple[str, ...]]", form: Dialect, n_rows: int
) -> "list[tuple[str, ...]]":
    """A twin's columns with its rows placed where the form says they stand.

    Guarantees:

    - Inputs: the finished columns, the form, the number of rows.
    - What moves: WHOLE ROWS, when the form names a sorted column --
      every column is permuted together, so no column's cells and no
      pair of columns' joint cells change -- and single cells WITHIN one
      column, to put the published number of all-empty records in their
      places and to leave no other record empty. Moving cells within a
      column changes no fact of that column, and the twin carries no
      structure between columns for such a move to break (CLAUDE.md,
      what the twin carries today). A row-sequence column is written in
      place last, so it reads 0, 1, 2, ... or 1, 2, 3, ... whatever
      moved.
    - Determinism: no random draw; a fixed function of the inputs.
    - Errors raised: none.
    """
    width = len(columns)
    if not width or not n_rows:
        return columns
    grid = [list(column) for column in columns]
    order = form.row_order
    empties = form.empty_rows_leading + form.empty_rows_interior + form.empty_rows_trailing
    targets = [False for _row in range(n_rows)]
    if width >= 2 and (empties or not order.column):
        _place_empty_rows(grid, form, n_rows)
        targets = _empty_targets(form, n_rows)
    if order.column and order.column <= width:
        # The records holding nothing stay where they were placed, and
        # the others are sorted into the rows around them.
        free = [row for row in range(n_rows) if not targets[row]]
        key = grid[order.column - 1]
        placed = _permutation([key[row] for row in free], order, len(free))
        for place in range(width):
            column = grid[place]
            moved = list(column)
            for index in range(len(free)):
                moved[free[index]] = column[free[placed[index]]]
            grid[place] = moved
    for index in range(width):
        if index < len(form.columns) and form.columns[index].sequence_start >= 0:
            grid[index] = sequence_cells(form.columns[index].sequence_start, n_rows)
    return [tuple(column) for column in grid]

'''

PLACE_EMPTY_ROWS = '''
def _place_empty_rows(grid: "list[list[str]]", form: Dialect, n_rows: int) -> None:
    """Swap cells within columns so exactly the target rows are all empty.

    First every target row is emptied: a cell holding something is
    exchanged for an empty cell of the same column from a row that is not
    a target. Then every other row left with nothing in it is given a
    cell: a cell holding something is exchanged into it from a row that
    keeps something else. Both walks are linear in the cells they touch.
    """
    width = len(grid)
    targets = _empty_targets(form, n_rows)
    for place in range(width):
        column = grid[place]
        donor = 0
        for row in range(n_rows):
            if not targets[row] or _holds_nothing(column[row]):
                continue
            while donor < n_rows and (
                targets[donor] or not _holds_nothing(column[donor])
            ):
                donor = donor + 1
            if donor >= n_rows:
                break
            column[row], column[donor] = column[donor], column[row]
            donor = donor + 1
    filled = [0 for _row in range(n_rows)]
    for place in range(width):
        column = grid[place]
        for row in range(n_rows):
            if not _holds_nothing(column[row]):
                filled[row] = filled[row] + 1
    giver = [0 for _place in range(width)]
    for row in range(n_rows):
        if targets[row] or filled[row]:
            continue
        for place in range(width):
            column = grid[place]
            source = giver[place]
            while source < n_rows and (
                targets[source]
                or _holds_nothing(column[source])
                or filled[source] < 2
            ):
                source = source + 1
            giver[place] = source
            if source >= n_rows:
                continue
            column[row], column[source] = column[source], column[row]
            filled[row] = filled[row] + 1
            filled[source] = filled[source] - 1
            break

'''


def _as_built_namespace() -> dict:
    """`dialect`'s names with the frozen functions compiled over them."""
    names = dict(vars(dialect))
    for text, label in (
        (SCHEDULES, "<as built schedules>"),
        (TWIN_TEXT, "<as built twin_text>"),
        (ARRANGED, "<as built arranged>"),
        (PLACE_EMPTY_ROWS, "<as built _place_empty_rows>"),
    ):
        exec(compile(text, label, "exec"), names)  # noqa: S102
    return names


AS_BUILT = _as_built_namespace()


def recorded_columns(described: contract.Profile, seed: int) -> "list[tuple[str, ...]]":
    """The finished columns `generate_held` makes, before any row is placed.

    Each is recorded where it is handed to `dialect.placed_column`: the
    cells 8a02faa3 appended to its grid as `tuple(spelled)`.
    """
    seen: "list[tuple[str, ...]]" = []
    shipped = dialect.placed_column

    def recording(state: dialect.Arranging, cells: "list[str]") -> "list[str]":
        nonlocal seen
        seen = seen + [tuple(cells)]
        return shipped(state, cells)

    dialect.placed_column = recording  # type: ignore[assignment]
    try:
        generation.generate_held(described, seed)
    finally:
        dialect.placed_column = shipped  # type: ignore[assignment]
    return seen


def before_text(described: contract.Profile, seed: int) -> str:
    """The twin's whole text as 8a02faa3 assembled it from the same columns."""
    columns = recorded_columns(described, seed)
    placed = AS_BUILT["arranged"](columns, described.source.dialect, described.n_rows)
    rows = tuple(
        tuple([placed[place][row] for place in range(len(placed))])
        for row in range(described.n_rows)
    )
    return AS_BUILT["twin_text"](
        tuple([column.name for column in described.columns]),
        rows,
        described.source.header_source == "file",
        described.source.dialect,
    )


def before_bytes(described: contract.Profile, seed: int) -> bytes:
    """`before_text` in the twin's own encoding, the bytes 8a02faa3 wrote."""
    codec = dialect.WRITING_CODECS[described.source.encoding]
    return before_text(described, seed).encode(codec)


def run(argv: "list[str]") -> int:
    """One synthtwin command in this process; its exit code."""
    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def described(folder: pathlib.Path, name: str, data: bytes, flags: "tuple[str, ...]" = ()) -> pathlib.Path:
    """``data`` written as ``name`` and described by the real producer; the description's path."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / name
    table.write_bytes(data)
    code = run(["profile", str(table), "--out-dir", str(folder), "--replace"] + list(flags))
    assert code == 0, (name, code)
    return folder / f"{table.stem}-profile.json"


def after_bytes(description: pathlib.Path, seed: int) -> bytes:
    """The twin the command writes today, read back from its file."""
    folder = description.parent / f"after-{seed}"
    folder.mkdir(exist_ok=True)
    code = run(
        ["generate", str(description), "--out-dir", str(folder), "--seed", f"{seed}", "--replace"]
    )
    assert code == 0, (description, code)
    found = [path for path in folder.iterdir() if "-twin." in path.name]
    assert len(found) == 1, found
    return found[0].read_bytes()


# -- the seeded tables ----------------------------------------------------


def wide_table(n_rows: int, width: int = 50, seed: int = 20261021) -> bytes:
    """A seeded wide table: numbers, labels, dates, stamps, codes and holes.

    No value comes from a real table. A fifth of the columns hold empty
    cells, so the twin's all-empty records and the cells given back to
    rows no column fills both have work to do.
    """
    draw = random.Random(seed)
    names = [f"c{index:02d}" for index in range(width)]
    lines = [",".join(names)]
    for _row in range(n_rows):
        cells: "list[str]" = []
        for index in range(width):
            kind = index % 6
            if index % 5 == 4 and draw.random() < 0.3:
                cells += [""]
            elif kind == 0:
                cells += [f"{draw.gauss(50, 12):.2f}"]
            elif kind == 1:
                cells += [draw.choice(("red", "green", "blue", "grey"))]
            elif kind == 2:
                cells += [f"2020-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"]
            elif kind == 3:
                cells += [
                    f"2021-03-{draw.randint(1, 28):02d} "
                    f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}"
                ]
            elif kind == 4:
                cells += [f"{draw.randint(0, 400)}"]
            else:
                cells += [f"K{draw.randint(100, 999)}"]
        lines += [",".join(cells)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def sorted_table(n_rows: int, seed: int = 20261022) -> bytes:
    """A seeded table sorted by its first column, with empty records among its rows."""
    draw = random.Random(seed)
    rows = sorted(
        [
            [f"{draw.randint(1, 900)}", draw.choice(("a", "b", "c")), f"{draw.random():.3f}"]
            for _row in range(n_rows)
        ],
        key=lambda row: int(row[0]),
    )
    lines = ["key,group,share"]
    for index in range(n_rows):
        if index % 37 == 5:
            lines += [",,"]
        lines += [",".join(rows[index])]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


def sparse_table(n_rows: int, seed: int = 20261023) -> bytes:
    """A seeded narrow table whose three columns are each half empty, written with semicolons."""
    draw = random.Random(seed)
    lines = ["\ufeffalpha;beta;gamma"]
    for _row in range(n_rows):
        cells = [
            "" if draw.random() < 0.5 else f"{draw.randint(1, 60)}",
            "" if draw.random() < 0.5 else draw.choice(("yes", "no")),
            "" if draw.random() < 0.5 else f"{draw.gauss(0, 1):.3f}",
        ]
        lines += [";".join(cells)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def text_table(n_rows: int, seed: int = 20261024) -> bytes:
    """A seeded table of free text, codes, a ward and record numbers.

    Its text columns (`note`, `dx`) take their cells from the column's
    plan, the route the other seeded tables do not reach (repair 1 of
    lane SG): reversing a plan's cells moved none of their bytes.
    """
    draw = random.Random(seed)
    words = (
        "patient", "reports", "mild", "pain", "since", "monday", "no", "fever",
        "stable", "review", "in", "two", "weeks", "dressing", "changed", "wound",
        "clean", "dry", "advised", "rest",
    )
    lines = ["note,dx,ward,record"]
    for _row in range(n_rows):
        note = " ".join(draw.choice(words) for _word in range(draw.randint(2, 6)))
        dx = f"{draw.choice('EIJKN')}{draw.randint(10, 99)}.{draw.randint(0, 9)}"
        ward = draw.choice(("north", "south", "east"))
        record = f"RC{draw.randint(0, 9999999):07d}"
        lines += [",".join([note, dx, ward, record])]
    return ("\n".join(lines) + "\n").encode("utf-8")
