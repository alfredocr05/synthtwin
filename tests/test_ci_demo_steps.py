"""The build job's demonstration steps, run here the way CI runs them.

`.github/workflows/ci.yml` builds a neutral table, profiles it with the
installed command, checks the description in a block of Python written
into the workflow, builds the twin and checks that too. Those blocks run
on no developer machine, and the profiling check went stale three times:
a ten-column shape for a thirteen-column table, a default floor of eleven
after it became one, and then one after stage 3 made it eleven again --
found only when stage 3 first reached CI (run 36121790821, 2026-09-25),
with the whole matrix skipped behind it. This reads the same blocks out
of the workflow and runs them against this tree, so the next change to
what they assert is red here before it is red there. The decontam job's
MESSAGES block, which scans commit messages (plan P4-D362), is run the
same way, on this checkout's history and on histories built here.
"""

import contextlib
import hashlib
import importlib.util
import io
import os
import pathlib
import re
import subprocess
import sys

import pytest

from synthtwin import cli

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"


def _block(tag: str) -> str:
    """One `<<'TAG'` block of the workflow, as the shell hands it to Python."""
    text = WORKFLOW.read_text(encoding="utf-8")
    found = re.search(r"<<'" + tag + r"'\n(.*?)\n[ ]*" + tag + r"\n", text, re.DOTALL)
    assert found is not None, f"ci.yml no longer carries its {tag} block"
    lines = found.group(1).splitlines()
    pad = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    return "\n".join(line[pad:] for line in lines) + "\n"


def _python(tag: str) -> "tuple[int, str]":
    """Run one block as a script; its exit status and what it printed."""
    printed = io.StringIO()
    status = 0
    with contextlib.redirect_stdout(printed):
        try:
            exec(compile(_block(tag), f"ci.yml:{tag}", "exec"), {"__name__": "__main__"})
        except SystemExit as stop:
            status = stop.code if isinstance(stop.code, int) else 1
    return status, printed.getvalue()


def _command(argv: "list[str]") -> int:
    """The installed command, as the step calls it, with its output kept quiet."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            return cli.main(argv)
        except SystemExit as stop:
            return stop.code if isinstance(stop.code, int) else 1


def test_the_build_jobs_demonstration_steps_pass_on_this_tree(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MAKE, profile, CHECK, generate and TWIN, in the workflow's order."""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    # The two commands are the workflow's own; a step that changes them
    # changes this test's premise, so say so rather than drift.
    assert '/bin/synthtwin" profile "$DEMO/table.csv"' in workflow
    assert "--identifier record_code" in workflow
    assert '"$DEMO/table-profile.json" --seed 7' in workflow
    monkeypatch.chdir(REPO)
    monkeypatch.setenv("RUNNER_TEMP", f"{tmp_path}")
    monkeypatch.setattr(sys, "path", list(sys.path))
    demo = tmp_path / "demo"
    demo.mkdir()
    status, printed = _python("MAKE")
    assert status == 0, printed
    assert _command(["profile", f"{demo / 'table.csv'}", "--identifier", "record_code"]) == 0
    status, printed = _python("CHECK")
    assert status == 0, printed
    assert _command(["generate", f"{demo / 'table-profile.json'}", "--seed", "7"]) == 0
    status, printed = _python("TWIN")
    assert status == 0, printed


# -- the decontam job's MESSAGES block -------------------------------------

CANARY = "zqvortex"  # the invented token of tests/test_decontamination.py


def _message_scanner() -> "object":
    """tools/hooks/check_messages.py, loaded fresh under the name MESSAGES imports."""
    spec = importlib.util.spec_from_file_location(
        "check_messages", REPO / "tools" / "hooks" / "check_messages.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_env() -> "dict[str, str]":
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    for role in ("AUTHOR", "COMMITTER"):
        env[f"GIT_{role}_NAME"] = "synthtwin-test"
        env[f"GIT_{role}_EMAIL"] = "synthtwin-test@example.invalid"
    return env


def _git(where: pathlib.Path, *arguments: str) -> str:
    done = subprocess.run(
        ["git", "-C", f"{where}", *arguments], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False, timeout=120, env=_git_env(),
    )
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout.strip()


def _commit(repo: pathlib.Path, message: str) -> str:
    _git(repo, "commit", "-q", "--allow-empty", "--no-verify", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _canary_manifest(folder: pathlib.Path) -> pathlib.Path:
    """A manifest denying the canary alone, in the committed one's shape."""
    lines = ["# test manifest", "# entry_count: 1", "# n_max: 1"]
    for name in (
        "snapshot_tree_sha256", "wordlist_sha256", "seed_sha256",
        "grammar_sha256", "magic_sha256", "tokenizer_sha256",
    ):
        lines += [f"# {name}: {hashlib.sha256(name.encode()).hexdigest()}"]
    lines += ["#", hashlib.sha256(CANARY.encode()).hexdigest()]
    path = folder / "manifest.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _messages(monkeypatch: pytest.MonkeyPatch, **event: str) -> "tuple[int, str]":
    """The MESSAGES block once, under the event the job would see."""
    for name in ("EVENT_NAME", "HEAD_SHA", "BASE_SHA"):
        monkeypatch.delenv(name, raising=False)
    for name, value in event.items():
        monkeypatch.setenv(name, value)
    return _python("MESSAGES")


def test_the_decontam_jobs_message_scan_passes_on_this_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MESSAGES on this checkout, on a push and on a pull request.

    It needs the history the job fetches with fetch-depth: 0. A checkout
    without it -- the tests job's own is shallow -- is left to the job,
    where the scan refuses it aloud; the next case holds that refusal.
    """
    scanner = _message_scanner()
    for name, value in _git_env().items():
        monkeypatch.setenv(name, value)
    shallow = _git(REPO, "rev-parse", "--is-shallow-repository")
    if shallow != "false" or not scanner.holds_commit(REPO, scanner.GRANDFATHER):  # type: ignore[attr-defined]
        pytest.skip("this checkout does not hold the history past the grandfather")
    head = _git(REPO, "rev-parse", "HEAD")
    monkeypatch.chdir(REPO)
    monkeypatch.setattr(sys, "path", list(sys.path))
    saved = sys.modules.pop("check_messages", None)
    try:
        for event in ("push", "pull_request"):
            status, printed = _messages(
                monkeypatch, EVENT_NAME=event, HEAD_SHA=head,
                BASE_SHA=scanner.GRANDFATHER,  # type: ignore[attr-defined]
            )
            assert status == 0, printed
            assert "past the grandfather line" in printed and ": clean," in printed
    finally:
        sys.modules.pop("check_messages", None)
        if saved is not None:
            sys.modules["check_messages"] = saved


def test_the_decontam_jobs_message_scan_reads_the_pull_request_and_refuses_a_cut_history(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MESSAGES on a history built here, its scanner pointed at that history.

    The feature branch starts from the base branch's tip, as a branch
    usually does, so the base's own canary is in the feature's history:
    it and one before the grandfather are not the pull request's, and
    are not reported on it; the pull request's own is reported and never
    printed; a push reads the whole branch; a history without the
    grandfather and a shallow clone both fail instead of passing.
    """
    repo = tmp_path / "history"
    repo.mkdir()
    _git(repo, "init", "-q")
    _commit(repo, "the first commit")
    _commit(repo, f"published before the guard {CANARY}")
    grandfather = _commit(repo, "the grandfather")
    base = _commit(repo, f"on the base branch {CANARY}")
    _git(repo, "checkout", "-q", "-b", "feature", base)
    clean = _commit(repo, "a clean feature commit")
    dirty = _commit(repo, f"a feature commit {CANARY}")

    scanner = _message_scanner()
    monkeypatch.setattr(scanner, "GRANDFATHER", grandfather)
    monkeypatch.setattr(scanner, "MANIFEST", _canary_manifest(tmp_path))
    monkeypatch.setitem(sys.modules, "check_messages", scanner)
    monkeypatch.setattr(sys, "path", list(sys.path))
    for name, value in _git_env().items():
        monkeypatch.setenv(name, value)
    monkeypatch.chdir(repo)

    status, printed = _messages(
        monkeypatch, EVENT_NAME="pull_request", HEAD_SHA=clean, BASE_SHA=base
    )
    assert status == 0 and "clean, 1 commit scanned" in printed, printed
    status, printed = _messages(
        monkeypatch, EVENT_NAME="pull_request", HEAD_SHA=dirty, BASE_SHA=base
    )
    assert status == 1, printed
    assert re.findall(r"^MATCH commit ([0-9a-f]{40}) ", printed, re.M) == [dirty]
    assert CANARY not in printed
    status, printed = _messages(monkeypatch, EVENT_NAME="push")
    assert status == 1, printed
    assert re.findall(r"^MATCH commit ([0-9a-f]{40}) ", printed, re.M) == [dirty, base]
    _git(repo, "checkout", "-q", base)
    status, printed = _messages(monkeypatch, EVENT_NAME="push")
    assert re.findall(r"^MATCH commit ([0-9a-f]{40}) ", printed, re.M) == [base]

    monkeypatch.setattr(scanner, "GRANDFATHER", "0" * 40)
    status, printed = _messages(monkeypatch, EVENT_NAME="push")
    assert status == 2 and "NOT SCANNED" in printed, printed
    monkeypatch.setattr(scanner, "GRANDFATHER", grandfather)
    shallow = tmp_path / "shallow"
    _git(tmp_path, "clone", "-q", "--depth", "1", repo.as_uri(), f"{shallow}")
    monkeypatch.chdir(shallow)
    status, printed = _messages(
        monkeypatch, EVENT_NAME="pull_request", HEAD_SHA=dirty, BASE_SHA=base
    )
    assert status == 2 and "SHALLOW" in printed, printed


def test_the_decontam_job_fetches_the_history_its_message_scan_reads() -> None:
    """MESSAGES reads every commit past the grandfather, so its checkout takes them all.

    Without `fetch-depth: 0` the job would still go red -- the scan
    refuses a shallow clone aloud -- and this names the cause first.
    """
    workflow = WORKFLOW.read_text(encoding="utf-8")
    job = workflow[workflow.index("\n  decontam:\n") : workflow.index("\n  offline-static:\n")]
    assert "<<'MESSAGES'" in job, "the MESSAGES block has left the decontam job"
    steps = re.split(r"\n      - ", job)
    checkouts = [step for step in steps if step.startswith("uses: actions/checkout@")]
    assert len(checkouts) == 1, checkouts
    assert re.search(r"^ +fetch-depth: 0$", checkouts[0], re.M), checkouts[0]
