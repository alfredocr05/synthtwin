"""The packaging content allowlist must name exactly the shipped modules.

CI checks the built wheel and sdist against a file allowlist written
inline in `.github/workflows/ci.yml`, and that check refuses any archive
member it does not recognize. So a new module in `src/synthtwin/` breaks
the build job until someone remembers to add two lines to a workflow
file -- and the workflow file is the one file in this repository that
never runs on a developer machine. Phase 2 added five modules at once
and the allowlist was left at Phase 1's nine, which is exactly the
failure this file exists to make impossible: the CI file itself already
carries a comment about a check that outlived the rule it was checking,
and a second instance of the same defect is not a coincidence worth
tolerating.

The obligation runs in both directions on purpose. A module added
without an allowlist entry fails the build job on an unexpected file; a
module deleted while its entry stays fails the build job on a missing
required file. Testing only one direction would leave the other to be
discovered in CI, which is the situation this file replaces.
"""

import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"
PACKAGE = REPO / "src" / "synthtwin"

# The two prefixes the allowlist uses for the package's own source. The
# wheel holds the importable package; the sdist holds the source tree,
# so the same module is named twice under different roots.
WHEEL_PREFIX = "synthtwin/"
SDIST_PREFIX = "ROOT/src/synthtwin/"


def _allowlist_lines() -> list:
    """Return the allowlist's rule lines, comments and blanks removed.

    Accepts no arguments and reads the workflow file from the repository
    root. Deterministic: it is a text read and a filter, with no
    randomness and no dependence on the environment. Raises
    `AssertionError` when the heredoc that carries the allowlist cannot
    be found, because a silently empty rule list would let every
    assertion below pass while checking nothing.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    opener = "<<'ALLOWLIST'\n"
    start = text.find(opener)
    assert start != -1, (
        "the packaging allowlist heredoc was not found in "
        f"{WORKFLOW}. It begins with the line ending {opener.strip()} "
        "inside the build job's content-check step. If the step was "
        "renamed or restructured, update this test to find it again -- "
        "do not delete the test, because CI's packaging check is the "
        "only thing standing between an unreviewed file and the "
        "published artifacts."
    )
    body = text[start + len(opener) :]
    end = body.find("\n          ALLOWLIST\n")
    assert end != -1, (
        "the packaging allowlist heredoc in "
        f"{WORKFLOW} has no closing ALLOWLIST marker, so its rules "
        "cannot be read. Restore the marker."
    )
    lines = []
    for raw in body[:end].splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _entries(archive: str, prefix: str) -> set:
    """Return the file names the allowlist REQUIRES under one prefix.

    `archive` is `wheel` or `sdist`; `prefix` is the path prefix that
    archive uses for the package's own source. Optional and tree rules
    are excluded deliberately: this check is about the modules that must
    ship, and `py.typed` is optional because the package does not carry
    one today. Deterministic; raises nothing of its own.
    """
    found = set()
    for line in _allowlist_lines():
        parts = line.split()
        if len(parts) < 3:
            continue
        if parts[0] != archive or parts[1] != "required":
            continue
        if parts[2].startswith(prefix):
            found.add(parts[2][len(prefix) :])
    return found


def _shipped_modules() -> set:
    """Return the file names of every Python module in the package."""
    return {path.name for path in PACKAGE.glob("*.py")}


def test_the_wheel_allowlist_names_every_shipped_module() -> None:
    modules = _shipped_modules()
    listed = _entries("wheel", WHEEL_PREFIX)
    assert listed == modules, (
        "the wheel allowlist in .github/workflows/ci.yml does not match "
        "the package. Missing from the allowlist: "
        f"{sorted(modules - listed)}. Listed but not in the package: "
        f"{sorted(listed - modules)}. Add or remove the matching "
        "'wheel required synthtwin/<name>.py' line; otherwise the build "
        "job fails on an unexpected or a missing file."
    )


def test_the_sdist_allowlist_names_every_shipped_module() -> None:
    modules = _shipped_modules()
    listed = _entries("sdist", SDIST_PREFIX)
    assert listed == modules, (
        "the sdist allowlist in .github/workflows/ci.yml does not match "
        "the package. Missing from the allowlist: "
        f"{sorted(modules - listed)}. Listed but not in the package: "
        f"{sorted(listed - modules)}. Add or remove the matching "
        "'sdist required ROOT/src/synthtwin/<name>.py' line."
    )


def test_the_allowlist_actually_carries_rules() -> None:
    # A vacuity floor. If the heredoc were ever emptied, or the parser
    # above stopped matching its shape, both checks would compare two
    # empty sets and pass while the real allowlist went unexamined.
    lines = _allowlist_lines()
    assert len(lines) > 20, (
        f"only {len(lines)} allowlist rules were parsed out of "
        f"{WORKFLOW}, which is fewer than the file is known to carry. "
        "The parser above has probably stopped matching the workflow's "
        "shape, which would make the checks in this file vacuous."
    )
