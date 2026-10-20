"""The dependency introduction (plans P1-D2, D5, P4-D409 and P4-D410).

Every floor is declared in four files -- the package's own metadata and
the three lock inputs -- and a floor that is declared in one place and
tested in another is not a tested floor at all. This file fails if they
ever drift apart, if a runtime dependency appears that no plan
authorized, if a library outside the December set (plan P4-D409 part 1)
enters any requirement file, and if a lock was compiled for another
Python than the floor the package declares.
"""

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

# Exactly the runtime dependencies the ratified plans authorize, each
# with the zone it may run in (plan P4-D409 part 2; the offline scanner
# holds each to its enumerated names): pandas by Phase 1 (plan P1-D2),
# zone R, reduced to `read_csv` and its own string storage; numpy by
# Phase 2 (plan P2-D8), zone G, reduced to the one random stream the
# generator draws from -- its REDUCTIONS made published statistics depend
# on row order at Phase 1 review round 1, so no published statistic
# comes from one; pyarrow (zone R, the reader and text held as exact
# bytes) and scipy (zone D's search side and zone P) by the December
# library set (plans P4-D409 and P4-D410).
AUTHORIZED = {"numpy", "pyarrow", "scipy", "pandas"}

# The one OPTIONAL dependency (plan P4-D409 part 4, the owner's "Yes,
# gated" of 2026-10-19): numba compiles the audited polish kernel and
# nothing else, and has no wheel for Intel Macs, which its marker leaves
# out. The extra's name, the floor and the marker are pinned here.
OPTIONAL = {"polish": ("numba", "0.68.0")}
NO_INTEL_MAC = "sys_platform != 'darwin' or platform_machine != 'x86_64'"

# The TEST-ONLY libraries (zone P): openpyxl reads a twin workbook
# independently (owner ruling 2026-09-15), statsmodels and scikit-learn
# cross-check the analyst kit (plan P4-D409). src/ never imports them.
TEST_ONLY = {"openpyxl", "statsmodels", "scikit-learn"}

# The development and build tools of plan D5.
TOOLS = {"pytest", "ruff", "mypy", "build", "hatchling", "twine"}

# THE FLOOR PYTHON (owner Q1 of 2026-10-19: "3.11 and later"). Every lock
# is compiled for it, because a universal lock compiled for a newer
# Python leaves the floor's interpreter without a pin.
FLOOR_PYTHON = "3.11"

# The libraries plan P4-D409 measured and did NOT adopt. None may appear
# in any requirement file, as a root or in a compiled closure.
NOT_ADOPTED = {
    "lifelines",
    "polars",
    "duckdb",
    "python-calamine",
    "xlsxwriter",
    "networkx",
    "pyreadstat",
}

INPUTS = ("requirements-dev.in", "requirements-install.in", "requirements-min.in")
LOCKS = ("requirements-dev.lock", "requirements-install.lock", "requirements-min.lock")


def _pyproject_text() -> str:
    # Read as text rather than with a TOML parser, as it always was: the
    # checks below compare the declared strings themselves.
    return (REPO / "pyproject.toml").read_text(encoding="utf-8")


def _block(text: str, opening: str) -> str:
    start = text.index(opening)
    return text[start : text.index("]", start)]


def _declared_floors() -> dict:
    floors = {}
    for piece in _block(_pyproject_text(), "dependencies = [").split('"')[1::2]:
        name, _, bound = piece.partition(">=")
        floors[name.strip()] = bound.strip()
    return floors


def _requirement_lines(name: str) -> "list[str]":
    """The requirement lines of one input file, comments and options left out."""
    found = []
    for raw in (REPO / name).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith(("#", "-")):
            found += [line]
    return found


def _minimum_pins() -> dict:
    """The versions the `minimums` CI job actually installs."""
    pins = {}
    for line in _requirement_lines("requirements-min.in"):
        name, _, pinned = line.partition("==")
        pins[name.strip()] = pinned.strip()
    return pins


def _lock_pins(name: str) -> dict:
    """The exact versions a compiled lock pins, by package name.

    A package the lock splits by Python (numpy 2.4.6 on 3.11, 2.5 on
    3.12 and later) keeps every version, in the order the lock writes
    them.
    """
    pins: dict = {}
    text = (REPO / name).read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        head = line.split(" ")[0]
        package, sep, version = head.partition("==")
        if sep:
            pins[package.strip()] = pins.get(package.strip(), []) + [version.strip()]
    return pins


def _lock_markers(name: str) -> dict:
    """Each pinned line's environment marker, by package and version."""
    markers = {}
    text = (REPO / name).read_text(encoding="utf-8")
    for raw in text.splitlines():
        if raw.startswith((" ", "#", "-")) or "==" not in raw:
            continue
        line = raw.rstrip(" \\")
        requirement, _, marker = line.partition(" ; ")
        markers[requirement.strip()] = marker.strip()
    return markers


def test_the_minimum_lock_pins_the_declared_floors() -> None:
    # Review item P1-R2-F8: the input file kept the floors while the
    # LOCK -- the file the job installs -- could be regenerated at newer
    # versions, so a regression against the advertised floors merged
    # with the minimums job green.
    declared = _declared_floors()
    pinned = _lock_pins("requirements-min.lock")
    for name, bound in declared.items():
        assert pinned.get(name) == [bound], (
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


def _input_floors(name: str) -> dict:
    """Each requirement's lower bound in one input file, its marker set aside."""
    floors = {}
    for line in _requirement_lines(name):
        requirement = line.partition(";")[0].strip()
        for separator in (">=", "=="):
            if separator in requirement:
                package, _, bound = requirement.partition(separator)
                floors[package.strip()] = bound.strip()
                break
    return floors


def test_only_the_authorized_runtime_dependencies_exist() -> None:
    assert set(_declared_floors()) == AUTHORIZED, (
        "a runtime dependency outside the plan's authorization appeared; "
        "each one needs a written justification reviewed adversarially "
        "(plan D5) and its zone (plan P4-D409)"
    )


def test_every_declared_floor_is_repeated_in_every_input_file() -> None:
    """The floors in pyproject.toml, requirements-dev.in, -install.in and -min.in agree.

    One floor, four files: the package's metadata, the development lock's
    input, the institutional install's input and the minimums job's pins.
    A floor raised in one of them and left in another is a version
    somebody is promised and nobody installs.
    """
    declared = _declared_floors()
    for name in INPUTS:
        inputs = _input_floors(name)
        for package, bound in declared.items():
            assert package in inputs, (
                f"{package} is a runtime dependency but is missing from "
                f"{name}, so the floor installed from it is not the floor "
                "the package declares"
            )
            assert inputs[package] == bound, (
                f"{package} declares >={bound} in pyproject.toml but "
                f"{inputs[package]} in {name}"
            )


def test_the_floor_check_would_notice_a_drifted_floor() -> None:
    """The comparison above, shown failing on a floor moved in one file."""
    declared = _declared_floors()
    drifted = dict(_input_floors("requirements-install.in"))
    drifted["numpy"] = "2.5.4"
    assert drifted["numpy"] != declared["numpy"]
    assert {k: v for k, v in drifted.items() if k in declared} != declared


def test_the_optional_polish_extra_is_numba_alone_and_leaves_intel_macs_out() -> None:
    """numba is optional, gated, and absent where no wheel exists (plan P4-D409 part 4)."""
    text = _pyproject_text()
    assert "[project.optional-dependencies]" in text
    for extra, (package, floor) in OPTIONAL.items():
        block = _block(text, f"{extra} = [")
        entries = block.split('"')[1::2]
        assert entries == [f"{package}>={floor} ; {NO_INTEL_MAC}"], entries
        dev = [line for line in _requirement_lines("requirements-dev.in") if line.startswith(package)]
        assert dev == [f"{package}>={floor} ; {NO_INTEL_MAC}"], (
            f"requirements-dev.in must repeat the {extra} extra's floor and marker"
        )
        assert package not in _input_floors("requirements-install.in"), (
            f"{package} enters the institutional install only when its gate is "
            "proved and the plan says so (lanes MPn and DEP-2)"
        )
        markers = _lock_markers("requirements-dev.lock")
        assert markers.get(f"{package}=={floor}") is not None, (
            f"the development lock must pin {package}=={floor}"
        )
        assert "darwin" in markers[f"{package}=={floor}"]
    assert "numba" not in set(_declared_floors()), "numba is never a hard dependency"


def test_the_requirement_files_name_exactly_the_december_set() -> None:
    """No library outside plan P4-D409's set enters any requirement file.

    The roots are counted file by file; the compiled closures are read
    for the libraries the plan measured and did not adopt (lifelines
    above all, which pulls matplotlib and a source-only package).
    """
    optional = {package for package, _ in OPTIONAL.values()}
    assert _roots("requirements-dev.in") == AUTHORIZED | optional | TEST_ONLY | TOOLS
    assert _roots("requirements-min.in") == AUTHORIZED | {"pytest"}
    for name in LOCKS:
        pinned = set(_lock_pins(name))
        assert not pinned & NOT_ADOPTED, (
            f"{name} pins {sorted(pinned & NOT_ADOPTED)}, which plan P4-D409 "
            "measured and did not adopt"
        )
    assert not set(_lock_pins("requirements-install.lock")) & (TEST_ONLY | optional), (
        "a test-only or optional library reached the institutional install"
    )


def test_the_lock_still_carries_the_wheel_only_rule() -> None:
    # The rule has to live in the lock itself, because a consumer that
    # omits the option on the command line must still be refused source
    # archives (plan D5). A newer resolver drops the line on
    # regeneration, so this is a standing check, not a formality.
    for name in LOCKS:
        text = (REPO / name).read_text(encoding="utf-8")
        assert "\n--only-binary :all:\n" in text, name


def test_every_lock_is_compiled_for_the_floor_python() -> None:
    """Each lock's own header names the floor Python it was resolved for."""
    for name in LOCKS:
        header = (REPO / name).read_text(encoding="utf-8").splitlines()[1]
        assert "--universal" in header and "--generate-hashes" in header, header
        assert f"--python-version {FLOOR_PYTHON} " in header, (
            f"{name} was compiled for another Python than the floor "
            f"{FLOOR_PYTHON}: {header}"
        )


def test_the_lock_pins_the_runtime_dependencies_with_hashes() -> None:
    text = (REPO / "requirements-dev.lock").read_text(encoding="utf-8")
    for name in AUTHORIZED | TEST_ONLY:
        assert f"\n{name}==" in text, f"{name} is not pinned in the lock"
    assert text.count("--hash=sha256:") > 100


def test_the_install_lock_covers_the_runtime_closure() -> None:
    # The file a user on a locked-down machine installs from (plan D5),
    # and the file the offline bundle is built from (plan P4-D409).
    install = REPO / "requirements-install.lock"
    assert install.is_file(), (
        "the hash-pinned runtime install file is part of this phase: it "
        "is what SECURITY.md names as the supported institutional "
        "install path"
    )
    text = install.read_text(encoding="utf-8")
    assert "--only-binary :all:" in text
    for name in AUTHORIZED:
        assert f"\n{name}==" in text, f"{name} is not in the install closure"
    assert "\nnumpy==" in text, (
        "numpy must still be pinned in the closure: the generator draws "
        "its one random stream from it and pandas requires it as well"
    )


def test_the_floor_python_installs_exactly_the_declared_floors() -> None:
    """On 3.11 the install lock pins each runtime library at its floor.

    numpy and scipy split by Python (their newest releases need 3.12):
    the line the floor Python reads must be the floor itself, so the
    minimums job and an institutional install on 3.11 run the same
    versions.
    """
    declared = _declared_floors()
    markers = _lock_markers("requirements-install.lock")
    for name, bound in declared.items():
        marker = markers.get(f"{name}=={bound}")
        assert marker is not None, f"the install lock never pins {name}=={bound}"
        assert marker in ("", "python_full_version < '3.12'"), (name, marker)


def _roots(name: str) -> set:
    """The packages a requirement INPUT names directly."""
    roots = set()
    for line in _requirement_lines(name):
        requirement = line.partition(";")[0].strip()
        for separator in (">=", "==", "<=", "~=", "<", ">"):
            if separator in requirement:
                roots.add(requirement.split(separator)[0].strip())
                break
        else:
            roots.add(requirement)
    return roots


def test_the_install_input_names_exactly_the_authorized_roots() -> None:
    # Review item P1-R4-F5: numpy was removed as a root, but nothing
    # stopped it -- or anything else -- coming back. A root here is a
    # package the institutional install requires by name, whatever
    # another library happens to depend on.
    assert _roots("requirements-install.in") == AUTHORIZED, (
        "the institutional install must require exactly the runtime "
        "dependencies the package declares; anything else is a package "
        "installed on a user's machine that no plan authorizes"
    )


def test_python_floor_matches_the_supported_matrix() -> None:
    assert f'requires-python = ">={FLOOR_PYTHON}"' in _pyproject_text()


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
