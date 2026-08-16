"""A published field that crossed the display boundary is not exact.

REVIEW ITEM P3-V7-F1, and plan amendment A-P3-19. Round 6 recovered the
person's `--missing-value` spellings from a column's `missing_by_source`
and called them "the exact spelling". They are not: the profile contract
says in terms that this map's keys pass through the DISPLAY BOUNDARY
that escapes line, control and bidirectional formatting characters, and
that `variants` deliberately does not, because a variant is written back
into a cell and a missing source is only ever read.

WHAT THAT COSTS, MEASURED HERE, IN BOTH DIRECTIONS. Seventy-two rows
whose holes are spelled `X`, U+0001, `Y` publish the key `X\\x01Y`. So do
seventy-two rows whose holes are spelled with those six PRINTABLE
characters. The two whole descriptions come out byte for byte alike, so
no reading of a description can tell the two apart -- and reading the
key as exact did both wrong things at once:

* the control-character table validated against its OWN profile
  reported seven obligations MISSED, which is the direction the review
  named;
* and a file spelled the printable way, validated against the
  control-character table's profile, came back with a census of ZERO
  MISSED and exit 0 -- although `synthtwin profile` under that
  description's own declaration reads that file as free text with 72
  present and 0 missing. That is a passing report on a file the
  description's own settings reject, and it is the direction the review
  did not name.

WHY THE WIDER MATCH IS NOT THE REPAIR, since it is the obvious one.
Matching a cell as a hole when its DISPLAYED form equals the key passes
both tables above -- and it is exactly what manufactures the false pass:
it reads the printable cells of the other file as holes and re-describes
that file as the one the description asks for. A rule that passes the
first passes the second, which is V2.4-A4 clause 3's own reasoning about
the kept-`n/a` gap, applied to the other declaration.

SO THE REPAIR IS THE NARROW ONE, and what it leaves open is stated at
its size. A key is recovered only where the boundary provably left it
alone -- `parsing.shows_only_itself`, decidable from the key, proved in
its own docstring. Round 6's measured gains survive untouched, because
`XX` and `-777` hold no character the boundary shows. A declaration that
DOES hold one is not recovered at all, so the table it was written from
reads those cells back as data, exactly as it did before round 6 -- and
the false pass is gone, which is the trade amendment A-P3-19 states.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import os
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

# The two spellings of one published key. `RAW` holds a real control
# character; `SHOWN` holds the six printable characters the boundary
# writes that control character as. `parsing.visible` maps both to
# `SHOWN`, and that is the whole finding.
RAW = "X\x01Y"
SHOWN = "X\\x01Y"

# The seven obligations the class costs, named rather than counted, so
# that a change to which ones move is a change somebody chose.
_SEVEN = (
    "presence.n_present",
    "presence.n_missing",
    "axes.role",
    "axes.statistical_type",
    "counts.n_not_numeric",
    "distinct.n_distinct",
    "distinct.n_distinct_folded",
)


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put round 6's unrestricted recovery back on request.

    MODULE-SCOPED, for the reason the corner-parity battery gives: the
    descriptions and reports this file compares are built in a
    module-scoped fixture, and a function-scoped `monkeypatch` would be
    applied after they were built -- a red check run against a patch
    nobody used.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V7-F1":
        monkeypatch.setattr(parsing, "shows_only_itself", lambda _text: True)
    if asked == "A-P3-26":
        # The other half of this file's red check: with no column ever
        # unrebuildable, the seven obligations are misses again and
        # every assertion below that says otherwise goes red.
        monkeypatch.setattr(
            validation, "unrebuildable_columns", lambda _described: {}
        )
    yield
    monkeypatch.undo()


def _table(marker: str) -> str:
    """Seventy-two rows: sixty numbers and twelve cells wearing ``marker``."""
    return fixtures.rows_to_csv(
        ["record_code", "reading"],
        [
            [
                f"R{index:05d}",
                marker if index % 6 == 0 else f"{1.0 + index * 0.25}",
            ]
            for index in range(72)
        ],
    )


def _document(folder: pathlib.Path, marker: str, stem: str) -> dict:
    """One table through the real producer, declared missing by ``marker``."""
    path = fixtures.write(folder, f"{stem}.csv", _table(marker))
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(
        table, taxonomy.Settings(declared_missing_values=(marker,)), []
    )


def _loaded(
    folder: pathlib.Path, document: dict, stem: str
) -> contract.Profile:
    """One document through the strict loader."""
    return contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )


class World(typing.NamedTuple):
    """One of the two indistinguishable worlds, built end to end."""

    marker: str
    document: dict
    described: contract.Profile
    path: str


@pytest.fixture(scope="module")
def worlds(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[World, World, pathlib.Path]":
    """Both tables, both descriptions, and the folder they live in."""
    folder = tmp_path_factory.mktemp("escaped-declarations")
    built: list[World] = []
    for stem, marker in (("raw", RAW), ("shown", SHOWN)):
        document = _document(folder, marker, stem)
        described = _loaded(folder, document, stem)
        built = built + [
            (
                World(
                    marker,
                    document,
                    described,
                    str(fixtures.write(folder, f"{stem}.csv", _table(marker))),
                )
            )
        ]
    return (built[0], built[1], folder)


def _verdicts(outcome: validation.Outcome) -> "dict[str, str]":
    """Every subcheck of one run and the verdict it came back with."""
    return {check.subcheck: check.verdict for check in outcome.checks}


def _missed(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run reported MISSED, sorted."""
    return sorted(
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    )


# -- what the format does, and what it therefore cannot carry ----------


def test_the_display_boundary_maps_two_spellings_onto_one_key() -> None:
    """The escape is not reversible, which is where the class begins."""
    assert parsing.visible(RAW) == SHOWN
    assert parsing.visible(SHOWN) == SHOWN
    assert RAW != SHOWN


def test_the_two_descriptions_are_byte_for_byte_alike(
    worlds: "tuple[World, World, pathlib.Path]",
) -> None:
    """No reading of a description can tell the two tables apart.

    This is what makes the class unclosable inside the validator under
    the current format, and it is asserted rather than argued: if the
    contract ever published the exact spelling somewhere, these bytes
    would differ and this test is what says so.
    """
    raw, shown, _folder = worlds
    assert canonical.serialize(raw.document) == canonical.serialize(
        shown.document
    )
    assert raw.described.columns[1].missing_by_source == {SHOWN: 12}
    assert shown.described.columns[1].missing_by_source == {SHOWN: 12}
    assert raw.described.columns[1].n_present == 60
    assert raw.described.columns[1].n_missing == 12


# -- the direction the review named ------------------------------------


def test_the_escaped_declaration_is_not_recovered(
    worlds: "tuple[World, World, pathlib.Path]",
) -> None:
    """The key crossed the boundary, so it is not read back as a spelling."""
    raw, shown, _folder = worlds
    assert validation.declared_spellings(raw.described) == ()
    assert validation.declared_spellings(shown.described) == ()
    settings = validation.settings_for(raw.described)
    assert settings.declared_missing_values == ()


def _unsupported(outcome: validation.Outcome) -> "list[str]":
    """The subchecks one run named as ones this description cannot ask."""
    return sorted(
        {
            listing.subcheck
            for listing in outcome.listings
            if listing.reason.endswith(validation.UNREBUILDABLE_REASON_TAIL)
        }
    )


def test_the_residual_is_exactly_the_seven_this_file_names(
    worlds: "tuple[World, World, pathlib.Path]",
) -> None:
    """What the narrow rule leaves open, measured instead of promised.

    A table whose declared holes are spelled with a character the
    boundary shows cannot be read back the way its own description was
    written. That is the cost amendment A-P3-19 records, and it is
    pinned here at its size so that a change to it is visible.

    IT IS SEVEN NOT-CHECKABLE LINES NOW, AND IT WAS SEVEN MISSES (owner
    ruling 2026-08-16, plan amendment A-P3-26). The residual is the same
    residual -- the spelling is exactly as unrecoverable as it was --
    and the same seven obligations are the ones it reaches. What changed
    is that a table which is its own description's perfect match is no
    longer told it failed seven obligations; the report says instead
    that this description does not record what measuring them needs.
    """
    raw, shown, _folder = worlds
    for world in (raw, shown):
        outcome = validation.measure(world.described, world.path)
        assert _missed(outcome) == [], world.marker
        assert outcome.census.missed == 0, world.marker
        for subcheck in _SEVEN:
            assert subcheck in _unsupported(outcome), (
                f"{world.marker}: {subcheck} is neither checked nor "
                f"named as unsupported, so the residual amendments "
                f"A-P3-19 and A-P3-26 state has changed size"
            )


def test_the_two_worlds_now_get_the_same_report(
    worlds: "tuple[World, World, pathlib.Path]",
) -> None:
    """Two descriptions nothing can tell apart give two files one answer.

    V5.1's shape, applied to the pair the format cannot separate: the
    tables differ only in a spelling the description does not carry, so
    a rule that treats them differently is a rule reading something the
    description does not publish.
    """
    raw, shown, _folder = worlds
    first = _verdicts(validation.measure(raw.described, raw.path))
    second = _verdicts(validation.measure(shown.described, shown.path))
    assert first == second


# -- the direction the review did not name: the passing report ---------


def test_a_file_the_declaration_rejects_is_no_longer_reported_on(
    worlds: "tuple[World, World, pathlib.Path]",
) -> None:
    """THE FALSE PASS, AND THE LOWERING THAT REPLACED THE ALARM.

    The description was written from the control-character table under
    the declaration that table's holes wear. The OTHER file wears the
    printable spelling, which that declaration does not name, so
    `synthtwin profile` under those settings describes it as free text
    with 72 present cells and no holes -- a file the description does
    not fit. Round 6's recovery read the published key as the printable
    spelling, re-described the file as the one the description asks for,
    and reported no miss at all: a passing report on a file the
    description's own settings reject.

    AMENDMENT A-P3-19 REPLACED THAT WITH SEVEN MISSES. IT IS SEVEN
    NOT-CHECKABLE LINES NOW, AND THIS IS THE ONE PLACE WHERE THAT IS A
    LOWERING (owner ruling 2026-08-16, plan amendment A-P3-26, and the
    first of the two risks the ruling was taken against). This run is
    the SAME construction as the two runs above -- one description, two
    files it cannot tell apart -- and V5.1 forbids a report that tells
    them apart. So the file that conforms and the file that does not
    both come back at exit code 0 with the same seven obligations named
    as ones this description cannot support asking of any file.

    WHAT IS TRUE OF THE REPORT, AND WHAT IS NOT. It no longer says the
    seven obligations were checked and held, which is what round 6's
    false pass said; it says they could not be checked, and why. That is
    the trade: a report that states a limit instead of a verdict it
    cannot support, at the price of a real failure in this corner going
    unremarked. This test asserts BOTH halves, so a change to either is
    a change somebody chose.
    """
    raw, shown, _folder = worlds
    # What the producer says about the other file under the settings the
    # description was actually written under. This is the truth the
    # report can no longer reach.
    table = reading.read_table(
        shown.path, first_row=reading.FIRST_ROW_AUTOMATIC
    )
    truth = profile.build_document(
        table, taxonomy.Settings(declared_missing_values=(RAW,)), []
    )
    column = truth["columns"][1]
    assert column["role"] == "free_text"
    assert column["n_present"] == 72
    assert column["n_missing"] == 0
    assert raw.described.columns[1].role == "continuous"
    outcome = validation.measure(raw.described, shown.path)
    # THE LOWERING, WRITTEN OUT: this file misses nothing now.
    assert outcome.census.missed == 0
    # ...and what replaced the misses is a stated limit, not a silence:
    # each of the seven is named in the not-checkable census with the
    # sentence saying what the description does not record.
    for subcheck in _SEVEN:
        assert subcheck in _unsupported(outcome), subcheck
    # ...and the two files still get one answer, which is why the
    # lowering cannot be repaired by looking at the file.
    conforming = validation.measure(raw.described, raw.path)
    assert _verdicts(conforming) == _verdicts(outcome)
    assert _unsupported(conforming) == _unsupported(outcome)


# -- the rule itself, and that round 6's gains are untouched -----------


def test_a_declaration_the_boundary_leaves_alone_is_still_recovered(
    tmp_path: pathlib.Path,
) -> None:
    """Round 6's two measured witnesses, unchanged by this repair.

    A text marker and a numeric one, each declared, each published as a
    `missing_by_source` key holding nothing the boundary shows. Both are
    recovered, and both tables miss nothing against their own profile --
    which is what amendment A-P3-15 clause 1 bought and what this
    amendment does not spend.
    """
    for stem, marker in (("text", "XX"), ("number", "-777")):
        folder = tmp_path / stem
        folder.mkdir()
        described = _loaded(folder, _document(folder, marker, stem), stem)
        assert validation.declared_spellings(described) == (marker,)
        path = str(fixtures.write(folder, f"{stem}.csv", _table(marker)))
        outcome = validation.measure(described, path)
        assert _missed(outcome) == [], marker
        assert outcome.census.missed == 0, marker


def test_the_recovery_skips_a_key_and_nothing_wider(
    tmp_path: pathlib.Path,
) -> None:
    """One column's escaped key does not silence another column's plain one.

    The exclusion is taken per key. Where one column publishes a key the
    boundary could have altered and another publishes a key it could
    not, the second is still read back; the first is what stays out.
    """
    folder = tmp_path / "mixed"
    folder.mkdir()
    rows = []
    for index in range(72):
        first = RAW if index % 6 == 0 else f"{1.0 + index * 0.25}"
        second = "XX" if index % 6 == 0 else f"{2.0 + index * 0.5}"
        rows = rows + [[f"R{index:05d}", first, second]]
    text = fixtures.rows_to_csv(["record_code", "first", "second"], rows)
    path = fixtures.write(folder, "mixed.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table,
        taxonomy.Settings(declared_missing_values=(RAW, "XX")),
        [],
    )
    described = _loaded(folder, document, "mixed")
    assert described.columns[1].missing_by_source == {SHOWN: 12}
    assert described.columns[2].missing_by_source == {"XX": 12}
    assert validation.declared_spellings(described) == ("XX",)


# -- `shows_only_itself` is the property its docstring claims ----------


def _display_controls() -> "list[int]":
    """One code point out of every range the boundary escapes, and more."""
    found: list[int] = []
    for code in (
        0x00,
        0x01,
        0x09,
        0x0A,
        0x0D,
        0x1F,
        0x7F,
        0x85,
        0x9F,
        0xAD,
        0x061C,
        0x200B,
        0x200E,
        0x2028,
        0x202E,
        0x2066,
        0xFEFF,
        0xFFF9,
        0x110BD,
        0x1D173,
        0xE0001,
    ):
        found = found + [code]
    return found


def test_every_escaped_control_makes_its_key_ambiguous() -> None:
    """A key that could have come out of the boundary is never recovered.

    Walked over one code point from every range the boundary escapes,
    because a range added later must arrive with this property rather
    than inherit a repair nothing checks for it.
    """
    for code in _display_controls():
        shown = parsing.visible(f"A{chr(code)}B")
        assert shown != f"A{chr(code)}B", hex(code)
        assert not parsing.shows_only_itself(shown), hex(code)


def test_a_form_the_boundary_could_not_write_is_not_ambiguous() -> None:
    """The conservative direction is exact, not merely safe.

    `\\x41` is the escape spelling of an ordinary letter and `\\u0001`
    of a character the boundary writes `\\x01`; neither is a form
    `_written_out` produces, so neither makes a key ambiguous. Treating
    them as ambiguous would cost declarations for nothing.
    """
    for spelling in ("\\x41", "\\u0001", "\\U00000001", "\\x0G", "\\x", "\\xZZ"):
        assert parsing.shows_only_itself(spelling), spelling
    for spelling in ("XX", "-777", "n/a-ish", "", "no value", "\\", "\\\\"):
        assert parsing.shows_only_itself(spelling), spelling


def _unescaped_readings(key: str) -> "list[str]":
    """Every text that could have shown as ``key``, by trying each token.

    A brute force over the pre-images: at each position, either the
    boundary wrote an escape there or it did not, and un-writing every
    subset of the escape-shaped tokens enumerates the candidates. Any
    candidate other than ``key`` itself that shows as ``key`` is a
    second reading, and the property under test is that a key
    `shows_only_itself` accepts has none.
    """
    found = [key]
    for start in range(len(key)):
        for width, prefix in ((4, "\\x"), (6, "\\u"), (10, "\\U")):
            piece = key[start : start + width]
            if not piece.startswith(prefix) or len(piece) != width:
                continue
            try:
                code = int(piece[len(prefix) :], 16)
            except ValueError:
                continue
            if code > 0x10FFFF:
                continue
            found = found + [
                key[:start] + chr(code) + key[start + width :]
            ]
    return found


def test_a_key_this_rule_accepts_has_exactly_one_reading() -> None:
    """The proof in arithmetic, over a battery of keys.

    For every candidate spelling below, every text that could have shown
    as it is enumerated and put back through the boundary. Where
    `shows_only_itself` says yes, the key itself is the only text that
    comes out as the key -- which is the claim its docstring makes -- and
    where it says no, some other text does.
    """
    battery = [
        "XX",
        "-777",
        SHOWN,
        RAW,
        "\\x41",
        "\\u0001",
        "a\\x0db",
        "\\x1f",
        "\\u200b",
        "\\U000e0001",
        "\\x2028",
        "no value",
        "\\\\x01",
    ]
    for spelling in battery:
        key = parsing.visible(spelling)
        others = [
            candidate
            for candidate in _unescaped_readings(key)
            if candidate != key and parsing.visible(candidate) == key
        ]
        if parsing.shows_only_itself(key):
            assert others == [], (
                f"{key!r} was accepted as unambiguous and {others!r} "
                f"also shows as it"
            )
        else:
            assert others, (
                f"{key!r} was refused as ambiguous and nothing else "
                f"shows as it, so the rule is costing a declaration for "
                f"no reason"
            )


def test_the_governing_documents_no_longer_call_the_field_exact() -> None:
    """The plan and the method say what the contract says.

    An amendment that claims more than the code does is a defect, and
    this one claimed a field was the exact spelling when its own
    contract says the opposite two documents away. The wording is
    checked here so that restoring it is a red test rather than a quiet
    edit.
    """
    root = pathlib.Path(__file__).resolve().parent.parent
    plan = (root / "docs" / "plans" / "phase-3-product.md").read_text(
        encoding="utf-8"
    )
    method = (
        root / "docs" / "spec" / "validation-method-v1.md"
    ).read_text(encoding="utf-8")
    contract_text = (
        root / "docs" / "spec" / "profile-contract-v4.md"
    ).read_text(encoding="utf-8")
    assert "display boundary" in contract_text
    for document, name in ((plan, "the plan"), (method, "the method")):
        assert "A-P3-19" in document, name
        assert (
            "`missing_by_source` publishes the exact spelling" not in document
        ), name
        assert "carries the exact spelling of every hole" not in document, name
