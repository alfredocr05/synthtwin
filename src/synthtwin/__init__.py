"""synthtwin — create a synthetic twin of your tabular data.

Same columns, same types, same row count, and the same published
behaviour of each column on its own — its distribution, its counts, and
how much of it is missing — worked out from a description of the table
rather than from its rows. Fully offline: this package contains no
construct that initiates network I/O, no subprocess execution, no native
calls, and no dynamic code loading (see SECURITY.md for the boundary
statement and how to verify it).

WHAT THE TWIN DOES NOT CARRY, STATED BEFORE ANYTHING ELSE CLAIMS MORE
(plan P2-D11, residual R-P2-3). This version builds every column on its
own and carries no cross-column structure at all: no correlation
between two columns, no formula tying one column to another, no shared
pattern of which cells are empty, and no ordering between two event
columns. Rows are treated as independent and the grain is undescribed —
the description never says what one row of the real table is — so the
twin of a repeated-measures table misdescribes the subject-level truth
even where every column of it is right on its own. Analysis code
developed on the twin RUNS, which is what the twin is for; a number
that code computes from two columns of the twin says nothing about the
real table. Cross-column structure arrives in a later phase (Phase 5),
and the report written beside every twin states both limits on every
run.

THE RECORD CLAIM, AND WHY IT IS QUALIFIED (plan P2-D11). Generation
reads no source table and samples or copies no row of one: every twin
cell is derived from the profile and the seed. That states where the
twin's values come from. It does NOT state that a twin row can never
equal a real row, and the categorical wording this package used to
carry — a flat assertion that a twin holds nothing of the user's —
said exactly that and was wrong. Allocating
published counts exactly can force a twin row to match a real one: an
11-row single-column table whose one label clears the disclosure floor
publishes that label with the count 11, so the twin holds it in all 11
rows. Nothing was copied; the arithmetic left no other answer. synthtwin
offers no formal privacy guarantee, and all three artifacts a full run
produces — the profile, the twin and the report — carry facts computed
from real data and are handled under the institution's rules for
real-derived material, never the profile alone.

Status: both halves are built. `synthtwin profile <table>` reads a
local CSV table and writes the description the twin is built from,
together with a plain-language summary of what was found and what of the
real table the description carries. `synthtwin generate <description>`
builds the twin from that description and a seed and from nothing else,
and writes it beside a report naming which published facts the twin
holds exactly, which it holds only approximately with the achieved value
beside the published one, and which it does not hold at all.

One rule shapes this package's structure: `synthtwin.reading` is the only
module that opens the user's table. Everything else receives values that
have already been read, so the boundary between the code that touches
real data and the code that builds the twin is visible in the import
graph rather than promised in prose.
"""
