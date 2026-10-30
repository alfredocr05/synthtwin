#!/bin/sh
# Install synthtwin on a Mac or on Linux from its offline bundle, then
# check this computer (plans P4-D397 and P4-D416).
#
# The bundle is the only way synthtwin is installed (the owner's D3 of
# 2026-10-20). Unzip it, then, in its folder:
#
#   sh scripts/install.sh
#
# It takes no folder and needs no internet: it installs from the
# bundle's own `wheelhouse` folder and nothing else.
#
# What it does, and nothing else:
#
# 1. finds a Python the bundle serves, 3.11 to 3.14: python3, then
#    python, then python3.14, python3.13, python3.12 and python3.11 (or
#    the one named in the SYNTHTWIN_PYTHON variable), so a Python 3.15
#    beside a 3.14 takes the 3.14; it takes only CPython's usual build,
#    so a free-threaded python3 (3.14t) beside a usual python3.14 takes
#    the usual one (Codex's review of lane DEP-2, item 3); and says in
#    plain words what to do when there is none (lane DEP-2's skeptic,
#    item 2);
# 2. runs scripts/check_bundle.py with that Python, which checks every
#    file of the bundle against SHA256SUMS, every library wheel against
#    the hashes requirements-install.lock pins, that the lock names no
#    place to fetch from, and that the bundle was made for this system
#    (its chip and, on a Mac, its macOS) and this Python -- before
#    anything on this computer is changed, and that the wheelhouse holds
#    a file this computer can take for every library the lock asks for,
#    so an incomplete bundle stops before an earlier environment is
#    replaced (Codex's review of lane DEP-2, item 5);
# 3. makes a fresh private environment, `.venv`, inside the bundle's
#    folder, so nothing else on this computer changes. An earlier one
#    there is cleared first (venv --clear), every time: a file in it is
#    never trusted because its version matches the lock -- pip skips a
#    package whose version is already in place without checking the
#    bytes on disk -- and a broken or too-old one is never reused (lane
#    TI's repair, the Codex review's items 2 and 3, the skeptic's item 3);
# 4. installs the libraries from the bundle's wheelhouse and nothing
#    else (--no-index), the hash of every file checked against the lock
#    (--require-hashes), then synthtwin by its name from the same folder
#    with --no-deps, so the checked versions stay in place. synthtwin is
#    named, not its file: pip reads a ';' in a file's path as the start
#    of a condition, so a bundle under a folder named like `notes;old`
#    stopped there (lane DEP-2's verify, item 3). Both pip commands
#    run with pip's --isolated and PIP_CONFIG_FILE set to /dev/null, so
#    no pip setting of this computer -- a find-links or an index named
#    in a pip.conf or a PIP_ variable -- adds a place to fetch from (the
#    Codex review of lane TI, item 1). There is no other way in: when a
#    file is missing, pip stops and so does this script;
# 5. ends by running `synthtwin doctor`, whose exit code it returns.
#
# It runs no code but the checked files of the bundle. It never asks
# for an administrator password.

set -u

here=$(cd "$(dirname "$0")/.." && pwd)
env_dir="$here/.venv"
lock="$here/requirements-install.lock"
wheels="$here/wheelhouse"

say() {
    printf '%s\n' "$*"
}

stop() {
    say ""
    say "The installation stopped: $*"
    exit 1
}

if [ "$#" -ne 0 ]; then
    stop "this script takes no folder: it installs from the wheelhouse \
folder of the bundle it sits in. Type sh scripts/install.sh with nothing \
after it, in the bundle's folder, and run it again."
fi

served() {
    "$@" -c 'import sys, sysconfig; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 14) and sys.implementation.name == "cpython" and not sysconfig.get_config_var("Py_GIL_DISABLED") else 1)' \
        >/dev/null 2>&1
}

too_old_advice="Install Python 3.14 from python.org (choose Downloads, then the \
newest Python 3.14 release; INSTALL.txt in this folder says how), open a new \
terminal window, and run this script again."

python=""
found=""
if [ -n "${SYNTHTWIN_PYTHON:-}" ]; then
    if served "$SYNTHTWIN_PYTHON"; then
        python="$SYNTHTWIN_PYTHON"
    else
        stop "SYNTHTWIN_PYTHON names $SYNTHTWIN_PYTHON, which is not Python 3.11, \
3.12, 3.13 or 3.14 (the usual build from python.org). Name one of those there, \
or leave SYNTHTWIN_PYTHON unset, and run this script again."
    fi
else
    for candidate in python3 python python3.14 python3.13 python3.12 python3.11; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if served "$candidate"; then
                python="$candidate"
                break
            fi
            if [ -z "$found" ]; then
                found=$("$candidate" -c 'import sys, sysconfig; print("%d.%d" % sys.version_info[:2] + ("" if sys.implementation.name == "cpython" else " (" + sys.implementation.name + ")") + (" (free-threaded)" if sysconfig.get_config_var("Py_GIL_DISABLED") else ""))' \
                    2>/dev/null)
            fi
        fi
    done
fi
if [ -z "$python" ] && [ -n "$found" ]; then
    stop "this computer's Python is $found, and this synthtwin bundle serves \
Python 3.11, 3.12, 3.13 and 3.14. $too_old_advice"
fi
if [ -z "$python" ]; then
    stop "no Python 3.11, 3.12, 3.13 or 3.14 was found on this computer. \
$too_old_advice"
fi

if ! "$python" -c 'import sys; sys.exit(0 if sys.prefix == sys.base_prefix else 1)' \
    >/dev/null 2>&1; then
    stop "the Python found, $python, belongs to a private environment that is \
switched on in this terminal window. Type deactivate, press Enter, and run \
this script again."
fi

if [ ! -f "$lock" ] || [ ! -f "$here/scripts/check_bundle.py" ]; then
    if [ -f "$here/pyproject.toml" ] && [ -d "$here/src/synthtwin" ]; then
        stop "this is synthtwin's source folder, not a bundle, and synthtwin is \
installed only from its bundle. README.md in this folder says where to get it, \
under 'Then get the synthtwin bundle'; unzip the bundle and run this script \
again from its folder."
    fi
    stop "this folder is not a whole synthtwin bundle: requirements-install.lock \
or scripts/check_bundle.py is missing from $here. Download the synthtwin bundle \
for this computer again, unzip it whole, and run this script again from its folder."
fi

# The bundle is checked before anything is changed, so a damaged or
# wrong bundle leaves an earlier environment as it was.
"$python" -I "$here/scripts/check_bundle.py" "$here" \
    || stop "the bundle's check above did not pass. Do what it says, then \
run this script again."

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
Download the synthtwin bundle again, unzip it whole, and run this script again."

say "Installing synthtwin into $env_dir"
say "using $("$python" -c 'import sys; print(sys.executable, sys.version.split()[0])')"

if [ -f "$env_dir/pyvenv.cfg" ]; then
    say "Replacing the earlier private environment in $env_dir; a package you"
    say "installed into it yourself must be installed again afterwards."
fi

venv_advice="Check that the bundle's folder is one you can save files in, \
then run this script again."
if [ "$(uname -s 2>/dev/null)" = "Linux" ]; then
    venv_advice="On Debian or Ubuntu, ask whoever looks after this computer \
to install the python3-venv package, then run this script again."
fi
"$python" -m venv --clear "$env_dir" || stop "Python could not make the \
private environment in $env_dir. $venv_advice"
venv_python="$env_dir/bin/python"

say "from the bundle's wheelhouse, with no internet"
PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install --isolated \
    --disable-pip-version-check \
    --no-index --find-links "$wheels" \
    --require-hashes -r "$lock" \
    || stop "pip could not install the bundle's libraries from $wheels with \
their hashes checked. Download the synthtwin bundle made for this computer \
again, unzip it whole into a new folder, and run this script again from there."
PIP_CONFIG_FILE=/dev/null "$venv_python" -m pip install --isolated \
    --disable-pip-version-check \
    --no-index --no-deps --find-links "$wheels" synthtwin \
    || stop "pip could not install $wheel. Download the synthtwin bundle \
again, unzip it whole into a new folder, and run this script again from \
there; if it stops here again, send the lines above to whoever looks after \
synthtwin."

say ""
"$env_dir/bin/synthtwin" doctor
status=$?

say ""
say "synthtwin is installed. Now, in this window, and in each new terminal"
say "window, switch its private environment on first, then type the commands"
say "as INSTALL.txt writes them and as synthtwin prints them:"
say "  source \"$env_dir/bin/activate\""
say "  synthtwin profile my-table.csv"
exit "$status"
