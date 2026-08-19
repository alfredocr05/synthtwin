"""`--smallest-group` below eleven, end to end (plan amendment A-P3-11).

THE DEFECT THIS FILE EXISTS TO KEEP CLOSED. `synthtwin profile t.csv
--smallest-group 2` exited 0 and wrote both files; `synthtwin generate`
and `synthtwin validate` then refused that description, because the
contract required `small_cell_floor >= 11` and the strict loader
enforced it. The refusal ended by telling the person to make the
description again by running `synthtwin profile` and to use the file
exactly as it writes it -- which is exactly what they had done. A
documented option produced an unusable file.

THE OWNER RULED IT THROUGH EVERYWHERE, on 2026-08-14, knowing the cost.
So this file holds two halves that only make sense together:

1. THE WORKFLOW RUNS. profile, generate and validate all accept a floor
   below the default, and the small counts really are published -- a
   test that only proved "exit 0" would pass on a build that quietly
   ignored the number.

2. THE COST IS VISIBLE. The warning at profile time says what a small
   count can reveal about a PERSON, and each of the three written pages
   -- the plain-language summary, the generation report, the quality
   report -- says on its OWN face that it was made under a lowered
   floor. That last property is asserted one file at a time, because
   that is how a person meets these files: one is emailed, the other
   four stay behind.

AND THE STRICT LOADER IS STILL STRICT. The only refusal withdrawn is the
one against the floor's own value. A floor of zero is still refused, a
description that holds something back at a floor of one is still
refused, and a description broken anywhere else is refused exactly as
before.

Every table here is built by the seeded neutral builders in
`fixtures.py` (plan D13: no data-format file is ever committed), and
every description by the REAL producer.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)
from synthtwin.cli import main

# Two floors below the default, and they are different cases. Two is an
# ordinary lowering. One is the boundary the contract now stops at, and
# the value at which nothing is held back at all -- which is where an
# arithmetic assumption of "there is always a pooled remainder" would
# show up.
_LOWERED = (2, 1)

_DEFAULT = taxonomy.Settings().small_cell_floor


def _table(folder: pathlib.Path) -> pathlib.Path:
    """The every-role table, whose `region` column has one rare label.

    `outlying` covers about seven of its 240 rows, so it is withheld at
    the default floor and published at any floor of seven or less. That
    makes it the witness that a lowered floor really lowers something.
    """
    folder.mkdir(parents=True, exist_ok=True)
    return fixtures.write(folder, "clinic.csv", fixtures.every_role_table())


def _described(folder: pathlib.Path, floor: int) -> pathlib.Path:
    """Describe the table at ``floor`` with the real producer."""
    table_path = _table(folder)
    table = reading.read_table(f"{table_path}")
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), []
    )
    return fixtures.write_profile(folder, "clinic-profile.json", document)


def _levels_of(document: dict, column: str) -> dict:
    """One column's published labels, as label -> count."""
    for block in document["columns"]:
        if block["name"] == column:
            return {
                entry["label"]: entry["count"] for entry in block["levels"]
            }
    raise AssertionError(f"no column called {column!r}")


# -- 1. the workflow runs ---------------------------------------------


@pytest.mark.parametrize("floor", _LOWERED)
def test_profile_generate_and_validate_all_run_at_a_lowered_floor(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str], floor: int
) -> None:
    """The whole chain, through the real commands, at a floor under 11.

    This is the defect stated as a test. Before the ruling the first
    command exited 0 and the second exited 1 with a refusal that told
    the person to do what they had just done.
    """
    table = _table(tmp_path)
    assert main(
        ["profile", f"{table}", "--smallest-group", f"{floor}"]
    ) == 0, "profile refused a floor it accepted before the twin existed"
    capsys.readouterr()

    description = tmp_path / "clinic-profile.json"
    assert main(["generate", f"{description}"]) == 0, (
        "generate refused the description profile had just written -- "
        "which is the whole defect amendment A-P3-11 closes"
    )
    capsys.readouterr()

    assert main(["validate", f"{description}"]) == 0, (
        "validate refused the description, or the twin missed an "
        "obligation, at a lowered floor"
    )
    capsys.readouterr()

    for name in (
        "clinic-profile.json",
        "clinic-profile.txt",
        "clinic-twin.csv",
        "clinic-twin-report.txt",
        "clinic-twin-quality.txt",
    ):
        assert (tmp_path / name).exists(), f"{name} was not written"


@pytest.mark.parametrize("floor", _LOWERED)
def test_a_lowered_floor_really_publishes_the_small_group(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The number changes what is published, not just what is accepted.

    Without this, a build that took the flag and then used eleven
    anyway would pass every other test in this file.
    """
    strict = json.loads(
        _described(tmp_path / "strict", _DEFAULT).read_text(encoding="utf-8")
    )
    loose = json.loads(
        _described(tmp_path / "loose", floor).read_text(encoding="utf-8")
    )
    assert "outlying" not in _levels_of(strict, "region"), (
        "the rare label is published at the DEFAULT floor, so this table "
        "no longer witnesses anything"
    )
    published = _levels_of(loose, "region")
    assert "outlying" in published, (
        f"a floor of {floor} did not publish the rare label, so the "
        "option changed nothing"
    )
    assert published["outlying"] < _DEFAULT, (
        "the published count is not below the default floor, so nothing "
        "the floor was protecting has actually been given up here"
    )
    assert loose["settings"]["small_cell_floor"] == floor


def test_at_a_floor_of_one_nothing_is_held_back_at_all(
    tmp_path: pathlib.Path,
) -> None:
    """The boundary case, asserted rather than assumed.

    Every floor-governed rule of the contract is written as "at least
    the floor" and "below the floor". At one the second half is the
    EMPTY range, so a producer that still pooled something would be
    writing a document its own loader must refuse.
    """
    document = json.loads(
        _described(tmp_path, 1).read_text(encoding="utf-8")
    )
    for block in document["columns"]:
        where = block["name"]
        assert block.get("suppressed_levels", 0) == 0, where
        assert block.get("suppressed_level_counts", []) == [], where
        assert block.get("suppressed_rows", 0) == 0, where
        for entry in block.get("levels", []):
            assert entry["variants_withheld"] == {}, where
        assert taxonomy.SUPPRESSED_LABEL not in block.get(
            "numeric_styles", {}
        ), where


# -- 2. the strict loader is still strict -----------------------------


def test_a_floor_of_zero_is_still_refused(tmp_path: pathlib.Path) -> None:
    """One is the smallest workable floor; zero is not a floor at all.

    "Below the floor" at zero would name counts of nothing at all, and
    no count is. The command refuses it before the table is opened and
    the loader refuses it in a document.
    """
    table = _table(tmp_path)
    assert main(["profile", f"{table}", "--smallest-group", "0"]) == 2

    document = json.loads(
        _described(tmp_path, 1).read_text(encoding="utf-8")
    )
    document["settings"]["small_cell_floor"] = 0
    broken = fixtures.write_profile(tmp_path, "zero-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{broken}")
    assert "small_cell_floor" in f"{refused.value}"


def test_a_description_that_holds_something_back_at_one_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The invariant still binds, and the refusal reads as a sentence.

    The permitted key range of a held-back map is `1 .. floor - 1`, so
    at a floor of one it is empty. The loader composed that as "a number
    of rows from 1 to 0", which sends a person looking for a number that
    cannot exist; it now says the block is empty and why.
    """
    document = json.loads(
        _described(tmp_path, 1).read_text(encoding="utf-8")
    )
    touched = ""
    for block in document["columns"]:
        for entry in block.get("levels", []):
            entry["variants_withheld"] = {"1": 1}
            touched = block["name"]
            break
        if touched:
            break
    assert touched, "no published label to hang a held-back spelling on"
    broken = fixtures.write_profile(tmp_path, "held-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{broken}")
    said = f"{refused.value}"
    assert "variants_withheld" in said
    assert "from 1 to 0" not in said, (
        "the refusal is asking for a number that cannot exist"
    )
    assert "empty" in said, (
        "the refusal does not say what the person is supposed to do"
    )


def test_a_lowered_floor_description_is_refused_for_everything_else(
    tmp_path: pathlib.Path,
) -> None:
    """Lowering the floor is not a way past the rest of the loader."""
    document = json.loads(
        _described(tmp_path, 2).read_text(encoding="utf-8")
    )
    document["columns"][0]["n_present"] = document["n_rows"] + 1
    broken = fixtures.write_profile(tmp_path, "bad-profile.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(f"{broken}")


def test_the_two_defaults_cannot_drift(tmp_path: pathlib.Path) -> None:
    """The reports compare against the producer's own default.

    `contract.DEFAULT_SMALL_CELL_FLOOR` exists because the generation
    and validation paths may not import the profiler's taxonomy. Two
    modules holding one number is the arrangement; this is the
    comparison that keeps it honest.
    """
    assert contract.DEFAULT_SMALL_CELL_FLOOR == _DEFAULT


# -- 3. the cost is visible, one file at a time -----------------------

# WHAT EACH WRITTEN PAGE OWES, in substrings a person would read. Not
# "the floor was lowered" -- that is a fact about a setting. What a
# reader is owed is what a group that small can mean for a person, and
# where the counts go next.
_OWED = (
    "one person",
    "twin",
)


def _summary_at(folder: pathlib.Path, floor: int) -> str:
    from synthtwin import summary

    document = json.loads(
        _described(folder, floor).read_text(encoding="utf-8")
    )
    return summary.render(document, "")


def _report_at(folder: pathlib.Path, floor: int) -> str:
    loaded = contract.load_profile(f"{_described(folder, floor)}")
    return rendering.report(loaded, generation.generate(loaded, 7))


def _quality_at(folder: pathlib.Path, floor: int) -> str:
    described = _described(folder, floor)
    loaded = contract.load_profile(f"{described}")
    twin = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(generation.generate(loaded, 7))
    )
    return quality.quality_report(loaded, validation.measure(loaded, f"{twin}"))


_PAGES = (
    ("the plain-language summary", _summary_at),
    ("the generation report", _report_at),
    ("the quality report", _quality_at),
)


@pytest.mark.parametrize("floor", _LOWERED)
@pytest.mark.parametrize("what,page", _PAGES, ids=[one[0] for one in _PAGES])
def test_each_written_page_says_it_on_its_own_face(
    tmp_path: pathlib.Path, floor: int, what: str, page: object
) -> None:
    """One file, read alone, tells its reader the floor was lowered.

    This is the same reasoning that put the handling rule on all five
    files (amendment A-P3-8 clause 2): a person is handed ONE of these,
    and the floor lives in the description's JSON as a number a
    non-programmer does not open. So each page is asserted separately,
    with no reference to the others.
    """
    assert callable(page)
    text = page(tmp_path, floor)
    assert f"LOWERED TO {floor}" in text or (
        f"LOWERED FOR THIS PROFILE, TO {floor}" in text
    ), f"{what} does not say the floor was lowered, or does not say to what"
    assert f"{_DEFAULT}" in text, (
        f"{what} does not name the number it was lowered FROM, so a "
        "reader cannot tell how far"
    )
    for owed in _OWED:
        assert owed in text, (
            f"{what} no longer says {owed!r}. Saying the floor was "
            "lowered without saying what that means for a person is the "
            "wording the ruling replaced"
        )
    if floor < 2:
        assert "single row" in text or "one person on their own" in text, (
            f"{what} does not say that a group of one is one person"
        )


@pytest.mark.parametrize("what,page", _PAGES, ids=[one[0] for one in _PAGES])
def test_no_written_page_says_it_on_an_ordinary_run(
    tmp_path: pathlib.Path, what: str, page: object
) -> None:
    """And it is silent at the default floor, which is the point.

    A paragraph printed on every run to say the floor was NOT lowered is
    how a reader is trained to skip the paragraph that matters. It is
    also what keeps the golden digests of an ordinary run still.
    """
    assert callable(page)
    text = page(tmp_path, _DEFAULT)
    assert "LOWERED TO" not in text, (
        f"{what} carries the lowered-floor section on a description made "
        "at the default floor"
    )
    assert "LOWERED FOR THIS PROFILE" not in text


def test_the_quality_report_names_the_floor_it_ran_at_on_every_run(
    tmp_path: pathlib.Path,
) -> None:
    """Unconditional, unlike the section above, and for a stated reason.

    The withholding rule used to read "never named in any description",
    which was true when every description had one floor. It is not one
    number now, so a reader supplies eleven and is wrong about what the
    lines above are showing them. This is the only sentence of an
    ordinary report that amendment A-P3-11 moves.
    """
    ordinary = _quality_at(tmp_path / "ordinary", _DEFAULT)
    lowered = _quality_at(tmp_path / "lowered", 2)
    assert f"publication floor of this description is {_DEFAULT}" in ordinary
    assert "publication floor of this description is 2" in lowered
    assert "never named in any description" not in ordinary, (
        "the sentence that invites a reader to supply eleven is back"
    )
    # A floor of one makes the general sentence absurd -- "a group fewer
    # than 1 rows carry is named in no description" -- so it does not get
    # the general sentence. What a reader of that report needs is that
    # nothing is held back this way at all.
    at_one = _quality_at(tmp_path / "one", 1)
    assert "publication floor is 1, so nothing is" in at_one
    assert "fewer than 1 rows carry" not in at_one, (
        "the report is asking the reader to picture a group of fewer "
        "than one row"
    )


def test_the_profile_command_warns_before_either_file_exists(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The warning is on the screen while there is still nothing to move.

    The ordering is the control P1-D6 fixes for the disclosure itself: a
    person who reads the warning and stops has written nothing. It is
    asserted by making the warning the thing that STOPS the run, which
    is the only way a test can see the order from outside.
    """
    table = _table(tmp_path)
    seen: list[str] = []

    real = profile.write_both_files

    def refuse(*arguments: object, **named: object) -> object:
        seen.append("wrote")
        raise KeyboardInterrupt

    profile.write_both_files = refuse  # type: ignore[assignment]
    try:
        with pytest.raises(KeyboardInterrupt):
            main(["profile", f"{table}", "--smallest-group", "2"])
    finally:
        profile.write_both_files = real  # type: ignore[assignment]

    assert seen == ["wrote"], "the run never reached the write at all"
    said = capsys.readouterr().err
    assert "one person" in said, (
        "the warning had not been printed by the time the first byte "
        "would have been written"
    )
