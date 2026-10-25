"""P4-D432 (lane ID-ROOM): no twin identifier cell equals a real identifier of its column, by construction.

WHAT WAS MEASURED (lane CODES-3's verify 3, wave6/CODES-3-verify3.md finding 1 and NEW SHAPES;
re-measured by lane ID-ROOM on CODES-3's final head 2d25b073 with wave6/ID-ROOM/idprobe.py and
zooprobe.py, logs base-*.log there). A declared or answered identifier's twin drew its free figures
and arcs in its column's own layouts and read no real value, so where the real values fill a layout
densely a twin cell EQUALLED a real identifier by chance. At 20,000 rows: `1.2.752.24.7.1.<k>` wrote
1,022 real UIDs (38 of 600 rows), `1.2.840.113619.2.40.10.12.<k>` 123, `1.2.276.0.7.1.2.<k>` 110,
Siemens' root and `1.2.<k>` 110, GE's root and `1.2.3.<k>` 11, `1.2.<k>` 2,222; Cerner record numbers
of three widths 214, of two widths 348, one place 214; record numbers `1` to `20,000` 11,110, a
person on twenty rows 19,980, zero-filled 2,225, `100000.0` exported 400, random seven figures 50;
`P` and five figures 4,000, `ABC-` and four 18,000, two systems 93; rsIDs 15, beside `.` 4,011; held
keys beside `N/A` 4,000; and the zoo's own identifier columns 328 cells at 600 rows (its REDCap
record ids 318). The count grows with the rows.

THE RULE (contract 7.12b, method G9.6b). The profile, which reads the real column, publishes beside
each named layout an EXCLUSION -- the layout with one place (or every other figure place of a block)
written as a character NO real cell of that layout holds there -- and the SPILL, a layout longer
than every real cell. The twin writes each excluded layout's cells with the exclusion, and every
other value nearest its own shape where no real cell can be: its layout's excluded template, the
named layout its own widens to, its own layout widened past the spill's length, the spill. Two
equal cells wear one layout and hold one character at every place, so no twin cell is spelled as a
real one. The exclusion publishes what the column does NOT hold: no value, no extreme of one, no
count below the floor (a character the choice passes over is held by the floor's cells or more).

Each case runs the product's command line, nobody at the keyboard, and each is red on the mutant its
docstring names (wave6/ID-ROOM/mutants.log).
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from synthtwin import contract, parsing, taxonomy

import identifier_room_shapes as room

SIZES = (600, 20_000)
FLOOR = 11
UID = re.compile(r"[012](\.(0|[1-9]\d*))+")


def _real_by_layout(real: "list[str]") -> "dict[str, list[str]]":
    present = [cell for cell in real if cell.strip()]
    convention = parsing.layout_convention(present)
    by: "dict[str, list[str]]" = {}
    for cell in present:
        by.setdefault(parsing.layout_form(cell, convention), []).append(cell)
    return by


# -- the gate: no twin cell spelled as a real one ---------------------------------------------


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("name", room.every_shape())
def test_no_twin_identifier_cell_equals_a_real_one(tmp_path: pathlib.Path, name: str, n: int) -> None:
    """Every shape at 600 and 20,000 rows: 0 twin cells spelled as a real cell of their column.

    Mutants: the exclusions dropped (`with_layout_exclusions` returning its column), the twin's final
    pass leaving its first moved value where it was, and an exclusion written with a character a real
    cell holds -- each turns a dense shape red.
    """
    seen = room.run_shape(tmp_path, name, n, validate=False)
    if n == 600 and name in room.REFUSED_AT_600:
        assert seen["exits"][0] == 1 and not seen["twin"], (name, seen["exits"])
        return
    assert seen["exits"][:2] == (0, 0), (name, n, seen["exits"])
    assert seen["equal"] == 0, (name, n, seen["equal"])
    if seen["block"].get("role") == "identifier" and seen["block"].get("layout_forms"):
        assert seen["block"]["layout_exclusions"], (name, n)


@pytest.mark.parametrize(
    ("name", "n"), [(name, n) for name, sizes in room.ANSWERED for n in sizes]
)
def test_an_answered_identifier_writes_no_real_one(tmp_path: pathlib.Path, name: str, n: int) -> None:
    """The held shapes answered `identifier` (a person column): 0 twin cells equal to a real one."""
    seen = room.run_shape(tmp_path, name, n, answer="identifier", validate=False)
    assert seen["exits"][:2] == (0, 0), (name, n, seen["exits"])
    assert seen["equal"] == 0, (name, n, seen["equal"])


# -- the fact's own privacy -------------------------------------------------------------------


@pytest.mark.parametrize("name", room.every_shape())
def test_the_exclusion_publishes_what_no_real_cell_holds(tmp_path: pathlib.Path, name: str) -> None:
    """Every written character is held by no real cell of its layout; the spill outlasts every cell.

    At 600 rows. Also: every character the one-place choice passed over at its place is held by at
    least the floor's cells, so no count of 1 to 10 is read off the choice; no exclusion holds a run
    of five written characters (a fragment some value could hold). Mutants: the choice passing over
    a character fewer than the floor's cells hold (the scan's stop removed), and the spill no longer
    than the longest real cell.
    """
    seen = room.run_shape(tmp_path, name, 600, validate=False)
    block = seen["block"]
    exclusions = block.get("layout_exclusions") or {}
    if name in room.REFUSED_AT_600:
        assert not block, name
        return
    by = _real_by_layout(seen["real"])
    longest = max(len(cell) for cell in seen["real"] if cell.strip())
    prefixes = block.get("layout_prefixes") or {}
    for scope, text in sorted(exclusions.items()):
        if scope == parsing.EXCLUSION_SPILL:
            assert len(text) > longest, (name, text)
            continue
        written = [place for place in range(len(text)) if text[place] != scope[place]]
        assert written, (name, scope)
        for cell in by.get(scope, []):
            assert any(cell[place] != text[place] for place in written), (name, scope)
        assert not re.search(r"[0-9A-Za-z]{5}", "".join(
            text[place] if place in written else "%" for place in range(len(text)))), (name, text)
        if len(written) == 1:
            place = written[0]
            held: "dict[str, int]" = {}
            for cell in by.get(scope, []):
                held[cell[place]] = held.get(cell[place], 0) + 1
            alphabet = parsing.exclusion_alphabet(scope[place])
            for character in reversed(alphabet):
                if character == text[place]:
                    break
                if character == "0" and (place == 0 or scope[place - 1] in ".-+!"):
                    continue
                assert held.get(character, 0) >= FLOOR, (name, scope, character)
        prefix = prefixes.get(scope, prefixes.get(parsing.PREFIX_OF_THE_COLUMN, ""))
        opening = len(parsing.prefix_layout(prefix, parsing.layout_convention(
            [cell for cell in seen["real"] if cell.strip()]))) if prefix else 0
        assert all(place >= opening for place in written), (name, scope)


def test_no_real_value_reaches_the_description_through_an_exclusion(tmp_path: pathlib.Path) -> None:
    """The densest shapes' exclusions carry no real value whole, at 600 rows."""
    for name in ("uid_752", "sequential_from_one", "cerner_three_widths", "rsid", "keys_beside_na"):
        seen = room.run_shape(tmp_path / name, name, 600, validate=False)
        published = json.dumps(seen["block"].get("layout_exclusions") or {})
        for value in {cell for cell in seen["real"] if cell.strip()}:
            assert f'"{value}"' not in published, (name, value)


# -- code runs unchanged: the grammar, the length, the prefix, the noughts, the join ------------


UID_SHAPES = tuple(name for name in room.SHAPES if name.startswith("uid_")) + ("codes3_pacs_study_uid",)


@pytest.mark.parametrize("name", UID_SHAPES)
def test_a_uid_twin_keeps_the_grammar_the_length_and_the_root(tmp_path: pathlib.Path, name: str) -> None:
    """Every twin UID matches `[012](\\.(0|[1-9]\\d*))+`, is at most 64 characters, opens with the root.

    At 20,000 rows. Mutant: the UID root's opening read only to the first placeholder (an exclusion's
    figure after the root then switches the grammar's test off, and arcs are led by noughts).
    """
    seen = room.run_shape(tmp_path, name, 20_000, validate=False)
    root = (seen["block"].get("layout_prefixes") or {}).get(parsing.PREFIX_OF_THE_COLUMN, "")
    for cell in seen["twin"]:
        if not cell.strip():
            continue
        assert UID.fullmatch(cell) is not None and len(cell) <= 64, (name, cell)
        assert cell.startswith(root), (name, cell, root)


PREFIXED = ("pt_seven_sequential", "pt_seven_person_on_three_rows", "e_nine_sequential", "p_five",
            "mrn_eight_random", "abc_dash_four", "rsid", "codes3_vcf_rsid")


@pytest.mark.parametrize("name", PREFIXED)
def test_a_prefixed_twin_opens_with_its_prefix(tmp_path: pathlib.Path, name: str) -> None:
    """Every twin cell of a column publishing a `(column)` prefix opens with it, at 20,000 rows."""
    seen = room.run_shape(tmp_path, name, 20_000, validate=False)
    prefix = (seen["block"].get("layout_prefixes") or {}).get(parsing.PREFIX_OF_THE_COLUMN, "")
    assert prefix, name
    assert all(cell.startswith(prefix) for cell in seen["twin"] if cell.strip()), name


@pytest.mark.parametrize("name", ("cerner_one_width", "cerner_three_widths", "cerner_two_widths",
                                  "cerner_person_on_three_rows", "codes3_cerner_encounter"))
def test_a_whole_record_number_keeps_its_noughts(tmp_path: pathlib.Path, name: str) -> None:
    """A record number exported as `31000000.00` writes `.00` on every twin cell, at 20,000 rows."""
    seen = room.run_shape(tmp_path, name, 20_000, validate=False)
    assert all(re.fullmatch(r"[1-9]\d*\.00", cell) for cell in seen["twin"] if cell.strip()), name


def test_an_npi_twin_keeps_its_ten_figures(tmp_path: pathlib.Path) -> None:
    """NPI-like numbers keep ten figures; the description publishes no check-digit fact.

    The product publishes no check digit for any column, so the twin's Luhn digits were never the
    table's; the exclusion writes its one figure at the first place and changes nothing else.
    """
    seen = room.run_shape(tmp_path, "npi_check_digit", 20_000, validate=False)
    assert all(re.fullmatch(r"[1-9]\d{9}", cell) for cell in seen["twin"]), "npi"
    assert seen["block"]["layout_exclusions"].get("%%%%%%%%%%", "").count("%") == 9


PEOPLE = ("sequential_person_on_three_rows", "sequential_person_on_twenty_rows",
          "pt_seven_person_on_three_rows", "cerner_person_on_three_rows",
          "zero_filled_person_on_four_rows", "uid_study_on_ten_rows", "uid_pydicom_repeated")


@pytest.mark.parametrize("name", PEOPLE)
def test_a_repeated_key_stays_one_key_on_its_rows(tmp_path: pathlib.Path, name: str) -> None:
    """The join: the twin's census of rows a value equals the published one, at 20,000 rows.

    A value is moved whole (the twin person's rows keep one key). Mutant: the final pass writing a
    fresh spelling on every ROW of a moved value instead of one a value.
    """
    seen = room.run_shape(tmp_path, name, 20_000, validate=False)
    counts: "dict[str, int]" = {}
    for cell in seen["twin"]:
        if cell.strip():
            counts[cell] = counts.get(cell, 0) + 1
    census: "dict[int, int]" = {}
    for rows in counts.values():
        census[rows] = census.get(rows, 0) + 1
    published = {int(key): value for key, value in seen["block"]["n_distinct_by_occurrences"].items()}
    assert census == published, name


# -- the bytes move only in identifier columns ---------------------------------------------------


def test_the_exclusion_is_the_only_key_the_description_gains(tmp_path: pathlib.Path, monkeypatch) -> None:
    """With the exclusions withdrawn, the description and every other column of the twin are the same.

    At 600 rows on a dense shape: the description read with `layout_exclusions` set aside is byte for
    byte the one written without it, and the twin's other two columns are cell for cell the same --
    so the landing moves bytes in identifier columns only.
    """
    seen = room.run_shape(tmp_path / "with", "cerner_three_widths", 600, validate=False)
    monkeypatch.setattr(taxonomy, "with_layout_exclusions", lambda column, cells, floor: column)
    without = room.run_shape(tmp_path / "without", "cerner_three_widths", 600, validate=False)
    first = json.loads(seen["texts"]["t-profile.json"])
    second = json.loads(without["texts"]["t-profile.json"])
    for document in (first, second):
        for block in document["columns"]:
            block.pop("layout_exclusions", None)
    assert first == second
    twin_one = (tmp_path / "with" / "t-twin.csv").read_text(encoding="utf-8").splitlines()
    twin_two = (tmp_path / "without" / "t-twin.csv").read_text(encoding="utf-8").splitlines()
    assert [row.split(",")[1:] for row in twin_one] == [row.split(",")[1:] for row in twin_two]


# -- the pieces -----------------------------------------------------------------------------------


def test_an_exclusion_is_its_layout_with_places_written_out() -> None:
    """`parsing.excludes_the_layout`, `written_excluded`, `spill_layout` and the loader's LX rules."""
    assert parsing.excludes_the_layout("%%%%", "9%%%")
    assert parsing.excludes_the_layout("-%", "-9")
    assert not parsing.excludes_the_layout("%%%%", "A%%%")
    assert not parsing.excludes_the_layout("%%%%", "%%%%")
    assert not parsing.excludes_the_layout("!%%%", "9%%%")
    assert parsing.written_excluded("REC%%%%", "@@@9%%%") == "REC9%%%"
    assert parsing.written_excluded("%%%%.00", "9%%%.%%") == "9%%%.00"
    assert parsing.spill_layout("%%%%", 0, 5) == "%%%%%%"
    assert parsing.spill_layout("@%%%%", 1, 5) == "@%%%%%"
    assert parsing.spill_layout("%.%.%%", 4, 6) == "%.%.%%%"
    assert parsing.spill_layout("@&&&", 0, 4) == "@@&&&"
    assert parsing.spill_layout("%" * 64, 0, 64) == ""
    assert not parsing.is_a_layout_exclusion("%%%%")
    assert parsing.is_a_layout_exclusion("-9")


def test_the_loader_refuses_an_exclusion_that_does_not_fit_its_layout(tmp_path: pathlib.Path) -> None:
    """LX2 for a written place inside the prefix; LX3 for a spill no longer than the longest value."""
    seen = room.run_shape(tmp_path / "made", "pt_seven_sequential", 600, validate=False)
    document = json.loads(seen["texts"]["t-profile.json"])
    block = [one for one in document["columns"] if one["name"] == "target"][0]
    for exclusions, rule in (({"@@%%%%%%%": "Z@%%%%%%%"}, "LX2"),
                             ({"(spill)": "@@%%%%%%%"}, "LX3")):
        block["layout_exclusions"] = exclusions
        path = tmp_path / f"{rule}.json"
        path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
        with pytest.raises(Exception) as refused:
            contract.load_profile(str(path))
        assert rule in str(refused.value)
