"""The dependency introduction (plan P1-D2, D5).

Two floors are declared in two files -- the package's own metadata and
the lock's input file -- and a floor that is declared in one place and
tested in another is not a tested floor at all. This file fails if they
ever drift apart, and if a runtime dependency ever appears that the
plan did not authorize.
"""

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

# Exactly the runtime dependencies the ratified plans authorize: pandas
# by Phase 1 (plan P1-D2) and numpy by Phase 2 (plan P2-D8). numpy left
# this set at Phase 1 review round 1, because its REDUCTIONS made
# published statistics depend on row order -- so the profiler still
# computes its own statistics and imports numpy nowhere. What Phase 2
# brings back is the one random stream the generator draws from, reduced
# by the offline scanner to `default_rng` and one `integers` call.
AUTHORIZED = {"numpy", "pandas"}


def _pyproject_text() -> str:
    # Read as text rather than with a TOML parser: the standard library
    # gained one only in Python 3.11, and this check has to run on the
    # oldest supported interpreter -- which is exactly the cell where
    # the declared floors are installed and tested.
    return (REPO / "pyproject.toml").read_text(encoding="utf-8")


def _declared_floors() -> dict:
    text = _pyproject_text()
    start = text.index("dependencies = [")
    block = text[start : text.index("]", start)]
    floors = {}
    for piece in block.split('"')[1::2]:
        name, _, bound = piece.partition(">=")
        floors[name.strip()] = bound.strip()
    return floors


def _minimum_pins() -> dict:
    """The versions the `minimums` CI job actually installs."""
    pins = {}
    text = (REPO / "requirements-min.in").read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        name, _, pinned = line.partition("==")
        pins[name.strip()] = pinned.strip()
    return pins


def _lock_pins(name: str) -> dict:
    """The exact versions a compiled lock pins, by package name."""
    pins = {}
    text = (REPO / name).read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        head = line.split(" ")[0]
        package, sep, version = head.partition("==")
        if sep:
            pins[package.strip()] = version.strip()
    return pins


def test_the_minimum_lock_pins_the_declared_floors() -> None:
    # Review item P1-R2-F8: the input file kept the floors while the
    # LOCK -- the file the job installs -- could be regenerated at newer
    # versions, so a regression against the advertised floors merged
    # with the minimums job green.
    declared = _declared_floors()
    pinned = _lock_pins("requirements-min.lock")
    for name, bound in declared.items():
        assert pinned.get(name) == bound, (
            f"requirements-min.lock installs {name}=={pinned.get(name)}, "
            f"but the declared floor is {bound}. The job would then test "
            "a version the package does not claim to support at its "
            "lower bound."
        )


def test_the_job_installs_exactly_the_declared_floors() -> None:
    # Review item P1-R1-F11: the drift check read requirements-dev.in
    # while the job installed requirements-min.lock, so the two could
    # part company with every test still green.
    declared = _declared_floors()
    pinned = _minimum_pins()
    for name, bound in declared.items():
        assert name in pinned, (
            f"{name} declares a floor of {bound} but the minimums job "
            "does not install it, so the floor is not tested at all"
        )
        assert pinned[name] == bound, (
            f"{name} declares >={bound} in pyproject.toml but the "
            f"minimums job installs =={pinned[name]}"
        )


def _input_floors() -> dict:
    floors = {}
    text = (REPO / "requirements-dev.in").read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        name, _, bound = line.partition(">=")
        floors[name.strip()] = bound.strip()
    return floors


def test_only_the_authorized_runtime_dependencies_exist() -> None:
    assert set(_declared_floors()) == AUTHORIZED, (
        "a runtime dependency outside the plan's authorization appeared; "
        "each one needs a written justification reviewed adversarially "
        "(plan D5)"
    )


def test_the_two_declared_floors_agree() -> None:
    declared = _declared_floors()
    inputs = _input_floors()
    for name, bound in declared.items():
        assert name in inputs, (
            f"{name} is a runtime dependency but is missing from "
            "requirements-dev.in, so the floor CI installs is not the "
            "floor the package declares"
        )
        assert inputs[name] == bound, (
            f"{name} declares >={bound} in pyproject.toml but "
            f">={inputs[name]} in requirements-dev.in"
        )


def test_the_lock_still_carries_the_wheel_only_rule() -> None:
    # The rule has to live in the lock itself, because a consumer that
    # omits the option on the command line must still be refused source
    # archives (plan D5). A newer resolver drops the line on
    # regeneration, so this is a standing check, not a formality.
    text = (REPO / "requirements-dev.lock").read_text(encoding="utf-8")
    assert "--only-binary :all:" in text


def test_the_lock_pins_the_runtime_dependencies_with_hashes() -> None:
    text = (REPO / "requirements-dev.lock").read_text(encoding="utf-8")
    for name in AUTHORIZED:
        assert f"\n{name}==" in text, f"{name} is not pinned in the lock"
    assert text.count("--hash=sha256:") > 100


def test_the_install_lock_covers_the_runtime_closure() -> None:
    # The file a user on a locked-down machine installs from (plan D5).
    install = REPO / "requirements-install.lock"
    assert install.is_file(), (
        "the hash-pinned runtime install file is part of this phase: it "
        "is what SECURITY.md names as the supported institutional "
        "install path"
    )
    text = install.read_text(encoding="utf-8")
    assert "--only-binary :all:" in text
    for name in AUTHORIZED:
        assert f"\n{name}==" in text
    assert "\nnumpy==" in text, (
        "numpy must still be pinned in the closure: the generator draws "
        "its one random stream from it and pandas requires it as well"
    )


def _roots(name: str) -> set:
    """The packages a requirement INPUT names directly."""
    roots = set()
    text = (REPO / name).read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        for separator in (">=", "==", "<=", "~=", "<", ">"):
            if separator in line:
                roots.add(line.split(separator)[0].strip())
                break
        else:
            roots.add(line)
    return roots


def test_the_install_input_names_exactly_the_authorized_roots() -> None:
    # Review item P1-R4-F5: numpy was removed as a root, but nothing
    # stopped it -- or anything else -- coming back. A root here is a
    # package the institutional install requires by name, whatever
    # pandas happens to depend on.
    assert _roots("requirements-install.in") == AUTHORIZED, (
        "the institutional install must require exactly the runtime "
        "dependencies the package declares; anything else is a package "
        "installed on a user's machine that no plan authorizes"
    )


def test_python_floor_matches_the_supported_matrix() -> None:
    assert 'requires-python = ">=3.10"' in _pyproject_text()


# -- the TEST-ONLY cross-check reader -----------------------------------
#
# openpyxl is not a dependency of synthtwin and `src` imports it
# nowhere: it exists in the SUITE as a second opinion, so that a fault
# in synthtwin's own workbook reader cannot hide behind itself. CI's
# `minimums` cell installs the declared floors and then the wheel with
# `--no-deps`, so it is absent there, and a test that goes red on its
# absence tells CI the product is broken when it is not. The answer is
# that it is named in ONE place, which skips and says why; these two
# tests hold that. (2026-09-20: twenty-five cases were red on
# `minimums`, from twenty-three `importorskip` copies and two bare
# imports.)
CROSS_CHECK_READER = "openpyxl"
NAMES_IT = "tests/crosscheck.py"
# The one other file allowed to name it, with the reason. It is a
# maintainer measurement driver run BY HAND, no test loads it, and a
# pytest helper has no business inside `tools/`; on a floors-only
# environment it simply cannot run, which is the right answer for it.
NAMES_IT_TOO = {
    "tools/measurements/kpi_datetime_speed.py":
        "a measurement driver run by hand; no test imports it",
}


def _files_naming_the_reader() -> "set[str]":
    """Every file of tests/ and tools/ that IMPORTS or asks for openpyxl."""
    naming = set()
    for folder in ("tests", "tools"):
        for path in sorted((REPO / folder).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            relative = path.relative_to(REPO).as_posix()
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                named = []
                if isinstance(node, ast.Import):
                    named = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    named = [node.module or ""]
                elif isinstance(node, ast.Call):
                    named = [
                        argument.value
                        for argument in node.args
                        if isinstance(argument, ast.Constant)
                        and isinstance(argument.value, str)
                    ]
                if any(
                    name == CROSS_CHECK_READER
                    or name.startswith(CROSS_CHECK_READER + ".")
                    for name in named
                ):
                    naming.add(relative)
    return naming


def test_the_test_only_cross_check_reader_is_named_in_one_place() -> None:
    """A twenty-sixth case inherits the skip instead of carrying a copy of it."""
    naming = _files_naming_the_reader()
    assert naming == {NAMES_IT} | set(NAMES_IT_TOO), (
        f"{CROSS_CHECK_READER} is named in {sorted(naming)}. It is TEST-ONLY "
        f"and absent from CI's `minimums` cell, so it belongs in {NAMES_IT} "
        "alone, where its absence is ONE skip with ONE reason: ask through "
        "crosscheck.reader(), crosscheck.read_excel() or "
        "crosscheck.fixture_writer() rather than importing it here."
    )


def test_each_way_the_cross_check_reader_can_be_absent_has_its_own_reason() -> None:
    """Three different facts, three messages -- because `-rs` prints each once.

    A shared skip message is printed once for every case that carries
    it, so a message true of most of them and false of the rest tells a
    reader of the `minimums` log the opposite of what happened. The
    review of 2026-09-21 found one message saying "everything it asks
    synthtwin's own workbook code ran before this point" over four
    cases where nothing of synthtwin had run at all.
    """
    source = (REPO / NAMES_IT).read_text(encoding="utf-8")
    reasons = set()
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "skip"
        ):
            named = [
                ast.unparse(argument).split(" + ")[0] for argument in node.args
            ]
            reasons |= set(named)
    assert len(reasons) == 3, (
        f"the skips in {NAMES_IT} name {sorted(reasons)}: there are three "
        "different facts about an absent cross-check reader and each needs "
        "its own message, because -rs prints each one once for every case "
        "that carries it"
    )
    from tests import crosscheck

    texts = {crosscheck.REASON, crosscheck.REASON_FIXTURE, crosscheck.REASON_PART}
    assert len(texts) == 3, "two of the three reasons read the same"
    assert "ran before this point" in crosscheck.REASON
    assert "NOTHING OF SYNTHTWIN HAS RUN" in crosscheck.REASON_FIXTURE
    assert "Not measured here: " in crosscheck.REASON_PART
