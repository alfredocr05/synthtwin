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
what they assert is red here before it is red there.
"""

import contextlib
import io
import pathlib
import re
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
