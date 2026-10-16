"""`python -m synthtwin`: the same command as `synthtwin` (plan P4-D397).

A person whose Python found the package but whose shell did not find the
`synthtwin` command -- the environment's script folder is not on the
search path, which is common on a fresh machine and on Windows -- can
type `python -m synthtwin` instead and reach the very same `main`, with
the same options, the same messages and the same exit codes. Before this
file existed that line failed with "'synthtwin' is a package and cannot
be directly executed".

Nothing else happens here: no import beyond the command's own module, so
what a run reaches is exactly what `synthtwin` reaches (plan P2-D1).
"""

import sys

from synthtwin.cli import main

if __name__ == "__main__":
    sys.exit(main())
