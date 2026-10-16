#!/bin/sh
# Install synthtwin on a Mac or on Linux, then check this computer
# (plan P4-D397).
#
# Run it from anywhere; it works on the synthtwin folder it sits in:
#
#   sh scripts/install.sh                  from this folder, over the internet
#   sh scripts/install.sh WHEEL_FOLDER     with no internet, from a folder of
#                                          wheels (see "Installing" in README.md)
#
# What it does, and nothing else:
#
# 1. finds Python 3.10 or later (python3, then python; or the one named
#    in the SYNTHTWIN_PYTHON variable);
# 2. makes a private environment, `.venv`, inside the synthtwin folder,
#    so nothing else on this computer changes;
# 3. installs numpy and pandas from requirements-install.lock, checking
#    the hash of every file against the lock (--require-hashes). Given a
#    wheel folder it installs from that folder and nothing else
#    (--no-index), then the synthtwin wheel found there with --no-deps, so
#    the checked versions stay in place -- the same two pip commands
#    README.md's "Installing" gives by hand. Without one it fetches the
#    same locked, hash-checked files and installs this folder itself;
# 4. ends by running `synthtwin doctor`, whose exit code it returns.
#
# It runs no code fetched from anywhere but the hash-checked files and
# this folder, and it never asks for an administrator password.

set -u

here=$(cd "$(dirname "$0")/.." && pwd)
env_dir="$here/.venv"
lock="$here/requirements-install.lock"
wheels="${1:-}"

say() {
    printf '%s\n' "$*"
}

stop() {
    say ""
    say "The installation stopped: $*"
    exit 1
}

new_enough() {
    "$@" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
        >/dev/null 2>&1
}

python=""
if [ -n "${SYNTHTWIN_PYTHON:-}" ]; then
    if new_enough "$SYNTHTWIN_PYTHON"; then
        python="$SYNTHTWIN_PYTHON"
    else
        stop "SYNTHTWIN_PYTHON names $SYNTHTWIN_PYTHON, which is not Python 3.10 or later."
    fi
else
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 && new_enough "$candidate"; then
            python="$candidate"
            break
        fi
    done
fi
if [ -z "$python" ]; then
    stop "no Python 3.10 or later was found on this computer. Install one \
(see \"Before you start\" in README.md), open a new terminal window, and run \
this script again."
fi

if [ ! -f "$lock" ]; then
    stop "requirements-install.lock is missing from $here. Download the \
synthtwin folder again; the lock file is part of it."
fi

say "Installing synthtwin into $env_dir"
say "using $("$python" -c 'import sys; print(sys.executable, sys.version.split()[0])')"

if [ ! -x "$env_dir/bin/python" ]; then
    "$python" -m venv "$env_dir" || stop "Python could not make the private \
environment in $env_dir. On Debian or Ubuntu, install the python3-venv package \
first, then run this script again."
fi
venv_python="$env_dir/bin/python"

if [ -n "$wheels" ]; then
    [ -d "$wheels" ] || stop "there is no folder at $wheels. Name the folder \
that holds the wheels you copied across."
    wheels=$(cd "$wheels" && pwd)
    wheel=""
    count=0
    for candidate in "$wheels"/synthtwin-*.whl; do
        if [ -f "$candidate" ]; then
            wheel="$candidate"
            count=$((count + 1))
        fi
    done
    [ "$count" -eq 1 ] || stop "the folder $wheels must hold exactly one \
synthtwin wheel (synthtwin-<version>-py3-none-any.whl), and it holds $count."
    say "from the wheel folder $wheels, with no internet"
    "$venv_python" -m pip install --disable-pip-version-check \
        --no-index --find-links "$wheels" \
        --require-hashes -r "$lock" \
        || stop "pip could not install numpy and pandas from $wheels with \
their hashes checked. The folder must hold the files the 'pip download' \
command in README.md fetched, for this computer's system and Python."
    "$venv_python" -m pip install --disable-pip-version-check \
        --no-index --no-deps "$wheel" \
        || stop "pip could not install $wheel."
else
    say "from this folder, fetching the locked, hash-checked numpy and pandas"
    "$venv_python" -m pip install --disable-pip-version-check \
        --require-hashes -r "$lock" \
        || stop "pip could not install numpy and pandas. Check the internet \
connection, or install from a wheel folder instead (see \"Installing\" in \
README.md)."
    "$venv_python" -m pip install --disable-pip-version-check \
        --no-deps -e "$here" \
        || stop "pip could not install synthtwin from $here."
fi

say ""
"$env_dir/bin/synthtwin" doctor
status=$?

say ""
say "synthtwin is installed. Run it by its full path, for example:"
say "  \"$env_dir/bin/synthtwin\" profile my-table.csv"
exit "$status"
