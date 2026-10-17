"""`python -m synthtwin`: the same command as `synthtwin` (plan P4-D397).

A person whose Python found the package but whose shell did not find the
`synthtwin` command -- the environment's script folder is not on the
search path, which is common on a fresh machine and on Windows -- can
type `python -m synthtwin` instead and reach the very same `main`, with
the same options, the same messages and the same exit codes. Before this
file existed that line failed with "'synthtwin' is a package and cannot
be directly executed".

One thing comes first: the Python. The command's own module is written
for Python 3.10 and an older one stops on its syntax with a stack
trace, before `synthtwin doctor` could say what is wrong -- so this
file, which an older Python still reads, says it in words and stops
with exit code 1 (the Codex review of lane TI, item 8). Measured: Apple's
Python 3.9.6 running a source folder stopped with "TypeError:
unsupported operand type(s) for |".

Nothing else happens here: no import beyond the command's own module, so
what a run reaches is exactly what `synthtwin` reaches (plan P2-D1).
"""

import sys

if sys.version_info < (3, 10):
    sys.exit(
        "synthtwin needs Python 3.10 or later, and this is Python "
        + "%d.%d.%d" % tuple(sys.version_info)[:3]
        + ". Install a newer Python (see 'Before you start' in README.md), "
        "then run the install script again from the synthtwin folder -- "
        "sh scripts/install.sh on a Mac or Linux, scripts\\install.bat on "
        "Windows."
    )

from synthtwin.cli import main  # noqa: E402 -- after the Python check

if __name__ == "__main__":
    sys.exit(main())
