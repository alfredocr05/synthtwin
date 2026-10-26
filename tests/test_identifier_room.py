"""P4-D432 (lane ID-ROOM): no twin identifier cell names a real identifier of its column, by construction.

WHAT WAS MEASURED (lane CODES-3's verify 3, wave6/CODES-3-verify3.md finding 1 and NEW SHAPES;
re-measured by lane ID-ROOM on CODES-3's final head 2d25b073 with wave6/ID-ROOM/idprobe.py and
zooprobe.py, logs base-*.log there). A declared or answered identifier's twin drew its free figures
and arcs in its column's own layouts and read no real value, so where the real values fill a layout
densely a twin cell EQUALLED a real identifier by chance. At 20,000 rows: `1.2.752.24.7.1.<k>` wrote
1,022 real UIDs (38 of 600 rows), `1.2.840.113619.2.40.10.12.<k>` 123, `1.2.276.0.7.1.2.<k>` 110,
Siemens' root and `1.2.<k>` 110, GE's root and `1.2.3.<k>` 11, `1.2.<k>` 2,222; Cerner record numbers
of three widths 214, of two widths 348, one place 214; record numbers `1` to `20,000` 11,110, a
person on twenty rows 19,980, zero-filled 2,225, `100000.0` exported 400, random seven figures 50;
`P` and five figures 4,000, `ABC-` and four 18,000, two systems 93; rsIDs 15, beside `.` 11 (its
absent `.` aside); and the zoo's own identifier columns 328 cells at 600 rows (its REDCap
record ids 318). The count grows with the rows.

AND WHAT THE LANE'S FIRST HEAD LEFT (skeptic 1, wave6/ID-ROOM-sk1.md, and Codex's review): one stray
cell that emptied the census turned the rule off (598 of 600 real record numbers written back); a
nought written after a prefix (`P0013736` beside a real `P13736`) and one number written two ways
(`9297784` beside a real `009297784`) named a real person as the product's own merged key reads one
(P4-D406); every rootless UID opened `9.`; dense layouts failed the twin's validation; the spill
printed one outlier's length; identifiers past sixty-four characters wrote real values or stopped.

THE RULE (contract 7.12b, method G9.6b). The profile, which reads the real column, publishes beside
each named layout an EXCLUSION -- the layout with one place (or every other place of a block)
written as a character NO real cell's MERGED KEY holds where that place stands in it -- and, beside
every identifier block, the SPILL: the column's prefix and figures, one character longer than the
published longest value. The twin writes each value with its merged key read place for place in an
excluded template, or at least as long, merged, as the spill, so no twin cell's merged key is a real
cell's, and no twin cell is spelled as a real one. The exclusion publishes what the column does NOT
hold: no value, no extreme of one, no count below the floor.

Each case runs the product's command line, nobody at the keyboard, and each is red on the mutant its
docstring names (wave6/ID-ROOM/repair1/mutants.log).
"""

from __future__ import annotations

import json
import pathlib
import re
import types

import pytest

from synthtwin import contract, generation, parsing, profile, taxonomy

import fixtures
import identifier_room_shapes as room
import unanswered_identifier_shapes as held_shapes

FLOOR = 11
UID = re.compile(r"[012](\.(0|[1-9]\d*))+")

# EVERY SHAPE AT 600 ROWS, AND ONE CASE A WRITER AT 20,000 ROWS (the orchestrator's rule of
# 2026-10-26 11:06: a test file adds at most three minutes to the suite, and checks at 20,000 rows go
# into a KPI driver or one case a writer). The spill and the widened layouts (`sequential_from_one`),
# a UID root (`uid_752`), the merged key across two zero fills (`pad_split`, validated), values
# widened beside a layout keeping its exclusion (`pad_mixed`, validated: V4.1-A2), a stray cell
# beside an empty census (`outlier_long`, validated), a nought after a prefix (`p_five`), a key's
# case split across its letters (`letter_case_halves`) and a person's rows
# (`cerner_person_on_three_rows`).
# Every shape at 20,000 rows, the answered shapes at 20,000 rows, the validated shapes and three at
# 200,000 rows are K-HZ-06's (tools/measurements/kpi_identifier_room.py, kpi_run --slow).
AT_20000 = ("sequential_from_one", "uid_752", "pad_split", "pad_mixed", "outlier_long", "p_five",
            "letter_case_halves", "cerner_person_on_three_rows")

_SEEN: "dict[tuple[str, int, str, bool], dict[str, object]]" = {}


def _seen(factory: pytest.TempPathFactory, name: str, n: int, answer: str = "",
          validate: bool = False) -> "dict[str, object]":
    """One shape's run, built once for the whole file (a test reading it reads its own copy's facts)."""
    key = (name, n, answer, validate)
    if key not in _SEEN:
        _SEEN[key] = room.run_shape(factory.mktemp(f"{name}-{n}"), name, n, answer=answer, validate=validate)
    return _SEEN[key]


def _cases() -> "list[tuple[str, int]]":
    return [(name, 600) for name in room.every_shape()] + [(name, 20_000) for name in AT_20000]


# -- the gate: no twin cell names a real one --------------------------------------------------


@pytest.mark.parametrize(("name", "n"), _cases())
def test_no_twin_identifier_cell_equals_a_real_one(
    tmp_path_factory: pytest.TempPathFactory, name: str, n: int
) -> None:
    """Every shape at 600 rows, and one a writer at 20,000: 0 twin cells spelled as, or merging with, a real one.

    Counted twice: exactly as written, and on the merged key `profile.subject_keys` counts a person
    by (plan P4-D406). The shapes `room.VALIDATED` among them are validated too, at exit 0 at 20,000
    rows (every one of them is, in K-HZ-06's driver).
    Mutants: the exclusions dropped (`with_layout_exclusions` returning its column); the final pass
    returning at once where the census is empty (the stray-cell shapes write 19,998 real values);
    the exclusions read per layout and not on the merged key (`pad_split`, `dash_split`); the final
    pass taking a filling that drops a nought (`p_five`, `abc_dash_four`, `rsid_beside_dots`); the
    room of a template not read per class (`hex4_dense` exits 3); an exclusion written with a
    character a real cell holds -- each turns a shape red.
    """
    validate = n == 20_000 and name in room.VALIDATED
    seen = _seen(tmp_path_factory, name, n, validate=validate)
    if n == 600 and name in room.REFUSED_AT_600:
        assert seen["exits"][0] == 1 and not seen["twin"], (name, seen["exits"])
        return
    assert seen["exits"][:2] == (0, 0), (name, n, seen["exits"])
    assert seen["equal"] == 0, (name, n, seen["equal"])
    assert seen["merged"] == 0, (name, n, seen["merged"])
    if validate:
        assert seen["exits"][2] == 0, (name, n, seen["exits"])
    if seen["block"].get("role") == "identifier":
        assert parsing.EXCLUSION_SPILL in (seen["block"].get("layout_exclusions") or {}), (name, n)
    _code_runs_unchanged(name, seen, answered=False)


@pytest.mark.parametrize(
    ("name", "n"), [(name, 600) for name, sizes in room.ANSWERED if 600 in sizes]
)
def test_an_answered_identifier_writes_no_real_one(
    tmp_path_factory: pytest.TempPathFactory, name: str, n: int
) -> None:
    """The held shapes answered `identifier` (a person column): 0 twin cells equal to, or merging with, a real one.

    At 600 rows; at 20,000 rows each is K-HZ-06's."""
    seen = _seen(tmp_path_factory, name, n, answer="identifier")
    assert seen["exits"][:2] == (0, 0), (name, n, seen["exits"])
    assert seen["equal"] == 0, (name, n, seen["equal"])
    assert seen["merged"] == 0, (name, n, seen["merged"])
    _code_runs_unchanged(name, seen, answered=True)


# -- the fact's own privacy -------------------------------------------------------------------


def _keys_by_length(real: "list[str]", absent: "set[str]") -> "dict[int, list[str]]":
    by: "dict[int, list[str]]" = {}
    for cell in real:
        if cell.strip() and cell not in absent:
            key = parsing.merged_key(cell)
            by.setdefault(len(key), []).append(key)
    return by


@pytest.mark.parametrize("name", room.every_shape())
def test_the_exclusion_publishes_what_no_real_cell_holds(
    tmp_path_factory: pytest.TempPathFactory, name: str
) -> None:
    """Every written character is held by no real merged key at its place; the spill outlasts every cell.

    At 600 rows. A written character stands in a filling's merged key at `parsing.merged_places`'s
    place, among the real keys as long as the template's fillings', and no such real key holds it
    there. Every character the one-place choice passed over at its place, and every spelling a block
    passed over at its places, is held by at least the floor's keys, so no count of 1 to 10 is read
    off the choice (the orchestrator's ruling 3 of 2026-10-25, item 2, option (b)). A block writes every other place,
    so no two written characters are NEIGHBOURS -- no spelling read off it, written or passed over,
    holds two neighbouring characters of a value, so none is a fragment (the orchestrator's ruling
    1 of 2026-10-25, item 2 (a)). No exclusion is a real cell's text. Mutants: the choice passing
    over a character fewer than the floor's cells hold (the scan's stop removed); the block passing
    over a spelling 1 to 10 keys hold (its stop kept for a block of one place alone, the lane's
    repair-1 head; `random_seven_figures`, `uuid`, `rsid`); the block written
    at neighbouring places; a nought written where it opens a run of figures (the block's test
    removed, skeptic 1's M0); a real cell spelled as an exclusion kept; and the spill's own mutant
    (`_the_spill_says_nothing_the_description_does_not`).
    """
    seen = _seen(tmp_path_factory, name, 600)
    block = seen["block"]
    if name in room.REFUSED_AT_600:
        assert not block, name
        return
    exclusions = block.get("layout_exclusions") or {}
    absent = set(block.get("missing_by_source") or {})
    keyed = _keys_by_length(seen["real"], absent)
    texts = {parsing.folded(cell) for cell in seen["real"] if cell.strip()}
    prefixes = block.get("layout_prefixes") or {}
    whole = prefixes.get(parsing.PREFIX_OF_THE_COLUMN, "")
    noughts = bool(block.get("all_whole_numbers")) and any(
        parsing.whole_places_layout(form) != form for form in block.get("layout_forms") or {}
    )
    entries: "list[tuple[str, str]]" = []
    for scope, value in sorted(exclusions.items()):
        if isinstance(value, list):
            # SEVERAL SPELLINGS OF ONE BLOCK: each held to the same rules, two to the cap.
            assert 2 <= len(value) <= parsing.EXCLUSIONS_AT_MOST and len(set(value)) == len(value)
            entries += [(scope, text) for text in value]
        else:
            entries += [(scope, value)]
    for scope, text in entries:
        if scope == parsing.EXCLUSION_SPILL:
            continue
        assert parsing.folded(text) not in texts, (name, text)
        written = [place for place in range(len(text)) if text[place] != scope[place]]
        assert written, (name, scope)
        assert all(later - earlier > 1 for earlier, later in zip(written, written[1:])), (name, text)
        template = parsing.layout_template(scope, prefixes.get(scope, whole), noughts)
        # NO NOUGHT OPENS A RUN OF FIGURES: a twin key spelled so would merge one nought shorter.
        for place in written:
            if text[place] == "0":
                assert place > 0 and template[place - 1] in "%~^0123456789", (name, text)
        stands = parsing.merged_places(template)
        for key in keyed.get(parsing.merged_length(template), []):
            assert any(key[stands[place]] != text[place].casefold() for place in written), (name, scope, key)
        if len(written) == 1:
            place = written[0]
            held: "dict[str, int]" = {}
            for key in keyed.get(parsing.merged_length(template), []):
                held[key[stands[place]]] = held.get(key[stands[place]], 0) + 1
            alphabet = parsing.exclusion_alphabet(scope[place])
            if any("0" <= c <= "9" for c in alphabet) and any(c > "9" for c in alphabet):
                # A hexadecimal place is written with a figure, read from nine down,
                # where some real key is figures alone; else its letters are read
                # first, from the greatest down, and its figures after.
                figures = "".join(c for c in alphabet if "0" <= c <= "9")
                letters = "".join(c for c in alphabet if c > "9")
                alone = any(
                    key.isdigit() for key in keyed.get(parsing.merged_length(template), [])
                )
                alphabet = figures if alone else figures + letters
            for character in reversed(alphabet):
                if character == text[place]:
                    break
                if character == "0" and (place == 0 or template[place - 1] not in "%~^0123456789"):
                    continue
                count = held.get(character.casefold(), 0)
                assert count == 0 or count >= FLOOR, (name, scope, character, count)
    # A BLOCK PASSES OVER ONLY SPELLINGS THE FLOOR'S KEYS HOLD (the orchestrator's ruling 3 of
    # 2026-10-25, item 2, option (b)): read in the product's order, from the greatest down, every
    # spelling before the last one written is written, opens a run of figures with a nought, or is
    # held at the block's places by no key or by at least the floor's.
    by_scope: "dict[str, list[str]]" = {}
    for scope, text in entries:
        if scope != parsing.EXCLUSION_SPILL:
            by_scope.setdefault(scope, []).append(text)
    for scope, texts_of in by_scope.items():
        block_places = sorted({place for text in texts_of for place in range(len(text))
                               if text[place] != scope[place]}, reverse=True)
        if len(block_places) < 2:
            continue
        template = parsing.layout_template(scope, prefixes.get(scope, whole), noughts)
        stands = parsing.merged_places(template)
        keys = keyed.get(parsing.merged_length(template), [])
        alone = any(key and all("0" <= c <= "9" for c in key) for key in keys)
        worn: "dict[str, int]" = {}
        for key in keys:
            spelt = "".join(key[stands[place]] for place in block_places)
            worn[spelt] = worn.get(spelt, 0) + 1
        alphabets = [taxonomy._greatest_last(parsing.exclusion_alphabet(template[place]), alone)
                     for place in block_places]
        written_spellings = {"".join(text[place] for place in block_places) for text in texts_of}
        choices = 1
        for alphabet in alphabets:
            choices *= len(alphabet)
        for number in range(choices - 1, -1, -1):
            if not written_spellings:
                break
            rest, spelt = number, ""
            for alphabet in alphabets:
                spelt += alphabet[rest % len(alphabet)]
                rest //= len(alphabet)
            if spelt in written_spellings:
                written_spellings.discard(spelt)
                continue
            if any(spelt[at] == "0" and (place == 0 or template[place - 1] not in "%~^0123456789")
                   for at, place in enumerate(block_places)):
                continue
            count = worn.get(parsing.folded(spelt), 0)
            assert count == 0 or count >= FLOOR, (name, scope, spelt, count)
    # NO FRAGMENT (K-S3-64's: a run of five or more letters and figures out of a real value) stands
    # in the published text, and the only number readable off it is one figure: no two written
    # characters are neighbours. (K-S3-64's own counter also reads every lone figure as a number, so
    # a real `000001` "is" the `1` of `!!!9%1`; one figure names no value.)
    published = json.dumps(exclusions)
    runs = {run for cell in seen["real"] if cell.strip() for run in held_shapes._runs(cell)}
    assert not [run for run in runs if run in published], name
    assert all(len(figures) == 1 for _scope, text in entries if _scope != parsing.EXCLUSION_SPILL
               for figures in re.findall(r"[0-9]+", text)), name
    _the_spill_says_nothing_the_description_does_not(name, seen)


def _the_spill_says_nothing_the_description_does_not(name: str, seen: "dict[str, object]") -> None:
    """The spill is the column's prefix and figures, as long as the published longest value and one.

    Asked on every run of `test_the_exclusion_publishes_what_no_real_cell_holds`, at 600 rows
    (skeptic 1 of lane ID-ROOM, item 6): where every real cell is at most the published longest
    value, one longer; where rule A1 counted a longer cell in a shorter layout,
    `parsing.LAYOUT_FORM_LIMIT` and one, a length that says nothing of any cell -- so the spill's
    length less one is never a length only 1 to 10 real cells hold that the description does not
    publish. And it is longer, merged, than every real cell. Mutant: the spill built off the longest
    real cell (`pt_two_outliers`: 16, one more than its one cell of 15).
    """
    block = seen["block"]
    if block.get("role") != "identifier":
        return
    spill = (block.get("layout_exclusions") or {}).get(parsing.EXCLUSION_SPILL)
    holes = set(block.get("missing_by_source") or {})
    present = [cell for cell in seen["real"] if cell.strip() and cell not in holes]
    assert isinstance(spill, str) and present, name
    longest = max(len(cell) for cell in present)
    published = block["max_length"]
    if longest <= published:
        assert len(spill) == published + 1, (name, spill, published)
    else:
        assert len(spill) == parsing.LAYOUT_FORM_LIMIT + 1, (name, len(spill))
    whole = (block.get("layout_prefixes") or {}).get(parsing.PREFIX_OF_THE_COLUMN, "")
    bound = parsing.merged_length(parsing.layout_template(spill, whole, False))
    assert all(len(parsing.merged_key(cell)) < bound for cell in present), name
    lengths: "dict[int, int]" = {}
    for cell in present:
        lengths[len(cell)] = lengths.get(len(cell), 0) + 1
    if len(spill) - 1 != published:
        assert not 1 <= lengths.get(len(spill) - 1, 0) < FLOOR, (name, len(spill))


def test_no_real_value_reaches_the_description_through_an_exclusion(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """The densest shapes' exclusions carry no real value whole, at 600 rows; nor a real cell spelled as one.

    `literal_marks` (Codex's review, item 2) holds a real cell spelled `9%%%`, which the first head
    published as its layout's exclusion. Mutant: the check of a candidate against the real cells
    removed.
    """
    for name in ("uid_752", "sequential_from_one", "cerner_three_widths", "rsid", "keys_beside_na", "literal_marks"):
        seen = _seen(tmp_path_factory, name, 600)
        published = json.dumps(seen["block"].get("layout_exclusions") or {})
        for value in {cell for cell in seen["real"] if cell.strip()}:
            assert f'"{value}"' not in published, (name, value)


# -- code runs unchanged: the grammar, the length, the prefix, the noughts, the join ------------


UID_SHAPES = tuple(name for name in room.SHAPES if name.startswith("uid_")) + ("codes3_pacs_study_uid",)
# Rootless UIDs of two roots: the walk of the lane's base writes about four in five of their twin
# cells off the grammar (an arc led by a nought, a first arc past 2), which no published fact lets a
# twin avoid; the exclusion writes none of them (it never writes a rootless UID's first arc).
UID_WALK_OFF_THE_GRAMMAR = ("uid_ge_and_siemens", "uid_hl7_and_dicom")
PREFIXED = ("pt_seven_sequential", "pt_seven_person_on_three_rows", "e_nine_sequential", "p_five",
            "letters_eight_random", "abc_dash_four", "rsid", "codes3_vcf_rsid", "pt_two_outliers",
            "sixty_four_characters")
WHOLE = ("cerner_one_width", "cerner_three_widths", "cerner_two_widths",
         "cerner_person_on_three_rows", "codes3_cerner_encounter")
PEOPLE = ("sequential_person_on_three_rows", "sequential_person_on_twenty_rows",
          "pt_seven_person_on_three_rows", "cerner_person_on_three_rows",
          "zero_filled_person_on_four_rows", "uid_study_on_ten_rows", "uid_pydicom_repeated",
          "outlier_person_on_three_rows", "folded_with_spaces")


def _code_runs_unchanged(name: str, seen: "dict[str, object]", answered: bool) -> None:
    """What a shape's twin keeps for code written on the real table, on one run of it.

    Asked on every run of `test_no_twin_identifier_cell_equals_a_real_one` and
    `test_an_answered_identifier_writes_no_real_one`, at 600 and 20,000 rows, so no shape is built
    twice for it. THE UID GRAMMAR: every twin UID matches `[012](\\.(0|[1-9]\\d*))+`, is at most 64
    characters and opens with the published root (a held UID publishes no root and its twin writes
    placeholders off the grammar, as on the lane's base 2d25b07, 480 of 600 cells: lane CODES-1 part
    C's, asked only answered here); a rootless UID of two roots keeps the grammar's first arc on every
    twin cell, its exclusion never writing it (skeptic 1, item 4); mutants: the UID root's opening read
    only to the first placeholder, the first arc offered to the exclusion. THE PREFIX: every twin cell
    of a column publishing a `(column)` prefix opens with it, and of `two_long_prefixes` with one of
    its two layouts' prefixes (Codex, item 4); mutant: a widened value given the spill. THE NOUGHTS: a
    record number exported as `31000000.00` writes `.00` on every twin cell. THE CHECK DIGIT: NPI-like
    numbers keep ten figures and the description publishes no check-digit fact -- the product
    publishes none for any column, so the twin's Luhn digits were never the table's (a stated limit,
    P4-D432) -- and the exclusion writes its one figure at the first place. THE JOIN: the twin's
    census of rows a value equals the published one, a value moved whole, and a folded identity
    written with and without a space stays ONE identity (Codex, item 3); mutant: the final pass
    writing a fresh spelling on every ROW of a moved value instead of one a value, or widening the
    members of one identity apart.
    """
    twin = [cell for cell in seen["twin"] if cell.strip()]
    block = seen["block"]
    prefixes = block.get("layout_prefixes") or {}
    if name in UID_SHAPES and (answered or name not in dict(room.ANSWERED)):
        root = prefixes.get(parsing.PREFIX_OF_THE_COLUMN, "")
        if not parsing.is_a_uid_root(root):
            # A ROOTLESS UID: the walk draws its first arc as the lane's base did, and no exclusion
            # writes it (skeptic 1, item 4), so every exclusion leaves the first arc a placeholder.
            assert name in UID_WALK_OFF_THE_GRAMMAR or name == "uid_one_arc_repeating", (name, root)
            for scope, value in (block.get("layout_exclusions") or {}).items():
                if scope != parsing.EXCLUSION_SPILL:
                    for text in [value] if isinstance(value, str) else value:
                        assert text[: parsing.first_arc_places(scope)] == scope[: parsing.first_arc_places(scope)], (name, text)
        else:
            for cell in twin:
                assert UID.fullmatch(cell) is not None and len(cell) <= 64, (name, cell)
                assert cell.startswith(root), (name, cell, root)
    if name in PREFIXED:
        prefix = prefixes.get(parsing.PREFIX_OF_THE_COLUMN, "")
        assert prefix, name
        assert all(cell.startswith(prefix) for cell in twin), name
    if name == "two_long_prefixes":
        opening = ("A" + "-" * 59, "B" + "_" * 59)
        assert all(cell.startswith(opening) for cell in twin), name
        assert all(sum(1 for cell in twin if cell.startswith(one)) for one in opening), name
    if name in WHOLE:
        assert all(re.fullmatch(r"[1-9]\d*\.00", cell) for cell in twin), name
    if name == "npi_check_digit":
        assert all(re.fullmatch(r"[1-9]\d{9}", cell) for cell in seen["twin"]), name
        assert block["layout_exclusions"].get("%%%%%%%%%%", "").count("%") == 9
    if name in PEOPLE:
        counts: "dict[str, int]" = {}
        for cell in seen["twin"]:
            if cell.strip():
                counts[cell] = counts.get(cell, 0) + 1
        census: "dict[int, int]" = {}
        for rows in counts.values():
            census[rows] = census.get(rows, 0) + 1
        published = {int(key): value for key, value in block["n_distinct_by_occurrences"].items()}
        assert census == published, name
    if name == "folded_with_spaces":
        folded = {parsing.folded(cell) for cell in seen["twin"] if cell.strip()}
        assert len(folded) == block["n_distinct_folded"], (name, len(folded))


def test_the_code_pins_reach_every_shape_they_name() -> None:
    """Every shape a pin of `_code_runs_unchanged` names is one the gate builds."""
    named = (set(UID_SHAPES) | set(PREFIXED) | set(WHOLE) | set(PEOPLE) | {"npi_check_digit"}
             | set(room.VALIDATED) | set(room.AT_600_ALONE) | set(UID_WALK_OFF_THE_GRAMMAR))
    assert named <= set(room.every_shape()), sorted(named - set(room.every_shape()))


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


def test_the_merged_key_is_the_one_the_product_counts_people_by() -> None:
    """`parsing.merged_key` is `profile._subject_key`, and a template's places stand where its fillings' keys hold them."""
    for cell in ("REC-0007", "rec7", "Rec 7", "P0013736", "009297784", "1.2.276.0.12", "00", "a0f", "ß1"):
        assert parsing.merged_key(cell) == profile._subject_key(cell), cell
    assert parsing.merged_key("P0013736") == parsing.merged_key("P13736") == "p13736"
    assert parsing.merged_key("009297784") == parsing.merged_key("9297784")
    # Case folded and spaces dropped, edge spaces too (skeptic 1, item 8: M2 and M5).
    assert parsing.merged_key(" Rec 7 ") == parsing.merged_key("REC7") == parsing.merged_key("rec-7") == "rec7"
    assert parsing.merged_key(" 1000003") == parsing.merged_key("1000003 ") == "1000003"
    assert parsing.merged_places("REC%%%%") == (0, 1, 2, 3, 4, 5, 6)
    assert parsing.merged_places("!!%%%") == (-1, -1, 0, 1, 2)
    assert parsing.merged_places("@-%%") == (0, -1, 1, 2)
    assert parsing.merged_length("%%%%%%%%.00") == 9
    places = parsing.merged_places("REC%%%%")
    assert parsing.projected("REC9123", places) == parsing.merged_key("REC9123")
    assert parsing.projected("REC0123", places) != parsing.merged_key("REC0123")


def test_an_exclusion_is_its_layout_with_places_written_out() -> None:
    """`parsing.excludes_the_layout`, `written_excluded`, `widened_layout` and the spill's own reading."""
    assert parsing.excludes_the_layout("%%%%", "9%%%")
    assert parsing.excludes_the_layout("-%", "-9")
    assert not parsing.excludes_the_layout("%%%%", "A%%%")
    assert not parsing.excludes_the_layout("%%%%", "%%%%")
    assert not parsing.excludes_the_layout("!%%%", "9%%%")
    assert parsing.written_excluded("REC%%%%", "@@@9%%%") == "REC9%%%"
    assert parsing.written_excluded("%%%%.00", "9%%%.%%") == "9%%%.00"
    assert parsing.widened_layout("%%%%", 0, 2, 64) == "%%%%%%"
    assert parsing.widened_layout("@%%%%", 1, 1, 64) == "@%%%%%"
    assert parsing.widened_layout("%.%.%%", 4, 1, 64) == "%.%.%%%"
    # A rootless UID is widened in its second arc, so its first keeps one figure.
    assert parsing.widened_layout("%.%.%%", 0, 1, 64) == "%.%%.%%"
    assert parsing.widened_layout("@&&&", 0, 1, 64) == "@@&&&"
    assert parsing.widened_layout("%" * 64, 0, 1, 64) == ""
    assert parsing.widened_layout("%" * 64, 0, 1, 1 << 30) == "%" * 65
    assert parsing.first_arc_places("%.%.%%") == 1 and parsing.first_arc_places("%%.%%") == 0
    assert parsing.is_a_spill_layout("@@" + "%" * 70)
    assert not parsing.is_a_spill_layout("@@%%@")
    assert not parsing.is_a_layout_exclusion("%%%%")
    assert parsing.is_a_layout_exclusion("-9")


def test_a_figure_after_a_numbers_point_is_never_written_out() -> None:
    """Several spellings of one block, none at the figure after the point (plan P4-D432).

    500 different values `100.0` to `149.9` held as record numbers fill too much of `%%%.%` for one
    spelling, so the block carries several; none writes the figure after the point, which says
    whether a value is whole, so a twin value ending `.0` still wears a template. Mutant: the point's
    figures offered to the block -- `%9%.9` and its neighbours, and the twin of a held measurement
    column missed its census at exit 3 at 20,000 rows.
    """
    cells = [f"{value / 10:.1f}" for value in range(1000, 1500)] * 7
    keys = [parsing.merged_key(cell) for cell in cells]
    found = taxonomy._exclusion_of(keys, "%%%.%", "%%%.%", "", FLOOR, len(cells), 1470, 0, {})
    assert 2 <= len(found) <= parsing.EXCLUSIONS_AT_MOST, found
    assert all(text[4] == "%" and text[3] == "." for text in found), found
    worn = {(cell[0], cell[2]) for cell in cells}
    assert all((text[0], text[2]) not in worn for text in found), found


def test_a_layout_of_one_place_carries_its_free_characters_as_several_spellings() -> None:
    """A block of ONE place (skeptic 1 of lane ID-ROOM, item 1 (c)).

    Eleven cells of four letters, `a` to `d`, beside a pool: no one spelling leaves room for four
    values, so the layout `&` carries several, `z`, `y`, `x` and `w`, each held by no cell, passing
    over none. Mutant: the block's sizes read from two, and the layout carries no exclusion.
    """
    cells = ["a", "b", "c", "d", "a", "b", "c", "d", "a", "b", "c"]
    found = taxonomy._exclusion_of(cells, "&", "&", "", FLOOR, 11, 4, 0, {})
    assert found == ["z", "y", "x", "w"], found


def test_the_dense_hexadecimal_column_keeps_its_width(tmp_path: pathlib.Path) -> None:
    """Four hexadecimal characters at random, 600 rows (skeptic 1 of lane ID-ROOM, item 5 (b)).

    Three spellings of one block leave 768 fillings for 591 values, and on the lane's first head the
    search spent the fillings a value of another class skipped, so 460 of 600 cells were written five
    characters long and validation exited 3. Each reading of a value now reads its templates from its
    own step. Since the ruling 3 of 2026-10-25 (item 2, option (b)) the profile publishes no block
    for this column -- every spelling of the last and second places is held by 1 to 10 keys -- so its
    values are written wider and its census and lengths are listed: the twin validates at exit 0.
    The final pass is asked here on the three spellings the repair's first head published, `~9~2`,
    `~9~1` and `~9~0`, beside the spill: at most one cell in five written wider (69 measured), and
    as many cells of figures alone as the walk wrote (79). Mutants: one step a template (the first
    head's: 283 wider); the class test dropped (223 cells of figures alone).
    """
    seen = room.run_shape(tmp_path, "hex4_dense", 600, validate=True)
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    cells = [cell for cell in seen["real"]]
    rows: "dict[str, int]" = {}
    for cell in cells:
        rows[cell] = rows.get(cell, 0) + 1
    census: "dict[str, int]" = {}
    for count in rows.values():
        census[str(count)] = census.get(str(count), 0) + 1
    facts = contract.IdentifierFacts(
        min_length=4, max_length=4, all_whole_numbers=False,
        n_all_digits=sum(1 for cell in cells if cell.isdigit()), n_code_alphabet=16,
        n_distinct_by_occurrences=census, layout_forms={"~~~~": 600}, layout_prefixes={},
        layout_exclusions={"~~~~": ("~9~2", "~9~1", "~9~0"), parsing.EXCLUSION_SPILL: ("%%%%%",)},
    )
    column = types.SimpleNamespace(name="target", time_grain=None)
    written, _remarks = generation._spelled_off_the_real(column, facts, cells, ())  # type: ignore[arg-type]
    wider = sum(1 for cell in written if len(cell) > 4)
    assert wider <= 120, wider
    assert sum(1 for cell in written if cell.isdigit()) == sum(1 for cell in cells if cell.isdigit())
    assert len(set(written)) == len(set(cells))


def test_a_value_no_layout_describes_keeps_its_class(tmp_path: pathlib.Path) -> None:
    """A value no layout describes is written as itself and letters, so its class stays (plan P4-D432).

    `literal_marks` (Codex's review of the lane, item 2) holds cells such as `x%00`, which no layout
    describes, and the walk writes stand-ins no layout describes for them: written wider as figures,
    as the spill is, their class and the column's counts of figure-only and code cells would move.
    Validation exits 0 and the twin holds as many cells of figures alone as the table. Mutant: such
    a value given the spill, and the counts miss.
    """
    seen = room.run_shape(tmp_path, "literal_marks", 600, validate=True)
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    figures = [cell for cell in seen["twin"] if cell.isdigit()]
    assert len(figures) == sum(1 for cell in seen["real"] if cell.isdigit()), len(figures)


def test_a_folded_identity_is_written_wider_together() -> None:
    """One identity written `A1`, ` A1` and `a1 ` is widened to one new core (Codex's review of the lane, item 3).

    The layout `@%` carries no exclusion, so every value is written wider, as the spill's length
    asks: the three spellings of one folded identity take ONE new core, each in its own case and with
    its own spaces, and the column keeps two identities, as the walk wrote it. Mutant: the members
    moved one by one, each claimed as it is moved, and the identity splits in three.
    """
    facts = contract.IdentifierFacts(
        min_length=2, max_length=3, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=4,
        n_distinct_by_occurrences={"1": 4}, layout_forms={"@%": 3}, layout_prefixes={},
        layout_exclusions={parsing.EXCLUSION_SPILL: ("%%%%",)},
    )
    column = types.SimpleNamespace(name="key", time_grain=None)
    cells, _remarks = generation._spelled_off_the_real(column, facts, ["B1", "A1", " A1", "a1 "], ())  # type: ignore[arg-type]
    assert len({parsing.folded(cell) for cell in cells}) == 2, cells
    assert cells[2] == " " + cells[1] and cells[3] == cells[1].lower() + " ", cells
    assert all(len(parsing.merged_key(cell)) >= 4 for cell in cells), cells


def test_a_block_passes_over_no_spelling_fewer_than_the_floors_keys_hold() -> None:
    """A spelling 1 to 10 keys hold ends a block size, as a character does the one-place scan.

    The orchestrator's ruling 3 of 2026-10-25, item 2, option (b) (skeptic 1 of lane ID-ROOM, item
    7: the lane's first head passed over block spellings held by 1 to 10 real cells, 170 of them on
    random seven figures at 20,000 rows, 43 held by one cell). Four figures, the one-place choice too
    short for 2,000 values and the last place full, so the block of the last and second places is
    asked: its greatest spelling, `9` and `9`, is held by five keys, so the size ends and the layout
    carries none; held by eleven, it is passed over and the next free spellings are written. Mutant:
    the stop kept for a block of one place alone (the repair's first head), and `%9%8` and its
    neighbours are written past the five keys.
    """
    keys = [f"1{second}2{last}" for last in range(10) for second in range(5) for _ in range(15)]
    assert taxonomy._exclusion_of(keys + ["1929"] * 5, "%%%%", "%%%%", "", FLOOR, 2000, 2000, 0, {}) == []
    found = taxonomy._exclusion_of(keys + ["1929"] * 11, "%%%%", "%%%%", "", FLOOR, 2000, 2000, 0, {})
    assert found[:3] == ["%9%8", "%9%7", "%9%6"] and "%9%9" not in found, found


def test_no_block_writes_a_nought_where_it_opens_a_run_of_figures() -> None:
    """A block's spelling never opens a run of figures with a nought (skeptic 1 of lane ID-ROOM, M0).

    The nine hundred three-figure values `100` to `999` hold every spelling of the block's two
    places, the last and the first, but those whose first figure is a nought: a twin value written
    `0%9` would merge with a real `%9`, so the layout carries none. Mutant: the block's test of a
    leading nought removed, and `0%9` is published.
    """
    cells = [f"{value}" for value in range(100, 1000)]
    assert taxonomy._exclusion_of(cells, "%%%", "%%%", "", FLOOR, 900, 10, 0, {}) == []


def test_the_loader_refuses_an_exclusion_that_does_not_fit_its_layout(tmp_path: pathlib.Path) -> None:
    """LX2 for a written place inside the prefix, in one exclusion or one of several; a list of one,
    of a repeated spelling or under `(spill)` refused as no entry; LX3 for a spill no longer than the
    longest value or holding more than figures after the prefix; and a spill beside an empty census
    loaded (skeptic 1, item 2)."""
    seen = room.run_shape(tmp_path / "made", "pt_seven_sequential", 600, validate=False)
    document = json.loads(seen["texts"]["t-profile.json"])
    block = [one for one in document["columns"] if one["name"] == "target"][0]
    for place, (exclusions, rule) in enumerate((({"@@%%%%%%%": "Z@%%%%%%%"}, "LX2"),
                             ({"@@%%%%%%%": ["@@%9%9%%%", "Z@%%%%%%%"]}, "LX2"),
                             ({"@@%%%%%%%": ["@@%9%9%%%", "@@%9%9%%%"]}, "layout_exclusions"),
                             ({"@@%%%%%%%": ["@@%9%9%%%"]}, "layout_exclusions"),
                             ({"(spill)": ["@@%%%%%%%%%", "@@%%%%%%%%%%"]}, "layout_exclusions"),
                             ({"(spill)": "@@%%%%%%%"}, "LX3"),
                             ({"(spill)": "@@%%%%%%%@"}, "LX3"))):
        block["layout_exclusions"] = exclusions
        path = fixtures.write_profile(tmp_path, f"{rule}-{place}.json", document)
        with pytest.raises(Exception) as refused:
            contract.load_profile(str(path))
        assert rule in str(refused.value)
    stray = room.run_shape(tmp_path / "stray", "outlier_long", 600, validate=False)
    loaded = contract.load_profile(str(tmp_path / "stray" / "t-profile.json"))
    facts = [column for column in loaded.columns if column.name == "target"][0].facts
    assert isinstance(facts, contract.IdentifierFacts)
    assert not facts.layout_forms and parsing.EXCLUSION_SPILL in facts.layout_exclusions, stray["block"]
