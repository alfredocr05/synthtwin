#!/usr/bin/env python3
"""Rehearse what a person does with synthtwin on Windows, and compare the runs.

Plan P4-D483 (lane WIN of the December plan). The jobs of the workflow
file windows-bundle.yml in the repository's workflow folder run this
with the very interpreter they rehearse -- the ready folder's own
python.exe, or the backup's -- after the firewall blocks it, so the
rehearsal itself runs nothing else; the Linux and macOS jobs run it with
their own Python for the comparison. It opens no network connection.

    rehearse_windows.py trial --route ROUTE --work DIR --tables DIR
        [--folder READY] [--python PY] [--stems visits,visits-1252]
        [--record FILE] [--summary FILE]

runs, for each invented table, the commands a person types, in this
order, in a fresh copy of the table's folder: synthtwin --version;
synthtwin doctor TABLE; synthtwin profile TABLE naming the person
column; the answers written (fill_answers.py: in the questions file, or
in the plain-text answers file where synthtwin reads one); synthtwin
profile TABLE --answers FILE; synthtwin generate --seed 7; synthtwin
validate --twin. Each command's exit status, seconds and new files are
recorded, and the run is refused unless every status is 0, the six
files stand beside the table, synthtwin counted 1,000 people and the
twin holds 1,000, nothing answered is open again and the verdict holds
no missed obligation. ROUTE is how the person reaches synthtwin:

    powershell  the function START-HERE.bat defines in its PowerShell
                window (taken from the folder's scripts\\check_folder.py)
    cmd         Command Prompt with the environment START-HERE.bat gives
                its window (the folder first on PATH, the current folder
                never searched), so the word synthtwin is synthtwin.bat
    guard       guard_run.py, every network call made to raise, run by
                the folder's python.exe (--folder) or by the backup's
                .venv python (--python)
    direct      PY -m synthtwin (the backup's .venv python, and Linux
                and macOS for the comparison)

On the powershell and cmd routes the work folder holds decoys first:
programs named synthtwin (.bat, .cmd, .ps1 and, on Windows, .exe) that
print DECOY and exit 9, as a stale or hostile file would sit where the
window opens; the trial passes only if the word reached the folder's
checked launcher every time.

    rehearse_windows.py redirect --route cmd|direct ... --expect pass|record
    rehearse_windows.py tamper --folder READY --into DIR
    rehearse_windows.py start-check --folder READY
    rehearse_windows.py golden --python PY --pytest-only DIR
    rehearse_windows.py again --python PY --from RUN --work DIR
    rehearse_windows.py compare (--assert A B | --report A B)...

`redirect` describes the table with standard output sent to a file, as
'> screen.txt' does (the label outside Windows-1252 is the point);
`tamper` copies the folder, changes one byte of a library file and
shows START-HERE.bat refusing the copy before synthtwin starts;
`start-check` runs START-HERE.bat /check on the folder as it was
unzipped, then on a copy of START-HERE.bat alone in an empty folder, as
Explorer runs it from inside the zip, which must say to unzip first;
`golden`
runs the golden tests with that interpreter, pytest put on its path by
a -c line (the folder's ._pth file ignores PYTHONPATH); `again`
generates and validates from another system's description and holds
its twin to that system's; `compare` holds the descriptions and twins
of two runs to each other, byte for byte, or reports how they differ.
"""

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fill_answers  # noqa: E402

REPO = HERE.parents[1]
PERSON = "subject_id"
# The answers the how-to's reader gives the invented tables, each
# column's in order of preference: what each column truly is (the zoo's
# rule: answer the data as it is). The five-figure codes are codes, and,
# asked next whether they could be ZIP codes, they are not.
ANSWERS = {"code": ("code", "no"), "age": ("years",), "weight": ("no",)}
ROUNDS = 3
STEMS = ("visits", "visits-1252")
PEOPLE = 1000
SEED = "7"
# Every file a full run writes beside the table.
OUTPUTS = (
    "{stem}-profile.json",
    "{stem}-profile.txt",
    "{stem}-questions.json",
    "{stem}-twin.csv",
    "{stem}-twin-report.txt",
    "{stem}-twin-quality.txt",
)
# The description and the twin: the bytes a system must not change.
HELD = ("{stem}-profile.json", "{stem}-twin.csv")
GOLDEN = (
    "tests/test_twin_golden.py",
    "tests/test_generation_reference.py",
    "tests/test_numeric_reference.py",
)
# The first level of the network's denial: every command the rehearsal
# starts is given proxy variables that point at a closed port of this
# computer (the workflow proves first that they refuse a web address).
PROXIES = {
    "HTTP_PROXY": "http://127.0.0.1:9",
    "HTTPS_PROXY": "http://127.0.0.1:9",
    "ALL_PROXY": "http://127.0.0.1:9",
    "NO_PROXY": "",
}
_PLAIN = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-:\\/")


def _system_root() -> str:
    return os.environ.get("SystemRoot") or "C:\\Windows"


def powershell_program() -> str:
    return os.path.join(_system_root(), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")


def cmd_program() -> str:
    return os.path.join(_system_root(), "System32", "cmd.exe")


def powershell_word(word: str) -> str:
    if word and all(character in _PLAIN for character in word):
        return word
    return "'" + "".join(c + c if c in "'\u2018\u2019\u201a\u201b" else c for c in word) + "'"


def cmd_word(word: str) -> str:
    if word and all(character in _PLAIN for character in word):
        return word
    return '"' + word + '"'


def _load_check_folder(folder: pathlib.Path):  # type: ignore[no-untyped-def]
    """The folder's own scripts\\check_folder.py, as START-HERE.bat runs it."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_folder", folder / "scripts" / "check_folder.py")
    if spec is None or spec.loader is None:
        raise ValueError(f"{folder} holds no scripts/check_folder.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Route:
    """How the person reaches synthtwin, and the command line of one typed command."""

    def __init__(
        self,
        kind: str,
        folder: "pathlib.Path | None" = None,
        python: "str | None" = None,
        extra: "dict[str, str] | None" = None,
    ) -> None:
        if kind in ("powershell", "cmd") and folder is None:
            raise ValueError(f"the {kind} route needs --folder")
        if kind == "guard" and folder is None and not python:
            raise ValueError("the guard route needs --folder (the ready folder) or --python (the backup's)")
        if kind == "direct" and not python:
            raise ValueError("the direct route needs --python")
        self.kind = kind
        self.folder = folder
        self.python = python
        self.extra = dict(extra or {})
        self.function = ""
        self.window = None
        if kind in ("powershell", "cmd") and folder is not None:
            # The folder's own check, as START-HERE.bat runs it: the
            # PowerShell function and the Command Prompt window's
            # environment are taken from it, not written again here.
            self.window = _load_check_folder(folder)
            self.function = self.window.powershell_function(str(folder))

    def environment(self) -> "dict[str, str]":
        given = proxied()
        given.update(self.extra)
        if self.kind == "cmd" and self.window is not None:
            given = self.window.cmd_environment(str(self.folder), given)
        return given

    def command(self, words: "list[str]", into: "str | None" = None) -> "str | list[str]":
        """The command line of ``synthtwin WORDS`` on this route, its output sent to ``into`` if named."""
        if self.kind == "powershell":
            typed = "synthtwin " + " ".join(powershell_word(word) for word in words)
            if into:
                typed += " > " + powershell_word(into)
            text = (
                self.function + "; " + typed
                + "; if ($null -eq $LASTEXITCODE) { exit 99 }; exit $LASTEXITCODE"
            )
            return [powershell_program(), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", text]
        if self.kind == "cmd":
            typed = "synthtwin " + " ".join(cmd_word(word) for word in words)
            if into:
                typed += ' > "' + into + '"'
            return '"' + cmd_program() + '" /d /s /c "' + typed + '"'
        if self.kind == "guard" and self.folder is not None:
            return [
                str(self.folder / "python" / "python.exe"), "-I", "-B", "-X", "utf8",
                str(HERE / "guard_run.py"), *words,
            ]
        if self.kind == "guard":
            # The backup's .venv python, run as the direct route runs it
            # (so --utf8-screen reaches it), with the guard in its process.
            return [str(self.python), str(HERE / "guard_run.py"), *words]
        return [str(self.python), "-m", "synthtwin", *words]


class Trial:
    """One route's run of the person's commands, recorded step by step."""

    def __init__(self, route: Route, work: pathlib.Path) -> None:
        self.route = route
        self.work = work
        self.steps: "list[dict[str, object]]" = []
        self.problems: "list[str]" = []

    def run(self, words: "list[str]", into: "str | None" = None, expect: "int | None" = 0) -> int:
        before = {path.name for path in self.work.iterdir()}
        command = self.route.command(words, into)
        log = self.work.parent / f"{self.work.name}-screen-{len(self.steps) + 1:02d}.txt"
        began = time.perf_counter()
        with open(log, "wb") as screen:
            done = subprocess.run(
                command,
                cwd=self.work,
                env=self.route.environment(),
                stdin=subprocess.DEVNULL,
                stdout=screen,
                stderr=subprocess.STDOUT,
                check=False,
            )
        seconds = time.perf_counter() - began
        made = sorted({path.name for path in self.work.iterdir()} - before)
        typed = "synthtwin " + " ".join(words) + (f" > {into}" if into else "")
        self.steps += [{"typed": typed, "exit": done.returncode, "seconds": round(seconds, 1), "new": made}]
        print(f"[{self.route.kind}] {typed}  -> exit {done.returncode}, {seconds:.1f} s, new: {made}", flush=True)
        if expect is not None and done.returncode != expect:
            said = log.read_bytes().decode("utf-8", "replace")
            print(said[-3000:], flush=True)
            self.problems += [f"{typed} exited {done.returncode}, not {expect}"]
        return done.returncode


def proxied() -> "dict[str, str]":
    """This process's environment with PROXIES in it, for a command the rehearsal starts."""
    given = dict(os.environ)
    given.update(PROXIES)
    return given


def person_option(source: pathlib.Path = REPO) -> str:
    """--person where the source of this commit has it (lane EZ-a), else --identifier."""
    cli = source / "src" / "synthtwin" / "cli.py"
    text = cli.read_text(encoding="utf-8") if cli.is_file() else ""
    return "--person" if '"--person",' in text else "--identifier"


def plain_answers_read(source: pathlib.Path = REPO) -> bool:
    """Whether the source of this commit reads a plain-text answers file (lane EZ-a)."""
    contract = source / "src" / "synthtwin" / "contract.py"
    return contract.is_file() and "_answers_written_as_lines" in contract.read_text(encoding="utf-8")


def people_counted(description: "dict[str, object]") -> "list[int]":
    """The people counts the description publishes (a date column's time grain carries one)."""
    found: "list[int]" = []
    columns = description.get("columns")
    for column in columns if isinstance(columns, list) else []:
        grain = column.get("time_grain") if isinstance(column, dict) else None
        if isinstance(grain, dict) and isinstance(grain.get("people"), int):
            found += [int(grain["people"])]
    return found


def missed(quality: str) -> "int | None":
    """The verdict's count of missed obligations, read from the quality report's verdict block."""
    for line in quality.splitlines():
        words = line.split()
        if len(words) >= 2 and words[1] == "MISSED" and words[0].isdigit():
            return int(words[0])
    return None


def _twin_people(twin: pathlib.Path) -> int:
    import csv

    with open(twin, encoding="utf-8-sig", errors="replace", newline="") as handle:
        rows = csv.reader(handle)
        head = next(rows)
        place = head.index(PERSON)
        return len({row[place] for row in rows if len(row) > place})


# Programs named as the word the person types, left in the work folder
# where the window opens, as a stale or hostile file would be (Codex's
# counterexample of the Command Prompt route): the word must still reach
# the folder's checked launcher, so a decoy that runs stops the trial.
DECOY_WORDS = b"DECOY: not synthtwin's own launcher"
DECOYS = {
    "synthtwin.bat": b"@echo off\r\necho " + DECOY_WORDS + b"\r\nexit /b 9\r\n",
    "synthtwin.cmd": b"@echo off\r\necho " + DECOY_WORDS + b"\r\nexit /b 9\r\n",
    "synthtwin.ps1": b"Write-Output '" + DECOY_WORDS.replace(b"'", b"''") + b"'\r\nexit 9\r\n",
}


def plant_decoys(work: pathlib.Path) -> "list[str]":
    """DECOYS in ``work``, and on Windows a program file synthtwin.exe (a copy of where.exe); their names."""
    for name, data in DECOYS.items():
        (work / name).write_bytes(data)
    where = pathlib.Path(_system_root()) / "System32" / "where.exe"
    if os.name == "nt" and where.is_file():
        shutil.copyfile(where, work / "synthtwin.exe")
    return sorted(path.name for path in work.iterdir() if path.name.startswith("synthtwin."))


def trial(route: Route, work: pathlib.Path, tables: pathlib.Path, stems: "tuple[str, ...]") -> Trial:
    """The person's commands for each table, in ``work`` (made fresh; the windows' routes with the decoys in it)."""
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    done = Trial(route, work)
    if route.kind in ("powershell", "cmd"):
        print(f"[{route.kind}] decoys in the work folder: {plant_decoys(work)}", flush=True)
    person = person_option()
    plain = plain_answers_read() and route.kind == "cmd"
    done.run(["--version"])
    for stem in stems:
        shutil.copyfile(tables / f"{stem}.csv", work / f"{stem}.csv")
        table = f"{stem}.csv"
        questions = work / f"{stem}-questions.json"
        if done.run(["doctor", table]) != 0 or done.run(["profile", table, person, PERSON]) != 0:
            return done
        written: "list[tuple[str, str]]" = []
        for _ in range(ROUNDS):
            try:
                document = fill_answers.load(questions)
            except (OSError, ValueError) as error:
                done.problems += [f"{questions.name} could not be read: {error}"]
                return done
            chosen, problems = fill_answers.choose(document, ANSWERS)
            if problems:
                done.problems += problems
                return done
            if not chosen:
                break
            written += chosen
            answers = work / f"{stem}-answers.txt" if plain else questions
            if plain:
                fill_answers.write_plain(answers, chosen)
            else:
                fill_answers.write_json(questions, document)
            if done.run(["profile", table, person, PERSON, "--answers", answers.name, "--replace"]) != 0:
                return done
        done.problems += fill_answers.settled(fill_answers.load(questions), written)
        if done.run(["generate", f"{stem}-profile.json", "--seed", SEED]) != 0:
            return done
        if done.run(["validate", f"{stem}-profile.json", "--twin", f"{stem}-twin.csv"]) != 0:
            return done
        done.problems += outcome_problems(work, stem)
    return done


def outcome_problems(work: pathlib.Path, stem: str) -> "list[str]":
    """What a full run's files beside the table say against the rehearsal's bar."""
    problems: "list[str]" = []
    for name in OUTPUTS:
        if not (work / name.format(stem=stem)).is_file():
            problems += [f"{name.format(stem=stem)} was not written beside the table"]
    if problems:
        return problems
    description = json.loads((work / f"{stem}-profile.json").read_text(encoding="utf-8"))
    if PEOPLE not in people_counted(description):
        problems += [f"{stem}: synthtwin's people counts read {people_counted(description)}, not {PEOPLE}"]
    if _twin_people(work / f"{stem}-twin.csv") != PEOPLE:
        problems += [f"{stem}: the twin holds {_twin_people(work / f'{stem}-twin.csv')} people, not {PEOPLE}"]
    verdict = missed((work / f"{stem}-twin-quality.txt").read_text(encoding="utf-8", errors="replace"))
    if verdict != 0:
        problems += [f"{stem}: the verdict's missed obligations read {verdict}, not 0"]
    return problems


def _digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(first: pathlib.Path, second: pathlib.Path, stems: "tuple[str, ...]", names=OUTPUTS) -> "list[str]":
    """Each output of ``first`` against ``second``'s: the files that differ or are missing."""
    differ: "list[str]" = []
    for stem in stems:
        for name in names:
            one, two = first / name.format(stem=stem), second / name.format(stem=stem)
            if not one.is_file() or not two.is_file():
                differ += [f"{name.format(stem=stem)} is missing from {one.parent if not one.is_file() else two.parent}"]
                continue
            same = one.read_bytes() == two.read_bytes()
            print(f"  {'equal    ' if same else 'DIFFERENT'} {name.format(stem=stem)}  {_digest(one)[:16]}  {_digest(two)[:16]}")
            if not same:
                differ += [f"{name.format(stem=stem)} differs"]
    return differ


def again(python: str, source: pathlib.Path, work: pathlib.Path, stems: "tuple[str, ...]") -> "list[str]":
    """Generate and validate from ``source``'s descriptions here; the twin must be ``source``'s, byte for byte."""
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    done = Trial(Route("direct", python=python), work)
    for stem in stems:
        shutil.copyfile(source / f"{stem}-profile.json", work / f"{stem}-profile.json")
        if done.run(["generate", f"{stem}-profile.json", "--seed", SEED]) != 0:
            continue
        if done.run(["validate", f"{stem}-profile.json", "--twin", f"{stem}-twin.csv"]) != 0:
            continue
        verdict = missed((work / f"{stem}-twin-quality.txt").read_text(encoding="utf-8", errors="replace"))
        if verdict != 0:
            done.problems += [f"{stem}: the verdict's missed obligations read {verdict}, not 0"]
    return done.problems + compare(source, work, stems, ("{stem}-twin.csv",))


def redirect(route: Route, work: pathlib.Path, tables: pathlib.Path) -> "tuple[int, list[str]]":
    """Describe visits.csv with standard output sent to a file: (exit status, files written)."""
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    shutil.copyfile(tables / "visits.csv", work / "visits.csv")
    done = Trial(route, work)
    words = ["profile", "visits.csv", person_option(), PERSON]
    if route.kind == "direct":
        before = {path.name for path in work.iterdir()}
        with open(work / "screen.txt", "wb") as screen:
            status = subprocess.run(
                route.command(words), cwd=work, env=route.environment(), stdin=subprocess.DEVNULL,
                stdout=screen, stderr=subprocess.PIPE, check=False,
            ).returncode
        made = sorted({path.name for path in work.iterdir()} - before)
        print(f"[direct] synthtwin {' '.join(words)} > screen.txt  -> exit {status}, new: {made}", flush=True)
        return status, made
    status = done.run(words, into="screen.txt", expect=None)
    return status, list(done.steps[-1]["new"])  # type: ignore[arg-type]


def tamper(folder: pathlib.Path, into: pathlib.Path) -> "list[str]":
    """A copy of the folder with one byte of a library file changed: START-HERE.bat must refuse it."""
    copy = into / folder.name
    if copy.exists():
        shutil.rmtree(copy)
    shutil.copytree(folder, copy)
    sources = sorted((copy / "python" / "lib").rglob("*.py"))
    target = next((path for path in sources if path.parts[-2:] == ("numpy", "__init__.py")), sources[0] if sources else None)
    if target is None:
        return ["the copy holds no library file to change"]
    data = bytearray(target.read_bytes())
    data[len(data) // 2] ^= 1
    target.write_bytes(bytes(data))
    print(f"changed one byte of {target.relative_to(copy).as_posix()}", flush=True)
    # START-HERE's /check: the same check that runs before the window
    # opens, without the key press a refusal otherwise waits for.
    line = '"' + cmd_program() + '" /d /s /c ""' + str(copy / "START-HERE.bat") + '" /check"'
    done = subprocess.run(
        line, cwd=copy, env=proxied(), stdin=subprocess.DEVNULL, capture_output=True, check=False, timeout=600
    )
    said = (done.stdout + done.stderr).decode("utf-8", "replace")
    print(said, flush=True)
    problems: "list[str]" = []
    if done.returncode == 0:
        problems += ["START-HERE.bat ran a copy with a changed library file"]
    if "does not match its hash in SHA256SUMS" not in said:
        problems += ["START-HERE.bat's refusal did not name the changed file's hash"]
    return problems


def start_check(folder: pathlib.Path) -> "list[str]":
    """START-HERE.bat /check on the folder as it was unzipped: it must pass, and say so."""
    line = '"' + cmd_program() + '" /d /s /c ""' + str(folder / "START-HERE.bat") + '" /check"'
    began = time.perf_counter()
    done = subprocess.run(
        line, cwd=folder, env=proxied(), stdin=subprocess.DEVNULL, capture_output=True, check=False, timeout=900
    )
    said = (done.stdout + done.stderr).decode("utf-8", "replace")
    print(said + f"START-HERE.bat /check: exit {done.returncode}, {time.perf_counter() - began:.1f} s", flush=True)
    problems: "list[str]" = []
    if done.returncode != 0 or "match their hashes in SHA256SUMS" not in said:
        problems += ["START-HERE.bat /check did not pass the folder as it was unzipped"]
    return problems


# What START-HERE.bat says when its folder's Python is not beside it.
UNZIP_FIRST = "Unzip synthtwin's zip first (right-click it, Extract All)"


def alone_check(folder: pathlib.Path) -> "list[str]":
    """START-HERE.bat alone in an empty folder, as Explorer runs it from inside the zip: it must say to unzip first."""
    import tempfile

    place = pathlib.Path(tempfile.mkdtemp(prefix="start-here-alone-"))
    try:
        shutil.copyfile(folder / "START-HERE.bat", place / "START-HERE.bat")
        line = '"' + cmd_program() + '" /d /s /c ""' + str(place / "START-HERE.bat") + '" /check"'
        done = subprocess.run(
            line, cwd=place, env=proxied(), stdin=subprocess.DEVNULL, capture_output=True, check=False, timeout=120
        )
    finally:
        shutil.rmtree(place, ignore_errors=True)
    said = (done.stdout + done.stderr).decode("utf-8", "replace")
    print(said + f"START-HERE.bat alone in a folder: exit {done.returncode}", flush=True)
    if done.returncode != 1 or UNZIP_FIRST not in said:
        return ["START-HERE.bat alone in a folder did not say to unzip the zip first"]
    return []


# What pip prints when it reaches for the network (tests/test_bundle.py's
# NETWORK_WORDS, which ci.yml's bundle-test greps an install log for).
NETWORK_WORDS = (
    "Downloading",
    "Looking in indexes",
    "Looking in links: http",
    "Retrying",
    "Could not fetch URL",
    "ProxyError",
    "NewConnectionError",
    "Failed to establish",
    "pypi.org",
    "files.pythonhosted.org",
)


def scan_log(path: pathlib.Path) -> "list[str]":
    """The lines of an install log that show pip reaching for the network."""
    said = path.read_bytes().decode("utf-8", "replace")
    return [line for line in said.splitlines() if any(word in line for word in NETWORK_WORDS)]


def golden(python: str, pytest_only: pathlib.Path) -> int:
    line = (
        "import sys; sys.path[:0] = [" + repr(str(pytest_only)) + "]; import pytest; "
        "sys.exit(pytest.main(['-p', 'no:cacheprovider', '-q', " + ", ".join(repr(name) for name in GOLDEN) + "]))"
    )
    return subprocess.run([python, "-I", "-B", "-c", line], cwd=REPO, env=proxied(), check=False).returncode


def _summary(path: "pathlib.Path | None", title: str, steps: "list[dict[str, object]]", problems: "list[str]") -> None:
    if path is None:
        return
    lines = [f"### {title}", "", "| command, as typed | exit | seconds |", "|---|---|---|"]
    lines += [f"| `{step['typed']}` | {step['exit']} | {step['seconds']} |" for step in steps]
    lines += ["", "PASSED" if not problems else "FAILED: " + "; ".join(problems), ""]
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="rehearse_windows", description=__doc__.split("\n")[0])
    kinds = parser.add_subparsers(dest="kind", required=True)
    for name in ("trial", "redirect"):
        each = kinds.add_parser(name)
        each.add_argument("--route", required=True, choices=("powershell", "cmd", "guard", "direct"))
        each.add_argument("--work", required=True, type=pathlib.Path)
        each.add_argument("--tables", required=True, type=pathlib.Path)
        each.add_argument("--folder", type=pathlib.Path)
        each.add_argument("--python")
        each.add_argument("--utf8-screen", action="store_true", help="stand in for a console window's Unicode screen")
        each.add_argument("--summary", type=pathlib.Path)
    kinds.choices["trial"].add_argument("--stems", default=",".join(STEMS))
    kinds.choices["trial"].add_argument("--record", type=pathlib.Path)
    kinds.choices["redirect"].add_argument("--expect", required=True, choices=("pass", "record"))
    tampered = kinds.add_parser("tamper")
    tampered.add_argument("--folder", required=True, type=pathlib.Path)
    tampered.add_argument("--into", required=True, type=pathlib.Path)
    kinds.add_parser("start-check").add_argument("--folder", required=True, type=pathlib.Path)
    kinds.add_parser("scan-log").add_argument("log", type=pathlib.Path)
    tested = kinds.add_parser("golden")
    tested.add_argument("--python", required=True)
    tested.add_argument("--pytest-only", required=True, type=pathlib.Path)
    redone = kinds.add_parser("again")
    redone.add_argument("--python", required=True)
    redone.add_argument("--from", dest="source", required=True, type=pathlib.Path)
    redone.add_argument("--work", required=True, type=pathlib.Path)
    redone.add_argument("--stems", default=",".join(STEMS))
    compared = kinds.add_parser("compare")
    compared.add_argument("--assert", dest="held", nargs=2, action="append", default=[], type=pathlib.Path)
    compared.add_argument("--report", nargs=2, action="append", default=[], type=pathlib.Path)
    compared.add_argument("--stems", default=",".join(STEMS))
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass
    if args.kind in ("trial", "redirect"):
        extra = {"PYTHONIOENCODING": "utf-8"} if args.utf8_screen else {}
        route = Route(args.route, args.folder.resolve() if args.folder else None, args.python, extra)
        if args.kind == "redirect":
            status, made = redirect(route, args.work.resolve(), args.tables.resolve())
            written = [name for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json") if name in made]
            print(f"redirected run: exit {status}; description files written: {written}")
            if args.expect == "record":
                print("RECORDED, not held: the product's own rider for this output (lane WIN-b) is not on this line yet")
                return 0
            return 0 if status == 0 and len(written) == 3 else 1
        done = trial(route, args.work.resolve(), args.tables.resolve(), tuple(args.stems.split(",")))
        if args.record is not None:
            args.record.write_text(
                json.dumps({"route": args.route, "steps": done.steps, "problems": done.problems}, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        _summary(args.summary, f"The trial through the {args.route} route", done.steps, done.problems)
        for problem in done.problems:
            print("PROBLEM:", problem)
        print("the trial PASSED" if not done.problems else "the trial FAILED")
        return 0 if not done.problems else 1
    if args.kind == "start-check":
        problems = start_check(args.folder.resolve()) + alone_check(args.folder.resolve())
        print("\n".join(f"PROBLEM: {problem}" for problem in problems) or "START-HERE.bat passed the folder")
        return 1 if problems else 0
    if args.kind == "scan-log":
        reached = scan_log(args.log)
        print("\n".join(f"pip reached for the network: {line}" for line in reached) or "the install never reached for the network")
        return 1 if reached else 0
    if args.kind == "tamper":
        problems = tamper(args.folder.resolve(), args.into.resolve())
        print("\n".join(f"PROBLEM: {problem}" for problem in problems) or "the changed copy was refused before synthtwin started")
        return 1 if problems else 0
    if args.kind == "golden":
        return golden(args.python, args.pytest_only.resolve())
    if args.kind == "again":
        problems = again(args.python, args.source.resolve(), args.work.resolve(), tuple(args.stems.split(",")))
        print("\n".join(f"PROBLEM: {problem}" for problem in problems) or "the twin made here is the other system's, byte for byte")
        return 1 if problems else 0
    stems = tuple(args.stems.split(","))
    failed: "list[str]" = []
    for first, second in args.held:
        print(f"ASSERTED: {first} against {second}")
        failed += compare(first, second, stems, HELD)
        compare(first, second, stems, tuple(name for name in OUTPUTS if name not in HELD))
    for first, second in args.report:
        print(f"REPORTED (not held): {first} against {second}")
        compare(first, second, stems)
    print("\n".join(f"PROBLEM: {line}" for line in failed) or "every asserted pair is equal, byte for byte")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
