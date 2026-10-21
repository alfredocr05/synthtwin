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
never holds. A block where some cell DOES hold it cannot be told apart
from more cells, so that block is held as its cells themselves, a tuple
of text, and read back from there: the one case where a block costs
what every block cost before, and never a different cell.

WHY BYTES AND NOT THE JOINED TEXT. Python keeps a text at the width of
its widest character, so one curly quotation mark in a block of numbers
would double the whole block; UTF-8 widens only the characters that
need it. The error handler `surrogatepass` lets a lone surrogate, which
a Python text may hold, through both ways, so every text round-trips
exactly.

Guarantees, for every function here: a fixed function of its inputs,
with no random draw, no clock and no input or output of any kind;
nothing is imported but `dataclasses`. What goes in comes back: for any
list of texts, `column_cells(held_column(cells))` equals ``cells`` cell
for cell, and so does every block read in turn.
"""

import dataclasses

# THE ROWS OF ONE BLOCK. Small enough that one block of each of fifty
# columns, read back as text objects, holds a few tens of megabytes; large
# enough that a block's own bookkeeping (one record and one bytes object,
# about 150 bytes) is under a fiftieth of a byte a cell.
BLOCK_ROWS = 8192


@dataclasses.dataclass(frozen=True)
class HeldBlock:
    """The cells of one block of a column.

    `data` is the cells joined by U+0000, as UTF-8 with surrogates passed
    through, and `cells` is empty; or, where some cell of the block holds
    U+0000 itself, `data` is empty and `cells` is the cells. `count` is
    how many cells the block holds either way.
    """

    data: bytes
    cells: "tuple[str, ...]"
    count: int


@dataclasses.dataclass(frozen=True)
class HeldColumn:
    """One finished column of the twin, its blocks in row order."""

    blocks: "tuple[HeldBlock, ...]"
    count: int


def _listed(cells: "list[str]") -> "list[str]":
    """The cells as a list of their own, for the join (the offline scan's rule)."""
    return [cell for cell in cells]


def held_block(cells: "list[str]") -> HeldBlock:
    """One block of cells, held as their joined bytes.

    Guarantees: accepts a list of texts; returns the block holding them,
    which `block_cells` reads back cell for cell. Raises TypeError where
    a cell is not text, as joining it would. No I/O of any kind.
    """
    joined = "\x00".join(_listed(cells))
    if joined.count("\x00") == len(cells) - 1:
        return HeldBlock(bytes(joined, "utf-8", "surrogatepass"), (), len(cells))
    return HeldBlock(b"", tuple(cells), len(cells))


def block_cells(block: HeldBlock) -> "list[str]":
    """The cells of one block, in row order, as a new list of texts.

    Guarantees: returns exactly the cells `held_block` was given. Raises
    nothing. No I/O of any kind.
    """
    if block.count == 0:
        return []
    if block.cells:
        return list(block.cells)
    return str(block.data, "utf-8", "surrogatepass").split("\x00")


def held_column(cells: "list[str]") -> HeldColumn:
    """A whole column held a block at a time.

    Guarantees: accepts the column's cells in row order; returns the held
    column, which `column_cells` reads back cell for cell and whose
    blocks hold `BLOCK_ROWS` cells each but the last. No I/O of any kind.
    """
    blocks: "list[HeldBlock]" = []
    for start in range(0, len(cells), BLOCK_ROWS):
        blocks += [held_block(cells[start : start + BLOCK_ROWS])]
    return HeldColumn(tuple(blocks), len(cells))


def column_cells(column: HeldColumn) -> "list[str]":
    """Every cell of a held column, in row order, as a new list of texts.

    The whole column becomes text objects again, so this is for one
    column at a time (arranging the rows, a column's own walk) and never
    for the whole twin at once. Raises nothing. No I/O of any kind.
    """
    cells: "list[str]" = []
    for block in column.blocks:
        cells += block_cells(block)
    return cells


def column_block(column: HeldColumn, index: int) -> "list[str]":
    """The cells of block ``index`` of a held column, as a new list.

    Guarantees: block ``index`` holds rows ``index * BLOCK_ROWS`` up to
    the next block's first; an index past the last block gives an empty
    list. Raises nothing. No I/O of any kind.
    """
    if index < 0 or index >= len(column.blocks):
        return []
    return block_cells(column.blocks[index])


def blocks_of(n_rows: int) -> int:
    """How many blocks a column of ``n_rows`` cells is held in."""
    return (n_rows + BLOCK_ROWS - 1) // BLOCK_ROWS


def held_bytes(column: HeldColumn) -> int:
    """The bytes of cell text a held column keeps, for the memory record.

    Counts each block's joined bytes, or the characters of a block held
    as its cells; the bookkeeping around them is not counted.
    """
    total = 0
    for block in column.blocks:
        total = total + len(block.data)
        for cell in block.cells:
            total = total + len(cell)
    return total
