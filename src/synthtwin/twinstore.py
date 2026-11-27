"""A finished twin column held compactly (plan P4-D415, lane SG of the December plan).

WHY THIS MODULE EXISTS. `generation.generate` held the whole twin as
Python objects, both ways round: one tuple of text objects a column and
one tuple a row holding the same objects. A text object of a few
characters costs about fifty bytes beside its characters and each
pointer to it eight more, so the cells of a table of 2,000,000 rows by
50 columns took about 5.5 to 5.8 GB before the twin was written at all
(lane B0's measurement), more than twice the 2.5 GB one process may
hold. Here a finished column is held as its cells' own bytes: the cells
of a block of rows joined by one separator character into one text,
held as that text's UTF-8 bytes, so a cell costs its characters and one
byte more. Nothing about a cell changes on the way in or out.

WHAT A BLOCK IS. `BLOCK_ROWS` consecutive cells of one column. A block
is the unit everything reads a held column in: the writers walk the
twin a block of rows at a time, taking each column's block, so at most
one block of every column is ever Python text at once.

THE SEPARATOR, AND THE ONE CASE IT CANNOT SERVE. The cells of a block
are joined by the character U+0000, which a cell of an ordinary table
never holds. A column where some cell DOES hold it cannot be told apart
from more cells, so that column is held as its cells themselves, a
tuple of text, and read back from there: the one case where a column
costs what every column cost before, and never a different cell.

WHY BYTES AND NOT THE JOINED TEXT. Python keeps a text at the width of
its widest character, so one curly quotation mark in a block of numbers
would double the whole block; UTF-8 widens only the characters that
need it. The error handler `surrogatepass` lets a lone surrogate, which
a Python text may hold, through both ways, so every text round-trips
exactly.

AND WHY THE BYTES ARE PACKED (zlib, the standard library's DEFLATE, at
its fastest level). A column's cells repeat their shapes block after
block -- the same digits, the same widths, the same few labels -- and
the twin's text at 2,000,000 rows by 50 columns is about 0.9 GB as
bytes; packed, block by block, it is about 0.3 GB (2.6 to 2.9 bytes a
cell on lane B0's two tables against 6.1 and 8.6 bytes of text; lane
SG's measurement), which the per-column working sets need. DEFLATE is
lossless: `zlib.decompress(zlib.compress(raw, level))` is `raw`, byte
for byte, for every `raw`, whatever the zlib version or the level, so
no byte of the twin can depend on it. What the packing writes (whose
bytes do differ between zlib versions) never leaves the process: it is
unpacked, here, before any cell is read.

Guarantees, for every function here: a fixed function of its inputs,
with no random draw, no clock and no input or output of any kind;
nothing is imported but `dataclasses` and `zlib`, whose two functions
`compress` and `decompress` the offline scan admits in this module
alone. What goes in comes back: for any
list of texts, `column_cells(held_column(cells))` equals ``cells`` cell
for cell, and so does every block read in turn.
"""

import dataclasses
import zlib

# THE ROWS OF ONE BLOCK. Small enough that one block of each of fifty
# columns, read back as text objects, holds under a megabyte, so a
# writer walking the rows holds a block of each column and little else;
# large enough that a block's own bytes object (about forty bytes beside
# its cells) is a sixth of a byte a cell.
BLOCK_ROWS = 256

# How hard zlib packs a block: its fastest level. Packing costs about a
# tenth of a microsecond a cell and unpacking half that (0.31 s and 0.12
# s for the 2,500,000 cells of 50,000 rows of lane B0's mixed table; 12
# s to pack 2,000,000 rows by 50). The level decides how small the held
# bytes are and nothing else: what comes back out is the same at every
# level.
PACK_LEVEL = 1


@dataclasses.dataclass(frozen=True)
class HeldColumn:
    """One finished column of the twin.

    `blocks` holds each block's cells joined by U+0000, as UTF-8 with
    surrogates passed through and packed by zlib, in row order, and
    `cells` is empty; or,
    where some cell of the column holds U+0000 itself, `blocks` is empty
    and `cells` is the cells. `count` is how many cells the column holds
    either way.
    """

    blocks: "tuple[bytes, ...]"
    cells: "tuple[str, ...]"
    count: int


def _listed(cells: "list[str]") -> "list[str]":
    """The cells as a list of their own, for the join (the offline scan's rule)."""
    return [cell for cell in cells]


def held_column(cells: "list[str]") -> HeldColumn:
    """A whole column held a block at a time.

    Guarantees: accepts the column's cells in row order; returns the held
    column, which `column_cells` reads back cell for cell and whose
    blocks hold `BLOCK_ROWS` cells each but the last. Raises TypeError
    where a cell is not text, as joining it would. No I/O of any kind.
    """
    blocks: "list[bytes]" = []
    for start in range(0, len(cells), BLOCK_ROWS):
        part = cells[start : start + BLOCK_ROWS]
        joined = "\x00".join(_listed(part))
        if joined.count("\x00") != len(part) - 1:
            return HeldColumn((), tuple(cells), len(cells))
        blocks += [zlib.compress(bytes(joined, "utf-8", "surrogatepass"), PACK_LEVEL)]
    return HeldColumn(tuple(blocks), (), len(cells))


def column_block(column: HeldColumn, index: int) -> "list[str]":
    """The cells of block ``index`` of a held column, as a new list.

    Guarantees: block ``index`` holds rows ``index * BLOCK_ROWS`` up to
    the next block's first; an index past the last block gives an empty
    list. Raises nothing. No I/O of any kind.
    """
    if index < 0 or index * BLOCK_ROWS >= column.count:
        return []
    if column.cells:
        return list(column.cells[index * BLOCK_ROWS : (index + 1) * BLOCK_ROWS])
    return str(zlib.decompress(column.blocks[index]), "utf-8", "surrogatepass").split("\x00")


def column_cells(column: HeldColumn) -> "list[str]":
    """Every cell of a held column, in row order, as a new list of texts.

    The whole column becomes text objects again, so this is for one
    column at a time (arranging the rows, a column's own walk) and never
    for the whole twin at once. Raises nothing. No I/O of any kind.
    """
    if column.cells:
        return list(column.cells)
    cells: "list[str]" = []
    for index in range(len(column.blocks)):
        cells += column_block(column, index)
    return cells


def blocks_of(n_rows: int) -> int:
    """How many blocks a column of ``n_rows`` cells is held in."""
    return (n_rows + BLOCK_ROWS - 1) // BLOCK_ROWS


def held_bytes(column: HeldColumn) -> int:
    """The bytes of cell text a held column keeps, for the memory record.

    Counts each block's packed bytes, or the characters of a column held
    as its cells; the bookkeeping around them is not counted.
    """
    total = 0
    for block in column.blocks:
        total = total + len(block)
    for cell in column.cells:
        total = total + len(cell)
    return total
