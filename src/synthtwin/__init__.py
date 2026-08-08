"""synthtwin — create a synthetic twin of your tabular data.

Same columns, same types, same distributions, same relationships, same
missing-data patterns — and no real records. Fully offline: this package contains no
construct that initiates network I/O, no subprocess execution, no native
calls, and no dynamic code loading (see SECURITY.md for the boundary
statement and how to verify it).

Status: the profiler is built -- `synthtwin profile <table>` reads a
local CSV table and writes the description the twin will be built from,
together with a plain-language summary of what was found and what of the
real table the description carries. Generation arrives in the next phase,
under the project's plan-first process.

One rule shapes this package's structure: `synthtwin.reading` is the only
module that opens the user's table. Everything else receives values that
have already been read, so the boundary between the code that touches
real data and the code that will build the twin is visible in the import
graph rather than promised in prose.
"""
