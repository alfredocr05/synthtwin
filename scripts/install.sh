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
# 1. finds Python 3.11 or later (python3, then python; or the one named
#    in the SYNTHTWIN_PYTHON variable);
# 2. makes a fresh private environment, `.venv`, inside the synthtwin
#    folder, so nothing else on this computer changes. An earlier one
#    there is cleared first (venv --clear), every time: a file in it is
#    never trusted because its version matches the lock -- pip skips a
#    package whose version is already in place without checking the
#    bytes on disk -- and a broken or too-old one is never reused (lane
#    TI's repair, the Codex review's items 2 and 3, the skeptic's item 3);
# 3. installs numpy and pandas from requirements-install.lock, checking
#    the hash of every file against the lock (--require-hashes). Given a
#    wheel folder it installs from that folder and nothing else
#    (--no-index), then the synthtwin wheel found there with --no-deps, so
#    the checked versions stay in place -- the same two pip commands
#    README.md's "Installing" gives by hand. Those two run with pip's
#    --isolated and PIP_CONFIG_FILE set to /dev/null, so no pip setting
#    of this computer -- a find-links or an index named in a pip.conf or
#    a PIP_ variable -- adds a place to fetch from (the Codex review of
#    lane TI, item 1). Without a wheel folder it fetches the same locked,
#    hash-checked files and installs this folder itself;
# 4. ends by running `synthtwin doctor`, whose exit code it returns.
#
# Given a wheel folder, it runs no code but the hash-checked files and
# that folder's synthtwin wheel. Without one, it also runs the packaging
# tool pip fetches to install this folder (the build backend
# pyproject.toml names, which requirements-install.lock does not pin;
# plan P4-D397 states it). It never asks for an administrator password.

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
    "$@" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' \
        >/dev/null 2>&1
}

python=""
if [ -n "${SYNTHTWIN_PYTHON:-}" ]; then
    if new_enough "$SYNTHTWIN_PYTHON"; then
        python="$SYNTHTWIN_PYTHON"
    else
        stop "SYNTHTWIN_PYTHON names $SYNTHTWIN_PYTHON, which is not Python 3.11 \
or later. Name a Python 3.11 or later there, or leave SYNTHTWIN_PYTHON unset, \
and run this script again."
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
    stop "no Python 3.11 or later was found on this computer. Install one \
(see \"Before you start\" in README.md), open a new terminal window, and run \
this script again."
fi

if ! "$python" -c 'import sys; sys.exit(0 if sys.prefix == sys.base_prefix else 1)' \
    >/dev/null 2>&1; then
    stop "the Python found, $python, belongs to a private environment that is \
switched on in this terminal window. Type deactivate, press Enter, and run \
this script again."
fi

if [ ! -f "$lock" ]; then
    stop "requirements-install.lock is missing from $here. Download the \
synthtwin folder again; the lock file is part of it."
fi

# The wheel folder is checked before anything is changed, so a mistyped
# folder leaves an earlier environment as it was.
wheel=""
if [ -n "$wheels" ]; then
    [ -d "$wheels" ] || stop "there is no folder at $wheels. Run this script \
again naming the folder that holds the wheels you copied across."
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
synthtwin wheel (synthtwin-<version>-py3-none-any.whl), and it holds $count. \
Leave exactly one there and run this script again."
fi

say "Installing synthtwin into $env_dir"
say "using $("$python" -c 'import sys; print(sys.executable, sys.version.split()[0])')"

if [ -f "$env_dir/pyvenv.cfg" ]; then
    say "Replacing the earlier private environment in $env_dir; a package you"
    say "installed into it yourself must be installed again afterwards."
fi

venv_advice="Check that the synthtwin folder is one you can save files in, \
then run this script again."
if [ "$(uname -s 2>/dev/null)" = "Linux" ]; then
    venv_advice="On Debian or Ubuntu, ask whoever looks after this computer \
to install the python3-venv package, then run this script again."
fi
"$python" -m venv --clear "$env_dir" || stop "Python could not make the \
private environment in $env_dir. $venv_advice"
venv_python="$env_dir/bin/python"

if [ -n "$wheels" ]; then
    say "from the wheel folder $wheels, with no internet"
    PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install --isolated \
        --disable-pip-version-check \
        --no-index --find-links "$wheels" \
        --require-hashes -r "$lock" \
        || stop "pip could not install numpy and pandas from $wheels with \
their hashes checked. The folder must hold the files the 'pip download' \
command in README.md fetched, for this computer's system and Python: fetch \
them again that way, then run this script again."
    PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install --isolated \
        --disable-pip-version-check \
        --no-index --no-deps "$wheel" \
        || stop "pip could not install $wheel. Put the synthtwin wheel from \
the release into the folder again, in place of this one, and run this script \
again; if it stops here again, send the lines above to whoever looks after \
synthtwin."
else
    say "from this folder, fetching the locked, hash-checked numpy and pandas"
    "$venv_python" -m pip install --disable-pip-version-check \
        --require-hashes -r "$lock" \
        || stop "pip could not install numpy and pandas. Check the internet \
connection and run this script again, or install from a wheel folder instead \
(see \"Installing\" in README.md)."
    "$venv_python" -m pip install --disable-pip-version-check \
        --no-deps -e "$here" \
        || stop "pip could not install synthtwin from $here. Download the \
synthtwin folder again and run this script again; if it stops here again, \
send the lines above to whoever looks after synthtwin."
fi

say ""
"$env_dir/bin/synthtwin" doctor
status=$?

say ""
say "synthtwin is installed. Now, in this window, and in each new terminal"
say "window, switch its private environment on first, then type the commands"
say "as README.md writes them and as synthtwin prints them:"
say "  source \"$env_dir/bin/activate\""
say "  synthtwin profile my-table.csv"
exit "$status"
