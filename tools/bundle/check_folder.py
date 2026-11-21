"""Check synthtwin's ready folder for Windows, then open the window it runs in.

Plan P4-D483 (lane WIN of the December plan). It is kept in the
repository as tools/bundle/check_folder.py and placed in the ready folder
as scripts\\check_folder.py. START-HERE.bat runs it with the folder's own
Python every time, before synthtwin starts, and every decision the
double-click makes is made here, where it can be tested:

    python\\python.exe -I -B scripts\\check_folder.py FOLDER
    python\\python.exe -I -B scripts\\check_folder.py --start FOLDER [/check]
    python\\python.exe -I -B scripts\\check_folder.py --powershell FOLDER
    python\\python.exe -I -B scripts\\check_folder.py --banner powershell|cmd

It uses the standard library alone and writes nothing. It refuses, in
plain words and never with a traceback:

* a folder with no SHA256SUMS, a line of it that is not a SHA-256 and a
  relative path inside the folder, a file it lists that is missing, and
  a file whose bytes do not match its line (the folder never changes
  after it is made: its Python writes no bytecode and every library file
  was compiled when the folder was built);
* a file SHA256SUMS does not list inside the python folder, where the
  folder's Python could load it as code;
* a file SHA256SUMS does not list anywhere else in the folder whose
  name ends as a program a Windows window runs by its name ends
  (synthtwin.exe, .com, .bat, .cmd, .ps1 and the rest of RUNNABLE, with
  the computer's own PATHEXT): beside synthtwin.bat it could answer to
  the word synthtwin in place of the checked launcher;
* a computer that does not run Windows;
* a file this computer will not let it read.

WHAT THE CHECK GUARDS AGAINST. A folder damaged on its way (a USB key,
a copy cut short) or changed by accident after it was made. It cannot
guard against a folder changed on purpose: the folder's own Python, the
files it loads first and this check itself run before any hash is
compared, so a changed copy of them could skip the check.
That is why the zip itself is checked, before it is unzipped, against a
SHA-256 that is not inside it (the one the build run prints), with
Windows' own Get-FileHash, as both guides say in their first step.

It ignores what a Mac leaves on a USB key it wrote to (._ files and
.DS_Store) and what Windows Explorer leaves in a folder (Thumbs.db,
desktop.ini), and warns about any other file SHA256SUMS does not list
outside the python folder (a file someone saved in the folder) without
refusing. It warns when the computer has an Arm processor: the folder is
made for 64-bit Intel and AMD processors.

With --start (START-HERE.bat's call), once the folder passed, it opens
the window synthtwin runs in and exits: a PowerShell window where
PowerShell answers -- a function named synthtwin calls the folder's
python.exe with -I -B -X utf8 -m synthtwin and the words typed after it,
so the commands synthtwin prints, written in PowerShell's quoting, work
as printed -- and otherwise a Command Prompt window. EVERY COMMAND THE
WINDOW RUNS NAMES THE CHECKED LAUNCHER OR INTERPRETER BY ITS FULL PATH,
never a word the shell would look up in the work folder first: the
PowerShell window runs the computer check with the folder's python.exe
by its path, and the word synthtwin typed there is the function (a
function comes before any program of that name, and PowerShell never
runs a program from the current folder by its name alone); the Command
Prompt window runs the computer check with the folder's synthtwin.bat
by its path, binds the word synthtwin to that path with a DOSKEY macro
(doskey.exe named by its path too), and is given the folder first on
PATH and NoDefaultCurrentDirectoryInExePath, so that even where the
macro does not apply the current folder is never searched for the word
(not yet measured on Windows). Either window opens in the work folder
twin-work in the person's own folder where it exists (else in the
person's own folder, never in synthtwin's: the computer check writes a
test file where the window stands), shows the banner and runs synthtwin
doctor.
The window keeps no history of what is typed in it: the PowerShell
window first turns off the history file PSReadLine would otherwise
write in the person's own folder (not yet measured on Windows), and
Command Prompt keeps none on disk; synthtwin's own files stay beside the
table. With /check it checks and opens nothing (the rehearsal's switch);
any other word after the folder is a file dropped on START-HERE, which
takes none, and is told so. It exits 0 when the folder passed (and the
window opened), 1 when the folder was refused or no window could open,
2 on a usage error and 3 when the folder passed with a note to read
(START-HERE.bat then waits for a key, so the note stays on the screen).
It prints how many seconds the check took. --powershell prints the
command the PowerShell window runs, for the rehearsal and for whoever
reviews the folder.
"""

import hashlib
import os
import re
import subprocess
import sys
import time

SUMS = "SHA256SUMS"
# What a Mac leaves on a USB key and what Windows Explorer leaves in a
# folder it showed; never part of the folder, never loaded as code.
_LEFTOVERS = (".ds_store", "thumbs.db", "desktop.ini")
_SUM_LINE = re.compile(r"([0-9a-f]{64})  ([^\r\n]+)")
# The characters PowerShell reads as a single quote inside a quoted
# string: the ASCII one and three typographic ones (synthtwin's own cli
# writes each of them twice in what it prints, the same rule).
_POWERSHELL_QUOTES = "'\u2018\u2019\u201a\u201b"
_AGAIN = (
    "Nothing was run. Unzip synthtwin's zip file again into a new folder "
    "(right-click it, Extract All), and double-click START-HERE in the new "
    "folder; if it stops here again, send this message to whoever looks "
    "after synthtwin."
)
# The window opens here if it exists (docs/windows-install.md's work folder).
WORK_FOLDER = "twin-work"

POWERSHELL_BANNER = """
synthtwin is ready in this window. Go first to the folder that holds
your table, then type synthtwin's commands, for example:

    cd $HOME\\twin-work
    synthtwin doctor my-table.csv
    synthtwin profile my-table.csv

While synthtwin works, do not click inside this window: a click pauses
it. If the window's title begins with the word Select, press Esc.
To stop, press Ctrl+C. To end your answers, press Ctrl+Z, then Enter.
synthtwin writes its files beside your table, or in the folder you name
with --out-dir, and never in synthtwin's own folder. This window keeps
no history of what you type (not yet measured on Windows). The computer
check follows.
"""

CMD_BANNER = """
synthtwin is ready in this window (Command Prompt: PowerShell did not
answer on this computer). Go first to the folder that holds your table,
then type synthtwin's commands, for example:

    cd /d "%USERPROFILE%\\twin-work"
    synthtwin doctor my-table.csv
    synthtwin profile my-table.csv

synthtwin prints the commands it suggests for PowerShell. Here, where a
name stands between single quotes 'like this', type it between double
quotes "like this", and where two single quotes stand together inside
it, as in 'Crohn''s disease', type one: "Crohn's disease".
While synthtwin works, do not click inside this window: a click pauses
it. If the window's title begins with the word Select, press Esc.
To stop, press Ctrl+C; if the window then asks "Terminate batch job
(Y/N)?", type Y and press Enter. To end your answers, press Ctrl+Z,
then Enter. synthtwin writes its files beside your table, or in the
folder you name with --out-dir, and never in synthtwin's own folder.
This window keeps no history of what you type. The computer check
follows.
"""
# The first words of the PowerShell window's command: PSReadLine, which
# Windows PowerShell 5.1 loads in an interactive window even with
# -NoProfile, would otherwise append every typed line (file and column
# names among them) to a history file in the person's own folder.
NO_HISTORY = "try { Set-PSReadLineOption -HistorySaveStyle SaveNothing } catch { }; "
# What a word after the folder means: a file dropped on START-HERE.
DROPPED = (
    "START-HERE takes no file: double-click it, then type synthtwin's "
    "commands in the window it opens."
)
# The endings of a file a Windows window runs when only its name is
# typed: Command Prompt's PATHEXT as Windows 10 and 11 set it, then
# PowerShell's own scripts and the endings a Python installer or an
# old setting may add. The computer's own PATHEXT is read beside them.
# An extra file with one of them, outside the python folder, could
# answer to the word synthtwin in place of the checked launcher, so it
# stops the run (the window puts the folder first on PATH).
RUNNABLE = (
    ".com", ".exe", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".msc",
    ".ps1", ".py", ".pyw", ".cpl", ".scr", ".pif",
)


def runnable_endings(environment=None):
    """RUNNABLE with every ending of the computer's PATHEXT, in lower case."""
    environment = os.environ if environment is None else environment
    listed = str(environment.get("PATHEXT", "") or "")
    return set(RUNNABLE) | {part.strip().lower() for part in listed.split(";") if part.strip().startswith(".")}


class _Unreadable(Exception):
    """A file of the folder this computer would not let the check read."""

    def __init__(self, relative, error):
        super().__init__(relative)
        self.relative = relative
        self.reason = getattr(error, "strerror", None) or type(error).__name__


def _digest(folder, relative):
    hasher = hashlib.sha256()
    try:
        with open(os.path.join(folder, *relative.split("/")), "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                hasher.update(block)
    except OSError as error:
        raise _Unreadable(relative, error) from None
    return hasher.hexdigest()


def _ignored(name):
    return name.startswith("._") or name.lower() in _LEFTOVERS


def _refuse_listing(error):
    raise _Unreadable(getattr(error, "filename", None) or "a folder", error)


def _on_disk(folder):
    """Every file under the folder, as a relative path with forward slashes."""
    found = []
    for root, folders, files in os.walk(folder, onerror=_refuse_listing):
        folders[:] = [name for name in folders if not _ignored(name)]
        for name in files:
            if not _ignored(name):
                relative = os.path.relpath(os.path.join(root, name), folder)
                found += [relative.replace(os.sep, "/")]
    return sorted(found)


def _arm(environment=None):
    """Whether this computer's processor is an Arm one, read from what Windows says of it.

    An x64 program emulated on Arm is told PROCESSOR_ARCHITECTURE=AMD64, so
    the other two names are read as well.
    """
    environment = os.environ if environment is None else environment
    words = " ".join(
        str(environment.get(name, ""))
        for name in ("PROCESSOR_ARCHITECTURE", "PROCESSOR_ARCHITEW6432", "PROCESSOR_IDENTIFIER")
    ).upper()
    return "ARM" in words


def check(folder, system=None, environment=None):
    """(problems, warnings) of the ready folder in ``folder``.

    ``system`` is sys.platform where it is None; ``environment`` the
    variables the Arm warning reads (os.environ where it is None).
    Problems refuse the folder; warnings are printed and run on.
    """
    system = sys.platform if system is None else system
    if system != "win32":
        named = {"darwin": "macOS"}.get(system, "Linux" if system.startswith("linux") else system)
        return [
            "this is synthtwin's folder for Windows, and this computer runs " + named
            + ". On a Mac or on Linux, use the synthtwin bundle made for it and "
            "its INSTALL.txt."
        ], []
    warnings = []
    if _arm(environment):
        warnings += [
            "this computer has an Arm processor, and this folder is made for 64-bit "
            "Intel and AMD processors. Windows 11 runs it on Arm too, more slowly; "
            "if synthtwin does not start, send this message to whoever looks after "
            "synthtwin."
        ]
    try:
        return _check(folder, warnings, runnable_endings(environment))
    except _Unreadable as unreadable:
        return [
            "this computer would not let synthtwin read " + str(unreadable.relative)
            + " in its folder (" + str(unreadable.reason) + "), so the folder cannot "
            "be checked. Copy synthtwin's zip file into a folder of your own, such as "
            "C:\\synthtwin, unzip it there, and double-click START-HERE in the new "
            "folder; if it stops here again, send this message to whoever looks after "
            "this computer."
        ], warnings


def _check(folder, warnings, runnable):
    sums_path = os.path.join(folder, SUMS)
    if not os.path.isfile(sums_path):
        return [
            "the file SHA256SUMS is missing from synthtwin's folder, so its files "
            "cannot be checked. " + _AGAIN
        ], warnings
    try:
        with open(sums_path, "rb") as handle:
            sums_text = handle.read().decode("utf-8", "replace")
    except OSError as error:
        raise _Unreadable(SUMS, error) from None
    listed = {}
    problems = []
    for number, raw in enumerate(sums_text.splitlines(), 1):
        if not raw.strip():
            continue
        found = _SUM_LINE.fullmatch(raw)
        relative = found.group(2).replace("\\", "/") if found else ""
        if (
            not found
            or relative.startswith("/")
            or ":" in relative
            or ".." in relative.split("/")
            or relative in listed
        ):
            problems += [
                "line " + str(number) + " of SHA256SUMS is not a SHA-256 and a file "
                "of this folder named once"
            ]
            continue
        listed[relative] = found.group(1)
    if not listed and not problems:
        problems += ["SHA256SUMS lists no file"]
    for relative, digest in sorted(listed.items()):
        if not os.path.isfile(os.path.join(folder, *relative.split("/"))):
            problems += [relative + " is listed in SHA256SUMS but missing"]
        elif _digest(folder, relative) != digest:
            problems += [
                relative + " does not match its hash in SHA256SUMS (it was changed "
                "or damaged after the folder was made)"
            ]
    for relative in _on_disk(folder):
        if relative == SUMS or relative in listed:
            continue
        if relative.split("/", 1)[0].lower() == "python":
            problems += [
                relative + " is not one of the folder's own files, and it sits inside "
                "the python folder, where the folder's Python could load it"
            ]
        elif os.path.splitext(relative)[1].lower() in runnable:
            problems += [
                relative + " is not one of the folder's own files, and a Windows window "
                "could run it in place of synthtwin's own launcher"
            ]
        else:
            warnings += [
                relative + " is not one of synthtwin's own files (a file saved in "
                "synthtwin's folder); synthtwin runs on. Keep your tables and "
                "synthtwin's results in a work folder of your own instead."
            ]
    if problems:
        return [
            "synthtwin's folder did not pass its check: " + "; ".join(problems) + ". "
            + _AGAIN
        ], warnings
    return [], warnings


def _quoted_for_powershell(text):
    """``text`` between PowerShell's single quotes, every quote character inside doubled."""
    return "'" + "".join(c + c if c in _POWERSHELL_QUOTES else c for c in text) + "'"


def powershell_function(folder):
    """The PowerShell function named synthtwin: the folder's python.exe, the words typed splatted."""
    python = _quoted_for_powershell(os.path.join(os.path.abspath(folder), "python", "python.exe"))
    return "function global:synthtwin { & " + python + " -I -B -X utf8 -m synthtwin @args }"


def powershell_command(folder):
    """The command the PowerShell window runs: the synthtwin function, the banner, doctor.

    The computer check runs the folder's python.exe by its full path, as
    the function does; nothing in it is a word PowerShell looks up.
    """
    folder = os.path.abspath(folder)
    python = _quoted_for_powershell(os.path.join(folder, "python", "python.exe"))
    script = _quoted_for_powershell(os.path.join(folder, "scripts", "check_folder.py"))
    return (
        NO_HISTORY
        + "try { $Host.UI.RawUI.WindowTitle = 'synthtwin' } catch { }; "
        + powershell_function(folder) + "; "
        "& " + python + " -I -B " + script + " --banner powershell; "
        "& " + python + " -I -B -X utf8 -m synthtwin doctor"
    )


def cmd_command_line(folder, system_root):
    """The whole command line of the Command Prompt window: the macro, the banner, then doctor.

    /s takes the outer quotes off the words after /k and runs the rest as
    typed, so each path keeps its own quotes. Every command names its
    program by its full path (title is Command Prompt's own): doskey.exe
    binds the word synthtwin to the folder's synthtwin.bat for every line
    the person types in this window, and the computer check runs that
    synthtwin.bat by its path, so a program named synthtwin in the work
    folder, where the window opens, is never what runs.
    """
    folder = os.path.abspath(folder)
    python = os.path.join(folder, "python", "python.exe")
    script = os.path.join(folder, "scripts", "check_folder.py")
    launcher = os.path.join(folder, "synthtwin.bat")
    shell = os.path.join(system_root, "System32", "cmd.exe")
    doskey = os.path.join(system_root, "System32", "doskey.exe")
    return (
        '"' + shell + '" /d /s /k "title synthtwin & "' + doskey + '" synthtwin="' + launcher + '" $* & "'
        + python + '" -I -B "' + script + '" --banner cmd & "' + launcher + '" doctor"'
    )


def cmd_environment(folder, environment):
    """The Command Prompt window's environment: the folder first on PATH, the current folder never searched.

    NoDefaultCurrentDirectoryInExePath keeps Command Prompt from looking
    in the current folder for a command typed by its name alone, so where
    the DOSKEY macro does not apply (a word after &, a leading space) the
    word synthtwin still reaches the folder's synthtwin.bat first.
    """
    given = dict(environment)
    given["PATH"] = os.path.abspath(folder) + ";" + str(environment.get("PATH", ""))
    given["NoDefaultCurrentDirectoryInExePath"] = "1"
    return given


def _system_root(environment):
    return str(environment.get("SystemRoot") or environment.get("SYSTEMROOT") or "C:\\Windows")


def window_place(environment):
    """Where the window opens: the person's twin-work folder, else the person's own folder."""
    home = str(environment.get("USERPROFILE") or "")
    if home and os.path.isdir(os.path.join(home, WORK_FOLDER)):
        return os.path.join(home, WORK_FOLDER)
    if home and os.path.isdir(home):
        return home
    return None


def _powershell_answers(environment):
    """Whether Windows PowerShell starts and runs one command here (not blocked by policy)."""
    program = os.path.join(_system_root(environment), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
    try:
        done = subprocess.run(
            [program, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "exit 0"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def open_window(folder, environment=None, popen=None, answers=None):
    """Open the window synthtwin runs in; the problems, empty when one opened.

    ``popen`` stands for subprocess.Popen and ``answers`` for the
    PowerShell probe (tests hand in their own); both are this
    computer's own where they are None.
    """
    environment = dict(os.environ if environment is None else environment)
    popen = subprocess.Popen if popen is None else popen
    answered = _powershell_answers(environment) if answers is None else answers()
    root = _system_root(environment)
    place = window_place(environment)
    new_console = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x10)
    if answered:
        shell = os.path.join(root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
        try:
            popen(
                [shell, "-NoLogo", "-NoProfile", "-NoExit", "-Command", powershell_command(folder)],
                cwd=place,
                creationflags=new_console,
            )
            return []
        except OSError:
            pass
    try:
        popen(
            cmd_command_line(folder, root),
            executable=os.path.join(root, "System32", "cmd.exe"),
            cwd=place,
            env=cmd_environment(folder, environment),
            creationflags=new_console,
        )
    except OSError as error:
        return [
            "synthtwin's folder passed its check, but this computer would not open "
            "a PowerShell or a Command Prompt window ("
            + str(getattr(error, "strerror", None) or type(error).__name__)
            + "). Send this message to whoever looks after this computer: the For IT "
            "part of INSTALL-WINDOWS.txt in this folder says what synthtwin needs."
        ]
    return []


def _say(text):
    print(text, flush=True)


def main(argv=None, opener=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        sys.stdout.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass
    if arguments[:1] == ["--banner"] and len(arguments) == 2 and arguments[1] in ("powershell", "cmd"):
        _say(POWERSHELL_BANNER if arguments[1] == "powershell" else CMD_BANNER)
        return 0
    if arguments[:1] == ["--powershell"] and len(arguments) == 2:
        _say(powershell_command(arguments[1]))
        return 0
    starting = arguments[:1] == ["--start"]
    if starting:
        arguments = arguments[1:]
    only = starting and arguments[1:] == ["/check"]
    if only:
        arguments = arguments[:1]
    if starting and len(arguments) > 1:
        _say(DROPPED)
        return 2
    if len(arguments) != 1:
        _say("Give synthtwin's folder: python -I -B scripts\\check_folder.py FOLDER")
        return 2
    folder = os.path.abspath(arguments[0])
    _say(
        "Checking synthtwin's files against SHA256SUMS: this can take a minute "
        "or more; the window prints how many seconds it took..."
    )
    began = time.perf_counter()
    try:
        problems, warnings = check(folder)
    except Exception as error:  # noqa: BLE001 -- never a traceback in front of a person
        problems, warnings = [
            "the check of synthtwin's folder stopped unexpectedly ("
            + type(error).__name__ + "). " + _AGAIN
        ], []
    _say("The check took " + format(time.perf_counter() - began, ".1f") + " s.")
    for warning in warnings:
        _say("Note: " + warning)
    if problems:
        for problem in problems:
            _say("synthtwin did not start: " + problem)
        return 1
    _say("synthtwin's files match their hashes in SHA256SUMS.")
    if not starting or only:
        return 0
    _say("Opening the window synthtwin runs in...")
    try:
        refused = open_window(folder) if opener is None else opener(folder)
    except Exception as error:  # noqa: BLE001 -- never a traceback in front of a person
        refused = ["the window could not be opened (" + type(error).__name__ + "). " + _AGAIN]
    for problem in refused:
        _say("synthtwin did not start: " + problem)
    if refused:
        return 1
    return 3 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
