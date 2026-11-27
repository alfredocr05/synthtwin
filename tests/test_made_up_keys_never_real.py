"""P4-D489 (lane ID-ROOM4, part a; K-HZ-39): made-up keys and codes a twin must never write as real ones.

WHAT WAS MEASURED (wave6/ID-ROOM4-spec-notes.md section 1; re-measured in the lane's step 0 on
7be40594, whose source is the public head's, at 20,000 rows through the commands a person types, with
the invented tables of `made_up_key_tables`). Two writers that are not identifier writers copied real
keys or codes BY CONSTRUCTION, with nothing in any file and validate exiting 0:

* C4, the writer of numbers too large or too small for the file format: its made-up spellings are
  fixed counters in the grammar code columns are written in (`1e400` onward at width 5), so a column of
  2,000 codes `1e400` to `9e622`, ten rows a code, got 20,000 of its 20,000 cells back as real codes,
  unanswered or answered `measurement`; a leading minus, `e-400` and `(-N)` 20,000 each, a two-figure
  mantissa 18,110, codes one a row 18,180, a capital E 20,000 case-folded; answered `code` the column
  became a long tail of labels whose stand-ins still wrote 6,440 real codes.
* C5, a key that repeats on a person's rows beside a declared person: read as a number and drawn
  inside its dense published range, a second key one a person wrote 19,990 of 20,000 real cells, an
  encounter key on two rows a value 19,999, a letter and four figures 19,990.

THE RULE. A1: once a description is final, `synthtwin profile` hands each such block to the writer's
own spelling function (`generation.unrepresentable_spellings`, which the writer calls too) and reads
the spellings against the column's real cells by merged key and, since batch 4t's last code round, by
the number each writes (`parsing.exact_of_a_number`; no wider mantissa ends with a nought), the holders counted in the subjects the
description is counted in; a column where one equals a real value 1 to 10 hold keeps its block with
the evidence NF139 WHATEVER ITS ANSWER, and its writer spells each cell one letter or figure longer
than its longest value (method G10.5 step 8; the orchestrator's LANE ID-ROOM4 RULINGS 5 (2)). A2:
lane HX5's rule is read counted in people beside a person column, so such a key is put HX5's question
and held until THAT question is answered (LANE ID-ROOM4 RULINGS 4, item 1); it is no person column.

THE CLASS, CLOSED BY ONE GENERATED CHECK A WRITER (LANE I4r RULINGS 1 (4)), with the 20,000-row cases
here kept to the writers' own tables and the rest in tools/measurements/kpi_keys_never_real.py. Each
check names the mutant it turns red.
"""

from __future__ import annotations

import dataclasses
import decimal
import json
import pathlib
import random
import sys

import pytest

import fixtures
from synthtwin import asking, canonical, cli, contract, generation, parsing, profile, reading, taxonomy

import made_up_key_tables as tables
import test_stage4_linear_work as linear

FLOOR = 11
FROZEN = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-33.json"


@pytest.fixture(scope="module")
def a_table(tmp_path_factory: pytest.TempPathFactory) -> reading.Table:
    """A table read from a file once, whose columns each case replaces (no file a case)."""
    path = fixtures.write(tmp_path_factory.mktemp("made-up-keys"), "t.csv", "c\n1\n2\n")
    return reading.read_table(f"{path}")


def _table(read: reading.Table, columns: "dict[str, list[str]]") -> reading.Table:
    names = list(columns)
    return dataclasses.replace(
        read, column_names=names, columns=[columns[name] for name in names], n_rows=len(columns[names[0]]),
        survey=None, file_bytes=0, fingerprint=0,
    )


def _by_value(text: str) -> "tuple[object, ...] | None":
    """The number a cell writes, read by this file alone, or None (batch 4t's last code round, item 1).

    Python's decimal module reads the cell and its coefficient's trailing noughts go into the exponent, with no
    context to round a long number: `30e404`, `3.0E+405` and `3e405` are one number. Zero and every cell that is
    no finite number give None (no made-up spelling is zero).
    """
    try:
        number = decimal.Decimal(text.strip())
    except (decimal.InvalidOperation, ValueError):
        return None
    if not number.is_finite() or not number:
        return None
    sign, digits, exponent = number.as_tuple()
    kept = len(digits)
    while kept > 1 and digits[kept - 1] == 0:
        kept -= 1
        exponent = int(exponent) + 1
    return ("value", sign, tuple(digits[:kept]), exponent)


def _keys_of(cell: str) -> "list[object]":
    """A cell's merged key and, where it writes a number, that number: the two ways a made-up spelling can name it."""
    number = _by_value(cell)
    return [parsing.merged_key(cell)] + ([number] if number is not None else [])


def _rare(cells: "list[str]", holders: "list[str] | None", absent: "tuple[str, ...]" = ()) -> "dict[object, bool]":
    """The present real spellings 1 to 10 hold (people where ``holders`` is given, else rows), by merged key and by value."""
    held: "dict[str, dict[str, bool]]" = {}
    for row in range(len(cells)):
        cell = cells[row]
        if not cell.strip() or cell in absent or parsing.is_missing_text(cell):
            continue
        held.setdefault(cell, {})[holders[row] if holders is not None else f"{row}"] = True
    return {key: True for cell in held if len(held[cell]) < FLOOR for key in _keys_of(cell)}


def _named_by(spellings: "tuple[str, ...]", rare: "dict[object, bool]") -> int:
    """How many spellings equal a rare real spelling exactly, case-folded, by merged key (merged holds both) or by value."""
    return sum(1 for spelling in spellings if any(key in rare for key in _keys_of(spelling)))


def _every_merged(cells: "list[str]") -> "dict[object, bool]":
    """The merged key of every present real cell, whoever holds it, and the number it writes."""
    return {key: True for cell in cells if cell.strip() for key in _keys_of(cell)}


def _spelled(read: reading.Table, described: "dict[str, object]", place: int = 0) -> "tuple[str, ...] | None":
    """The spellings the writer would write in one column of a description, as `synthtwin generate` loads it; None where none can be made."""
    return generation.made_up_spellings(contract.checked_description(canonical.serialize(described)), place)


# -- A1: the made-up spellings are read against the real cells -------------------------------------


def test_the_writer_places_the_one_functions_spellings(a_table: reading.Table, monkeypatch) -> None:
    """The writer writes `unrepresentable_spellings`' spellings and no others (RULING D1: one source).

    The function is replaced by one that hands back each of its spellings with a figure in front: the
    twin's cells are exactly those. Red on the mutant that gives the writer its own list (a writer that
    spells its cells without asking the function writes the plain spellings; measured: the mutant
    `_ONE_SOURCE = unrepresentable_spellings` bound at import, `wave6/ID-ROOM4/mutants.log`).
    """
    cells = [f"{1 + (row // 3) % 9}e{400 + (row // 3) // 9}" for row in range(90)]
    described = profile.build_document(_table(a_table, {"c": cells}), taxonomy.Settings(), [])
    assert described["columns"][0]["role"] == taxonomy.ROLE_UNREPRESENTABLE
    typed = contract.checked_description(canonical.serialize(described))
    plain = generation.made_up_spellings(typed, 0)
    real_function = generation.unrepresentable_spellings

    def marked_spellings(column, everywhere=()):
        spellings, notes = real_function(column, everywhere)
        return tuple(f"9{spelling}" for spelling in spellings), notes

    monkeypatch.setattr(generation, "unrepresentable_spellings", marked_spellings)
    twin = generation.generate(typed, 0)
    assert len(plain) == 30
    assert set(twin.columns[0]) == {f"9{spelling}" for spelling in plain}
    assert generation.made_up_spellings(typed, 0) == tuple(f"9{spelling}" for spelling in plain)


# The frozen cases of method G10.5 step 8, each the invented column the oracle's block was described from.
FROZEN_COLUMNS = {
    "wider_exponent": [f"{1 + c % 9}e{400 + c // 9}" for c in range(30) for _ in range(3)],
    "wider_negative": [f"-{1 + c % 9}e{400 + c // 9}" for c in range(24) for _ in range(2)],
    "wider_too_small": [f"{1 + c % 9}e-{400 + c // 9}" for c in range(24) for _ in range(2)],
    "wider_bracket": [f"(-{1 + c})" for c in range(40) for _ in range(2)],
    "wider_beside_numbers": [f"{10 + c % 90}e{400 + c // 90}" for c in range(30) for _ in range(2)]
    + ["12.5", "7", "-3.25", "41"],
    "wider_fold_partners": [f"{1 + c % 9}e{400 + c // 9}" for c in range(20)] + [f"{1 + c % 9}E{400 + c // 9}" for c in range(6)],
    # ...and the cases the oracle reads off its own reading (Codex's review of lane ID-ROOM4, items 1 and 4;
    # LANE ID-ROOM4 RULINGS 6 (10)): a fraction too small past what a mantissa under 400 fills, the same
    # past a three-figure exponent's room, a whole number the format holds past it (Codex's 1,312
    # figures beside a `7`), and three rounds of folded partners, case variants and then spaces.
    "wider_too_small_past_room": [f"{1 + c % 9}e-{400 + c // 9}" for c in range(20) for _ in range(2)] + ["1" + "0" * 98 + "7"] * 2,
    "wider_too_small_four_figures": [f"{1 + c % 9}e-{400 + c // 9}" for c in range(10) for _ in range(2)] + ["3" + "0" * 688 + "1"] * 2,
    "wider_whole_four_figures": [f"{10 ** 1311 + 7919 * i}" for i in range(5) for _ in range(2)] + ["7"] * 2,
    "wider_fold_partners_rounds": [f"{n}e400" for n in (1, 2, 3)] + [f"{n}E400" for n in (1, 2, 3)]
    + [f" {n}e400" for n in (1, 2, 3)] + [f"{n}e400 " for n in (1, 2, 3)],
}


@pytest.mark.parametrize("name", sorted(FROZEN_COLUMNS))
def test_the_product_writes_the_oracles_wider_content(name: str, a_table: reading.Table) -> None:
    """The oracle's thirty-third file, held to the product (A-P4-59): the block the profiler writes and the cells.

    The profiler describes each invented column, reads its writer's spellings against its cells and
    keeps its block with NF139 (the block is the frozen one), and the generator writes the oracle's
    content, spelling for spelling with its cells. Red on step 8 removed (the plain counters, real codes)
    and on any change of its families, its order or its partners.
    """
    case = json.loads(FROZEN.read_text(encoding="utf-8"))["cases"][name]
    read = _table(a_table, {"c": FROZEN_COLUMNS[name]})
    settings = taxonomy.Settings()
    held, unmade = cli._made_up_spellings_held(read, profile.build_document(read, settings, []), settings, [])
    assert held == ("c",) and unmade == ()
    described = profile.build_document(read, settings, [], made_up_held=list(held))
    assert described["columns"][0] == case["block"]
    twin = generation.generate(contract.checked_description(canonical.serialize(described)), 0)
    counted: "dict[str, int]" = {}
    for cell in twin.columns[0]:
        counted[cell] = counted.get(cell, 0) + 1
    assert counted == case["content"]
    assert _named_by(tuple(counted), _every_merged(FROZEN_COLUMNS[name])) == 0


def _a1_case(draw: random.Random) -> "tuple[list[str], tuple[str, ...], str]":
    """One generated column of numbers past a double's range, or of the writer's other families.

    Exponent spellings with mantissas of one to four figures, zero-padded or not, a small or capital
    e, a leading minus or none, too large or too small, exponents from 100 to 999 starting at every
    offset of the writer's walk; digit strings past 309 figures; a minus inside brackets; one a row or
    ten rows a code, or a mixture; beside a few numbers the format holds and a declared missing
    spelling the writer would spell; or one real code at the narrowest width among codes the writer
    never spells; or codes too small to hold beside digit strings and whole numbers of 100 to 330
    figures, which take the column's width past a three-figure exponent's room (the verify of repair
    1, item 1). Returns the cells, the declared missing spellings and the declaration (`code`,
    `measurement` or none).
    """
    codes = draw.randint(4, 45)
    family = draw.choice(("exponent", "exponent", "exponent", "digits", "bracket", "narrowest", "small-long"))
    figures = draw.randint(1, 4)
    padded = draw.random() < 0.5
    letter = draw.choice("eE")
    sign = draw.choice(("", "", "-"))
    small = draw.random() < 0.25
    start = draw.choice((400, 400 + draw.randint(0, 599), draw.randint(309, 999), draw.randint(100, 999)))
    if family == "small-long":
        # ...codes too small to hold, every one (an exponent of 400 or more).
        start = 400 + draw.randint(0, 500)
    real: "list[str]" = []
    for code in range(codes):
        mantissa = 1 + code % (10 ** figures - 1)
        written = f"{mantissa:0{figures}d}" if padded else f"{mantissa}"
        exponent = start + code // (10 ** figures - 1)
        if family == "exponent" or family == "small-long":
            power = exponent if exponent <= 999 else 309 + exponent % 690
            minus = "-" if small or family == "small-long" else ""
            real += [f"{sign}{written}{letter}{minus}{power}"]
        elif family == "digits":
            real += [f"{sign}{draw.randint(1, 9)}{'0' * draw.randint(309, 330)}{code}"]
        elif family == "bracket":
            real += [f"(-{1 + code})"]
        else:
            real += [f"{1 + code % 9}E+{1000 + code}"]
    if family == "narrowest":
        real[0] = "1e400"
    if family == "small-long":
        # ...beside digit strings and whole numbers of 100 to 330 figures, in range or past it.
        for _each in range(draw.randint(1, 3)):
            real += [f"{draw.randint(1, 9)}{'0' * draw.randint(99, 329)}{draw.randint(0, 9)}"]
    repeats = draw.choice((1, 10, 0))
    cells: "list[str]" = []
    for place in range(len(real)):
        cells += [real[place]] * (repeats if repeats else draw.randint(1, 12))
    if draw.random() < 0.3:
        cells += [f"{draw.uniform(1, 500):.1f}"]
    missing: "tuple[str, ...]" = ()
    if draw.random() < 0.2:
        missing = (f"{1 + draw.randint(0, 8)}e400",)
        cells += [missing[0]] * draw.randint(1, 15)
    draw.shuffle(cells)
    declared = draw.choice(("", "", "", "code", "measurement"))
    return cells, missing, declared


def test_a1_generated_columns_are_held_wherever_a_made_up_spelling_names_a_real_value(a_table: reading.Table) -> None:
    """A3 (i): 1,200 generated columns: held exactly where the writer would spell a value 1 to 10 hold.

    Each column is described as `synthtwin profile` describes it, declared or not; the expectation is
    read apart: the writer's spellings of the column described with NO declaration, against the real
    spellings 1 to 10 rows hold, by merged key and by value (this file's own reader, `_by_value`: since
    batch 4t's last code round a zero-padded `-010E-401` is the counters' `-1e-400`). Where the column
    is not held and stays of the role, its writer's spellings name no such value. Red on each mutant:
    the dry run removed; the fold or the merged key removed (exact or folded equality only: the
    capital-E and zero-padded cases); the reading by value removed; the hold skipped for a column
    declared `code` or `measurement`.
    """
    draw = random.Random(48901)
    held_count = unheld_count = 0
    for _case in range(1200):
        cells, missing, declared = _a1_case(draw)
        read = _table(a_table, {"c": cells})
        settings = taxonomy.Settings(declared_missing_values=missing)
        described = profile.build_document(
            read, settings, [],
            forced_codes=["c"] if declared == "code" else [],
            forced_measurements=["c"] if declared == "measurement" else [],
        )
        held = cli._made_up_spellings_held(read, described, settings, [])[0]
        unanswered = profile.build_document(read, settings, [])
        rare = _rare(cells, None, missing)
        spelled: "tuple[str, ...] | None" = ()
        if unanswered["columns"][0]["role"] == taxonomy.ROLE_UNREPRESENTABLE:
            spelled = _spelled(read, unanswered)
        # ...a column whose spellings cannot be made is held whole (Codex's item 1).
        expected = spelled is None or _named_by(spelled, rare) > 0
        assert (held == ("c",)) == expected, (declared, cells[:3], missing)
        if held:
            held_count += 1
        elif described["columns"][0]["role"] == taxonomy.ROLE_UNREPRESENTABLE:
            unheld_count += 1
            assert _named_by(_spelled(read, described), rare) == 0
    # The class reaches both sides (no vacuous pass).
    assert held_count > 300 and unheld_count > 100


def _published_counts(block: "dict[str, object]") -> "tuple[object, ...]":
    """What a column of the role publishes of its cells: the census and every count of notation, whole number and sign."""
    return tuple(
        block[key]
        for key in (
            "n_present", "n_distinct", "n_distinct_by_occurrences", "n_numeric", "n_not_numeric", "n_out_of_range",
            "n_contradictory", "n_whole", "n_fraction", "n_whole_unknown", "n_positive", "n_negative", "n_sign_unknown",
        )
    )


def test_a1_held_or_not_a_column_writes_no_real_value_through_generate(a_table: reading.Table) -> None:
    """A3 (i), through publication and generation: 60 generated columns of the role, held or not, generated whole.

    Every twin cell is counted against the real spellings 1 to 10 rows hold, exactly, case-folded and
    by merged key: 0. A held column keeps its block with NF139 (method G10.5 step 8): its twin, read
    back by the producer, is of the role with the census, the counts of notation, whole number and sign
    and the folded count the block publishes, and every twin cell's merged key is longer than every real
    cell's. (A column the format can hold is read as numbers and published, and its twin's chance-equal
    values are the owner's accepted class: not this lane's.) Red on the dry run removed (the held
    columns' writer copies their codes) and on step 8 removed.
    """
    draw = random.Random(48902)
    generated = held_seen = 0
    while generated < 60:
        cells, missing, _declared = _a1_case(draw)
        read = _table(a_table, {"c": cells})
        settings = taxonomy.Settings(declared_missing_values=missing)
        unanswered = profile.build_document(read, settings, [])
        if unanswered["columns"][0]["role"] != taxonomy.ROLE_UNREPRESENTABLE:
            continue
        generated += 1
        # ...both readings, as the command makes them (a column whose wider spellings meet a value or
        # cannot be made is held as record numbers).
        described = _held_as_the_command_holds(read, settings)
        block = described["columns"][0]
        twin = generation.generate(contract.checked_description(canonical.serialize(described)), 0)
        written = [cell for cell in twin.columns[0] if cell]
        rare = _rare(cells, None, missing)
        assert _named_by(tuple(written), rare) == 0, cells[:3]
        if block["detection_evidence"] != generation.SPELLED_WIDER_EVIDENCE:
            continue
        held_seen += 1
        if block["role"] != taxonomy.ROLE_UNREPRESENTABLE:
            assert _named_by(tuple(written), _every_merged(cells)) == 0, cells[:3]
            continue
        again = profile.build_document(_table(a_table, {"c": list(twin.columns[0])}), settings, [])["columns"][0]
        assert again["role"] == taxonomy.ROLE_UNREPRESENTABLE, cells[:3]
        assert _published_counts(again) == _published_counts(block), cells[:3]
        assert again["n_distinct_folded"] == block["n_distinct_folded"], cells[:3]
        longest = max(len(parsing.merged_key(cell)) for cell in cells if cell.strip())
        assert min(len(parsing.merged_key(cell)) for cell in written) > min(longest, block["max_length"]), cells[:3]
    assert held_seen > 15


def test_a1_where_even_the_wider_spellings_meet_a_value_the_column_is_held_as_record_numbers(a_table: reading.Table) -> None:
    """The second reading `synthtwin profile` makes on the description written, and its one way out (method G10.5 step 8).

    A real cell `max_length` does not measure -- ordinary text of figures and marks, `1 1 e 4 0 0` --
    has a merged key as long as the wider spellings, and here equals the first of them (`11e400`: since
    batch 4t's last code round no wider mantissa ends with a nought, so `10e400` is stepped past): read
    again, the column is named once more, and the command then holds it as record numbers with NF139
    (P4-D432's writer and its exclusion), whose twin writes 0 cells equal to a real value. Red on the dry
    run skipping a column already spelled wider (its wider spellings read against nothing).
    """
    cells = [f"{1 + c % 9}e{400 + c // 9}" for c in range(40) for _ in range(3)] + ["1 1 e 4 0 0"]
    read = _table(a_table, {"c": cells})
    settings = taxonomy.Settings()
    held = cli._made_up_spellings_held(read, profile.build_document(read, settings, []), settings, [])[0]
    assert held == ("c",)
    wider = profile.build_document(read, settings, [], made_up_held=list(held))
    assert parsing.merged_key("1 1 e 4 0 0") in {parsing.merged_key(one) for one in _spelled(read, wider) or ()}
    again = cli._made_up_spellings_held(read, wider, settings, [])[0]
    assert again == ("c",)
    apart = profile.build_document(read, settings, [], unanswered=list(again), made_up_held=list(held))
    block = apart["columns"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    twin = generation.generate(contract.checked_description(canonical.serialize(apart)), 0)
    assert _named_by(tuple(cell for cell in twin.columns[0] if cell), _every_merged(cells)) == 0


# The widths each family is read at: around every edge of step 8's constructions (a mantissa of 76 and
# 77 figures; a three-figure exponent out of room at a cell of 680 and 1,312; 310 figures), and drawn.
_EDGES = (5, 6, 7, 10, 77, 78, 79, 80, 81, 82, 100, 101, 307, 308, 309, 310, 311, 330, 331, 400, 679, 680, 681, 682,
          1000, 1310, 1311, 1312, 1313, 1400)


def test_a1_every_family_is_spelled_at_every_width_past_the_exponent_range() -> None:
    """A3 (i), the writer's six families at widths past the exponent's room (Codex's review of lane ID-ROOM4, item 1).

    Each shape and sign walks its family at the widths around every edge and at drawn widths up to
    1,400 letters and figures (and once at 9,680 and 9,681, where a fraction too small takes five
    exponent figures): its first members all read back as their shape and sign, hold exactly the
    width's letters and figures, open no run of figures with a nought (so the merged key is as long),
    and differ. Red on the fraction too small walked from 400 whatever the width (from a mantissa of
    77 figures every candidate reads as a number the format holds) and on the whole number the format
    holds kept to a three-figure exponent (none is left from a cell of 1,312).
    """
    draw = random.Random(48922)
    widths = list(_EDGES) + [draw.randint(5, 1400) for _each in range(40)]
    walked = 0
    for kind in range(6):
        for negative in (False, True) if kind not in (0, 5) else (False,):
            for width in widths + ([9680, 9681] if kind == 2 else []):
                here = generation._wider_width(kind, width)
                used: "dict[str, int]" = {}
                states: "dict[tuple[int, bool], int]" = {}
                seen: "dict[str, bool]" = {}
                for _member in range(12 if here < 2000 else 3):
                    spelling = generation._wider_family_number(kind, negative, width, states, used, ())
                    assert spelling is not None, (kind, negative, width)
                    assert generation._wider_reads_back(kind, negative, spelling), (kind, negative, width)
                    figures = sum(1 for character in spelling if character.isalnum())
                    assert figures == here == len(parsing.merged_key(spelling)), (kind, width, figures)
                    assert spelling not in seen
                    seen[spelling] = True
                    walked += 1
    assert walked > 3000


def test_a1_codes_too_small_beside_long_numbers_are_spelled_wider_at_widths_77_to_330(a_table: reading.Table) -> None:
    """A3 (i) at the widths the verify of repair 1 found (its item 1; LANE ID-ROOM4 RULINGS 7 (1)).

    Codes `1e-400` onward, 150 to 300 of them on 1 to 10 rows each, beside one to three whole numbers
    of a drawn width from 77 to 330 figures, which take the column's longest value past what a mantissa
    under ten to the minus 400 can fill: each column is held and spelled wider (NF139, of the role),
    its twin generates, the census and every count of notation, whole number and sign read back as
    published, and 0 twin cells equal a real value exactly, folded or by merged key. Red on the
    fraction too small walked from 400 whatever its width (every candidate a number the format holds:
    the dry run cannot spell the column, which is held as record numbers and loses its census).
    """
    draw = random.Random(48923)
    for _case in range(16):
        codes = draw.randint(150, 300)
        figures = draw.randint(1, 3)
        cells: "list[str]" = []
        for code in range(codes):
            mantissa = 1 + code % (10 ** figures - 1)
            cells += [f"{mantissa}e-{400 + code // (10 ** figures - 1)}"] * draw.randint(1, 10)
        width = draw.randint(77, 330)
        for _each in range(draw.randint(1, 3)):
            cells += [f"{draw.randint(1, 9)}{'0' * (width - 2)}{draw.randint(0, 9)}"] * draw.randint(2, 10)
        draw.shuffle(cells)
        read = _table(a_table, {"c": cells})
        settings = taxonomy.Settings()
        described = _held_as_the_command_holds(read, settings)
        block = described["columns"][0]
        assert block["role"] == taxonomy.ROLE_UNREPRESENTABLE, width
        assert block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE, width
        twin = generation.generate(contract.checked_description(canonical.serialize(described)), 0)
        written = [cell for cell in twin.columns[0] if cell]
        assert _named_by(tuple(written), _every_merged(cells)) == 0, width
        again = profile.build_document(_table(a_table, {"c": written}), settings, [])["columns"][0]
        assert _published_counts(again) == _published_counts(block), width


def _held_as_the_command_holds(read: reading.Table, settings: taxonomy.Settings) -> "dict[str, object]":
    """The description `synthtwin profile` writes of a table read whole, nothing declared: its two readings of the made-up spellings."""
    held, unmade = cli._made_up_spellings_held(read, profile.build_document(read, settings, []), settings, [])
    apart = list(unmade)
    while True:
        described = profile.build_document(read, settings, [], unanswered=list(apart), made_up_held=list(held))
        again, unmade = cli._made_up_spellings_held(read, described, settings, [])
        more = [name for name in again if name not in apart and (name in held or name in unmade)]
        newly = [name for name in again if name not in held]
        if not more and not newly:
            return described
        apart += more
        held = held + tuple(newly)


@pytest.mark.parametrize("holders", [1, 10, 11, 12])
def test_a1_a_column_spelled_wider_meets_no_real_value_however_many_hold_it(holders: int, a_table: reading.Table) -> None:
    """NF139's promise read on every real value (Codex's review of lane ID-ROOM4, item 5; LANE ID-ROOM4 RULINGS 6 (3)).

    Codes `1e400` onward, two rows each, beside ``holders`` cells `t10000`: the wider writer's first
    ordinary text is `t10000`, so the second reading names the column whatever number of rows hold
    that value (the floor of 11 is a rule about published counts, never about a twin cell equal to a
    real one), and the command holds it as record numbers: 0 twin cells equal to a real value. Red on
    the version whose second reading counts holders as the first does (eleven and twelve real cells
    written while NF139 promised none).
    """
    cells = [f"{1 + c % 9}e{400 + c // 9}" for c in range(600) for _ in range(2)] + ["t10000"] * holders
    read = _table(a_table, {"c": cells})
    settings = taxonomy.Settings()
    described = _held_as_the_command_holds(read, settings)
    block = described["columns"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    twin = generation.generate(contract.checked_description(canonical.serialize(described)), 0)
    assert _named_by(tuple(cell for cell in twin.columns[0] if cell), _every_merged(cells)) == 0


def test_a1_a_family_spent_at_its_width_holds_the_column_whole(a_table: reading.Table, monkeypatch) -> None:
    """A dry run that cannot make the spellings holds the column whole (Codex's review of lane ID-ROOM4, item 1).

    THE WALK: a whole number this format holds, spelled at 1,158 letters and figures, has 1,386
    members (154 exponents of nine, the fewest at any width; three figures and four tie there), then
    none, and the column's spellings raise `errors.DomainTooSmall`. THE HOLD: where the writer's dry
    run cannot make a column's wider spellings (`generation.made_up_spellings` is None, as on a column
    of more such numbers than the family holds), the command's reading names the column among those it
    cannot spell, the command holds it as record numbers with NF139 and says why, and the twin
    generates with 0 cells equal to a real value. Red on the reading that takes no spellings for none
    to read (the description accepted, and `synthtwin generate` refusing it).
    """
    states: "dict[tuple[int, bool], int]" = {}
    used: "dict[str, int]" = {}
    made = 0
    while generation._wider_family_number(3, False, 1158, states, used, ()) is not None:
        made += 1
    assert made == 1386
    cells = [f"{1 + c % 9}e{400 + c // 9}" for c in range(40) for _ in range(3)]
    read = _table(a_table, {"c": cells})
    settings = taxonomy.Settings()
    held = cli._made_up_spellings_held(read, profile.build_document(read, settings, []), settings, [])[0]
    assert held == ("c",)
    wider = profile.build_document(read, settings, [], made_up_held=list(held))
    real_spellings = generation.made_up_spellings

    def spent(typed: contract.Profile, place: int) -> "tuple[str, ...] | None":
        if typed.columns[place].detection_evidence == generation.SPELLED_WIDER_EVIDENCE:
            return None
        return real_spellings(typed, place)

    monkeypatch.setattr(generation, "made_up_spellings", spent)
    assert cli._made_up_spellings_held(read, wider, settings, []) == (("c",), ("c",))
    assert "cannot make up spellings of their width" in cli._made_up_held_said(("c",), ("c",), ("c",))
    described = _held_as_the_command_holds(read, settings)
    block = described["columns"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    twin = generation.generate(contract.checked_description(canonical.serialize(described)), 0)
    assert _named_by(tuple(cell for cell in twin.columns[0] if cell), _every_merged(cells)) == 0


def _folded_block(a_table: reading.Table, pairs: int) -> "contract.ColumnBlock":
    """The block of a column spelled wider whose ``pairs`` codes are each written once with `e` and once with `E`."""
    cells = [f"{1 + c % 9}e{400 + c // 9}" for c in range(pairs)] + [f"{1 + c % 9}E{400 + c // 9}" for c in range(pairs)]
    read = _table(a_table, {"c": cells})
    described = profile.build_document(read, taxonomy.Settings(), [], made_up_held=["c"])
    return contract.checked_description(canonical.serialize(described)).columns[0]


def _spelled_wider_scanning_every_parent(column: "contract.ColumnBlock", facts: object) -> "tuple[str, ...]":
    """Step 8 as repair 1 built it: each partner chosen by a scan of every parent of its family (the regression of Codex's item 4)."""
    groups = generation._groups_of(column.facts.n_distinct_by_occurrences)
    kinds, signs = generation._unrepresentable_families(column, column.facts, groups)
    width = max(column.facts.max_length, 1) + 1
    folded = min(column.n_distinct_folded, len(groups))
    used: "dict[str, int]" = {}
    walked: "dict[tuple[int, bool], int]" = {}
    parents: "dict[tuple[int, bool], list[int]]" = {}
    partners: "list[int]" = []
    spellings: "list[str]" = []
    for index in range(len(groups)):
        family = (kinds[index], signs[index])
        partners += [0]
        if index >= folded and family in parents:
            chosen = parents[family][0]
            for place in parents[family]:
                if partners[place] < partners[chosen]:
                    chosen = place
            partner = generation._case_variant(spellings[chosen], 1) or f"{spellings[chosen]} "
            partners[chosen] = partners[chosen] + 1
            spellings += [generation._take(partner, used)]
            continue
        spelling = generation._wider_family_number(kinds[index], signs[index], width, walked, used, ())
        spellings += [spelling or ""]
        if index < folded:
            parents.setdefault(family, []).append(index)
    return tuple(spellings)


def _lines_of(codes: "tuple[object, ...]", function: "object", *arguments: object) -> int:
    """Lines the frames of ``codes`` alone run during one call of ``function``, counted with no clock.

    The walk of a family and its parser are the same either way and are left out, so what is counted
    is the step's own choosing: its loop over the groups and each partner's parent.
    """
    ran = [0]

    def lines(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        return lines

    def calls(frame: object, event: str, argument: object) -> object:
        if event == "call" and frame.f_code in codes:  # type: ignore[attr-defined]
            return lines
        return None

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return ran[0]


def test_a1_folded_partners_cost_no_more_lines_a_value_as_the_values_double(a_table: reading.Table) -> None:
    """The folded partners of step 8 in time linear in the values (Codex's review of lane ID-ROOM4, item 4).

    Lines step 8's own choosing runs (`_spelled_wider` and `_wider_partner`; the family's walk and its
    parser are the same either way) spelling a column of N codes each written once with `e` and once
    with `E` -- N parents and N partners -- at N and 2N, counted with no clock: about two now
    (`test_stage4_linear_work.LINEAR_AT_MOST`); and the regression beside it, each partner's parent
    found by a scan of every parent of its family as repair 1 built it, must grow as the square
    (`SQUARE_AT_LEAST`), so the measure sees the defect (a column of 500,000 such pairs at 1,000,000
    rows: 250 billion comparisons a spelling run). The same spellings either way.
    """
    small, large = _folded_block(a_table, 300), _folded_block(a_table, 600)
    assert generation._spelled_wider(small, small.facts, ())[0] == _spelled_wider_scanning_every_parent(small, small.facts)
    now = (generation._spelled_wider.__code__, generation._wider_partner.__code__)
    now_small = _lines_of(now, generation._spelled_wider, small, small.facts, ())
    now_large = _lines_of(now, generation._spelled_wider, large, large.facts, ())
    assert now_large / now_small < linear.LINEAR_AT_MOST, (now_small, now_large)
    old = (_spelled_wider_scanning_every_parent.__code__,)
    old_small = _lines_of(old, _spelled_wider_scanning_every_parent, small, small.facts)
    old_large = _lines_of(old, _spelled_wider_scanning_every_parent, large, large.facts)
    assert old_large / old_small >= linear.SQUARE_AT_LEAST, (old_small, old_large)


def test_a1_the_command_holds_a_column_whose_wider_spellings_meet_a_value(tmp_path: pathlib.Path) -> None:
    """The command's second reading, through `synthtwin profile` and `synthtwin generate` (the verify of repair 1, item 2).

    The gate's own column -- 40 codes three times each and `1 1 e 4 0 0`, whose merged key is the first
    wider spelling's (`11e400`; no wider mantissa ends with a nought since batch 4t's last code round) --
    profiled with nobody at the keyboard (the library's small-table path): the command's loop holds it
    as record numbers with NF139, and the twin writes 0 cells equal to a real value by merged key. Red
    on the loop that drops the hold of a column already spelled wider (3 twin cells equal to the
    straggler by merged key).
    """
    cells = [f"{1 + c % 9}e{400 + c // 9}" for c in range(40) for _ in range(3)] + ["1 1 e 4 0 0"]
    path = tables.write_table(tmp_path / "s.csv", ["c"], [[cell] for cell in cells])
    with tables.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{path}", "--out-dir", f"{tmp_path}"], small_tables_refused=False) == 0
        assert cli.main(
            ["generate", f"{tmp_path / 's-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0"],
            small_tables_refused=False,
        ) == 0
    block = json.loads((tmp_path / "s-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER and block["detection_evidence"] == generation.SPELLED_WIDER_EVIDENCE
    twin = tables.columns_of(tmp_path / "s-twin.csv")["c"]
    assert tables.equal_cells(cells, twin)["merged"] == 0


# -- A1 counted in the subjects the description is counted in ---------------------------------------


def _a1_people_case(draw: random.Random) -> "tuple[list[str], list[str], int]":
    """One generated column of codes in the writer's grammar beside a column that repeats on its people.

    Codes `1e400` onward (a small or capital e, a leading minus or none), each held by ``holders``
    people over many rows (the floor's rows or more, held by 1 to 10 people), or by many people over few
    rows each, or a mixture; the people column is a declared person, or an undeclared key the person
    question names. Returns the people cells, the code cells and how many people each code stands on.
    """
    holders = draw.choice((1, 2, 3, 5, 10, 11, 12, 20))
    people = holders * draw.randint(8, max(9, 200 // holders))
    rows = draw.randint(2, 15) if holders < FLOOR else draw.randint(1, 2)
    sign = draw.choice(("", "", "-"))
    letter = draw.choice("eE")
    persons: "list[str]" = []
    codes: "list[str]" = []
    for person in range(people):
        code = person // holders
        for _row in range(rows):
            persons += [f"S{100000 + person}"]
            codes += [f"{sign}{1 + code % 9}{letter}{400 + code // 9}"]
    return persons, codes, holders


def test_a1_holders_are_counted_in_the_people_of_every_subject(a_table: reading.Table) -> None:
    """Skeptic 1 of lane ID-ROOM4, items 2 and 3: 600 generated code columns beside a column of people.

    The held reading follows the people count: a column whose codes stand on the floor's rows or more
    but on 1 to 10 people is held, and one whose every code stands on the floor's people or more is not,
    whether the people column is declared (a person column) or an undeclared key the open person
    question names (a subject the final describe counts in). Red on the mutant that counts the holders
    in rows alone (MS1: `held = min(held, ...)` removed) and on the subjects reduced to the declared
    person columns (the code on twenty rows of one person, copied while the person question was open).
    """
    draw = random.Random(48904)
    held_count = unheld_count = 0
    for _case in range(600):
        persons, codes, fewest = _a1_people_case(draw)
        read = _table(a_table, {"pid": persons, "c": codes})
        declared = draw.random() < 0.5
        settings = taxonomy.Settings(person_columns=("pid",) if declared else ())
        described = profile.build_document(read, settings, ["pid"] if declared else [], subjects=["pid"])
        held = cli._made_up_spellings_held(read, described, settings, ["pid"])[0]
        rare = _rare(codes, persons)
        spelled = _spelled(read, described, 1)
        expected = spelled is None or _named_by(spelled, rare) > 0
        assert (held == ("c",)) == expected, (declared, fewest, codes[:2])
        if expected:
            held_count += 1
        else:
            unheld_count += 1
    assert held_count > 150 and unheld_count > 100


# -- A2: a key beside a declared person is held -----------------------------------------------------


def _a2_case(draw: random.Random) -> "tuple[list[str], list[str], str, bool]":
    """One generated key column beside a person column, or a measurement control.

    Keys: an opening of zero to six letters with or without a mark, four to nine figures, one a
    person or one an encounter (each person one to five encounters, one to six rows each), in a run
    or at random, beside placeholders, words and blank cells set aside, INTERLEAVED among the key rows
    (skeptic 1 of lane ID-ROOM4, item 5: the people of each present cell are matched to its own row).
    Controls (``False``): a whole number fixed per person with ties, a decimal fixed per person, a
    count a row, an age. Returns the person cells, the column, the role the column takes at the table
    floor (an opening of letters: affixed; figures alone: count) and whether the rule must reach it:
    every key of five figures or more, and a key of four figures in a run (RULING D4: HX5's five-figure
    line is dropped for a run alone; four figures at random stay part b's item B3, a stated limit).
    """
    people = draw.randint(60, 250)
    persons: "list[str]" = []
    column: "list[str]" = []
    kind = draw.choice(("key", "key", "key", "fixed", "decimal", "count", "age"))
    letters = "".join(draw.choice("ABCDEKPRSVZ") for _each in range(draw.randint(0, 6)))
    mark = draw.choice(("", "", "-", "_")) if letters else ""
    width = draw.randint(4, 9)
    run = draw.random() < 0.5
    start = draw.randint(10 ** (width - 1), 10 ** width - 2000)
    encounters = draw.random() < 0.4
    asides = kind == "key" and draw.random() < 0.4
    taken: "dict[int, bool]" = {}
    serial = start

    def key() -> str:
        nonlocal serial
        if run:
            serial = serial + 1
            return f"{letters}{mark}{serial}"
        while True:
            number = draw.randint(10 ** (width - 1), 10 ** width - 1)
            if number not in taken:
                taken[number] = True
                return f"{letters}{mark}{number}"

    for person in range(people):
        fixed = draw.randint(45, 140)
        decimal = f"{draw.uniform(40, 120):.1f}"
        age = draw.randint(18, 95)
        own = "" if encounters else key()
        for _visit in range(draw.randint(1, 5) if encounters else 1):
            visit_key = key() if encounters else own
            for _row in range(draw.randint(1, 6) if encounters else draw.randint(2, 6)):
                if asides and draw.random() < 0.02:
                    # ...a placeholder, a word or a blank on a row of ANOTHER person, among the keys.
                    persons += [f"S{100000 + draw.randint(0, people - 1)}"]
                    column += [draw.choice(("UNKNOWN", "0", "-1", ""))]
                persons += [f"S{100000 + person}"]
                if kind == "key":
                    column += [visit_key]
                elif kind == "fixed":
                    column += [f"{fixed}"]
                elif kind == "decimal":
                    column += [decimal]
                elif kind == "count":
                    column += [f"{draw.randint(0, 20)}"]
                else:
                    column += [f"{age}"]
    role = taxonomy.ROLE_AFFIXED if letters else taxonomy.ROLE_COUNT
    return persons, column, role, kind == "key" and (width >= 5 or run)


def test_a2_generated_keys_beside_a_person_are_reached_and_controls_are_not() -> None:
    """A3 (ii): 2,000 generated columns beside a person column, counted in the people each value stands on.

    Every key is reached (one question, HX5's, and its hold follow); every control stays unasked.
    Red on each mutant: the people arm removed; rows counted instead of people (a key on two rows a
    value or more is never reached); the holders matched by place instead of by row (MS6: the asides
    interleaved among the keys move each later key onto another row's person).
    """
    draw = random.Random(48903)
    keys = controls = asided = 0
    for _case in range(2000):
        persons, column, role, a_key = _a2_case(draw)
        if not a_key and column and column[0][:1].isalpha():
            continue
        settings = taxonomy.Settings(person_columns=("pid",))
        present, _absent = taxonomy.split_missing(column, settings)
        people = asking._people_of([{"name": "pid"}, {"name": "c"}], [persons, column], settings)
        holders = asking._holders_of(column, present, people, "c", settings)
        reached = asking._each_on_one_person(present, holders, role, False, "c")
        if a_key:
            keys += 1
            asided += int(len(present) < len(column))
            assert reached, column[:3]
        else:
            controls += 1
            assert not reached, column[:3]
    assert keys > 600 and controls > 500 and asided > 100


_NINES_BOUNDARIES = (999, 9999, 99999, 999999)
_SPELLINGS = ("bare", "comma", "mixed", "comma-nines-bare")


def _spelled_key(number: int, spelling: str, draw: random.Random) -> str:
    """A key of figures alone written bare, with comma thousands, either at random, or with comma thousands save nines alone."""
    nines = f"{number}" == "9" * len(f"{number}")
    if spelling == "bare" or (spelling == "comma-nines-bare" and nines):
        return f"{number}"
    if spelling == "mixed" and draw.random() < 0.5:
        return f"{number}"
    return f"{number:,}"


def test_a2_runs_across_every_all_nines_boundary_are_reached_in_every_spelling() -> None:
    """A3 (ii) widened (Codex's review of lane ID-ROOM4, item 3; the orchestrator's LANE ID-ROOM4 RULINGS 6 (1)).

    A run of keys of figures alone beside a person column crosses each all-nines boundary (999, 9,999,
    99,999, 999,999), one a person or one an encounter, written bare, with comma thousands, at random
    either way, or with comma thousands save the nines alone (`9999` bare among `8,900` to `10,899`:
    the walk sets it aside as nobody's, and a second copy of the run test that left it out saw a gap,
    so the twin wrote 19,980 real keys). Every run is reached: the arm's one test of a run closes a gap
    a set-aside nines value stands in. Red on the version whose run test before the five-figure line
    reads no nines.
    """
    draw = random.Random(48919)
    seen: "dict[tuple[int, str], int]" = {}
    for case in range(480):
        boundary = _NINES_BOUNDARIES[case % len(_NINES_BOUNDARIES)]
        spelling = _SPELLINGS[(case // len(_NINES_BOUNDARIES)) % len(_SPELLINGS)]
        people = draw.randint(60, 250)
        encounters = draw.random() < 0.4
        serial = boundary - draw.randint(1, people // 2)
        persons: "list[str]" = []
        column: "list[str]" = []
        for person in range(people):
            for _visit in range(draw.randint(1, 4) if encounters else 1):
                serial = serial + 1
                written = _spelled_key(serial, spelling, draw)
                for _row in range(draw.randint(1, 5) if encounters else draw.randint(2, 6)):
                    persons += [f"S{100000 + person}"]
                    column += [written]
        settings = taxonomy.Settings(person_columns=("pid",))
        present, _absent = taxonomy.split_missing(column, settings)
        people_read = asking._people_of([{"name": "pid"}, {"name": "c"}], [persons, column], settings)
        holders = asking._holders_of(column, present, people_read, "c", settings)
        assert asking._each_on_one_person(present, holders, taxonomy.ROLE_COUNT, False, "c"), (boundary, spelling)
        seen[(boundary, spelling)] = seen.get((boundary, spelling), 0) + 1
    assert len(seen) == len(_NINES_BOUNDARIES) * len(_SPELLINGS)


def _people_words(persons: "list[str]", column: "list[str]") -> "tuple[str, str]":
    """The arm the people's rule reads a key column by, beside a person column, and the words its question says."""
    settings = taxonomy.Settings(person_columns=("pid",))
    present, _absent = taxonomy.split_missing(column, settings)
    people = asking._people_of([{"name": "pid"}, {"name": "c"}], [persons, column], settings)
    holders = asking._holders_of(column, present, people, "c", settings)
    arm = asking._each_on_one_person_arm(present, holders, taxonomy.ROLE_AFFIXED, False, "c")[0]
    return arm, asking._each_on_one_person_said(present, holders, False, "c", taxonomy.ROLE_AFFIXED)


def test_a2_each_arm_says_what_its_condition_establishes() -> None:
    """The people's question in the words of the arm that reached the key (Codex's review of lane ID-ROOM4, item 6).

    Arm (a), every value on one person: so it says; all but one in a hundred: nearly so. Arm (b), keys
    `P100000` to `P101999` ten rows each, five rows on person i and five on person i + 1, the last on
    one (1,999 values with two holders): a run with fewer than two people a value on average, never
    "each value on the rows of one person". Arm (c), lettered keys of six figures at random, most on
    two people: the same average. Red on the run's words saying each value stands on one person.
    """
    one = "each value standing on the rows of one person"
    average = "fewer than two people a value on average"
    persons = [f"S{100000 + key}" for key in range(300) for _row in range(3)]
    keys = [f"P{500000 + key}" for key in range(300) for _row in range(3)]
    arm, words = _people_words(persons, keys)
    assert arm == "different" and one in words and average not in words
    persons = persons + ["S100001"]
    keys = keys + ["P500000"]
    arm, words = _people_words(persons, keys)
    assert arm == "nearly" and f"nearly {one}" in words
    persons = []
    keys = []
    for key in range(2000):
        for copy in range(10):
            persons += [f"S{10000 + (key if copy < 5 or key == 1999 else key + 1)}"]
            keys += [f"P{100000 + key}"]
    arm, words = _people_words(persons, keys)
    assert arm == "sequence" and average in words and one not in words
    draw = random.Random(48924)
    numbers = draw.sample(range(100000, 999999), 600)
    persons = []
    keys = []
    for key in range(600):
        for copy in range(4):
            persons += [f"S{10000 + key + (copy % 2) * (key < 450)}"]
            keys += [f"ACC{numbers[key]}"]
    arm, words = _people_words(persons, keys)
    assert arm == "prefixed" and average in words and one not in words
    assert asking._EACH_ON_ONE_PERSON_SEEN in words


def _agreement_tables(rows: int, people: int) -> "dict[str, tuple[list[str], list[list[str]]]]":
    """The tables the people's rule reads, after Codex's two (lane ID-ROOM4, items 2 and 3).

    A second key one a person and an encounter key two a person beside a measurement; keys run in
    sequence across 9,999 with comma thousands save `9999`, bare; a key one a person beside a column
    of dates with stray codes (one cell in fifty `PENDING`), the shape whose group a walk asks again
    alone (the scoped verify 2 of lane ID-ROOM4, item 1; named to come last, so the older tables'
    generated orders and budgets stay as they were). ``people`` people, as many rows each.
    """
    found: "dict[str, tuple[list[str], list[list[str]]]]" = {}
    found["second-key"] = (
        ["pid", "hr", "pkey", "enc"],
        [
            [
                f"S{10000 + row % people}", f"{60 + (row * 7) % 40}", f"P{100000 + row % people}",
                f"E{1000000 + (row % people) * 2 + (row // people) % 2}",
            ]
            for row in range(rows)
        ],
    )
    found["nines-bare"] = (
        ["pid", "v", "hr"],
        [
            [f"S{10000 + row % people}", "9999" if 9500 + row % people == 9999 else f"{9500 + row % people:,}", f"{60 + (row * 7) % 40}"]
            for row in range(rows)
        ],
    )
    found["second-pass"] = (
        ["pid", "pkey", "d"],
        [
            [
                f"S{10000 + row % people}", f"P{100000 + row % people}",
                "PENDING" if row % 50 == 7 else f"2024-{1 + row % 12:02d}-{1 + row % 28:02d}",
            ]
            for row in range(rows)
        ],
    )
    return found


def _asked_of(read: reading.Table, document: "dict[str, object]", settings: taxonomy.Settings) -> "list[tuple[str, str, str]]":
    """Every question `synthtwin profile`'s first walk puts, as name, reason and words."""
    found = profile.questions_of(
        read, document, settings, ["pid"], (), profile.stored_as_of(read, settings),
        None, None, asking.DateColumnsSeen(), False, (), False,
    )
    return [(question.name, question.reason, question.shape) for question in found.asked + found.listed]


def _asked_in_two_groups(
    path: pathlib.Path, document: "dict[str, object]", settings: taxonomy.Settings, monkeypatch
) -> "tuple[list[tuple[str, str, str]], list[tuple[int, int, bool, bool]]]":
    """The table at ``path`` read in ONE walk of two groups, its first two columns in the first: its questions, and each group asked.

    The group budget is read off `reading.column_groups` until it cuts so (halving the span of
    budgets). Each group asked is its first column, its width, whether it may describe and whether
    it gave no answer.
    """
    monkeypatch.setattr(reading, "WALK_BYTES", 1 << 40)
    low, high = 1, 64 * path.stat().st_size
    while True:
        budget = (low + high) // 2
        monkeypatch.setattr(reading, "GROUP_BYTES", budget)
        grouped = reading.read_table(f"{path}", in_groups=True)
        groups = reading.column_groups(grouped)
        if groups == ((0, 2), (2, 3)):
            break
        assert high - low > 1, groups
        if len(groups) == 1:
            high = budget
        else:
            low = budget
    assert reading.column_walks(grouped) == ((0, 3),)
    calls: "list[tuple[int, int, bool, bool]]" = []
    asked_as_written = profile._group_asked

    def counted(step, start, part, cells, describes, people=None):
        answer = asked_as_written(step, start, part, cells, describes, people)
        calls.append((start, len(cells), describes, answer is None))
        return answer

    monkeypatch.setattr(profile, "_group_asked", counted)
    asked = _asked_of(grouped, document, settings)
    monkeypatch.undo()
    return asked, calls


def test_a2_the_people_are_read_alike_whole_and_in_groups(tmp_path: pathlib.Path, monkeypatch) -> None:
    """The people's rule gives the same questions whole and in groups (Codex's review of lane ID-ROOM4, item 2).

    Each table the rule reads, its columns in several generated orders, is read whole and then one
    column a group with the walks cut at generated budgets (every column a walk; the person column
    and the key in one walk or two, either first), as a table too large to read whole is read; the
    first walk's questions must be the whole reading's, the second key's hold among them. Red on the
    version whose groups read only their own columns (a key beside a person column in another group
    is asked nothing and copied: 19,990 real keys at 20,000 rows).

    THE SECOND PASS OF A WALK (the scoped verify 2 of lane ID-ROOM4, item 1): a walk asks each of
    its groups without describing, and a group one of whose columns would be described is asked
    again alone (`profile._by_groups`). The key and the dates with stray codes in ONE group, the
    person column in another, ONE walk: the group budget is read off `reading.column_groups` until it
    cuts so, the key's group is seen asked again alone at this size, and the questions are the whole
    reading's. That table is read in its one order: the case costs 0.34 to 0.38 CPU seconds more
    (measured twice). Red on that second pass asked without the people (the verify's X1: the key is
    only listed, as a checklist entry, the class of Codex's item 2 above).
    """
    draw = random.Random(48921)
    settings = taxonomy.Settings(person_columns=("pid",))
    keys = {"second-key": {"pkey", "enc"}, "nines-bare": {"v"}, "second-pass": {"pkey"}}
    cuts = 0
    for which, (header, body) in sorted(_agreement_tables(2000, 1000).items()):
        for turn in range(1 if which == "second-pass" else 4):
            # The first order puts the person column last, after every key.
            order = list(range(1, len(header))) + [0]
            if turn:
                draw.shuffle(order)
            path = tables.write_table(
                tmp_path / f"{which}.csv", [header[place] for place in order],
                [[row[place] for place in order] for row in body],
            )
            whole = reading.read_table(f"{path}")
            document = profile.build_document(whole, settings, ["pid"], subjects=["pid"])
            expected = _asked_of(whole, document, settings)
            assert {name for name, reason, _words in expected if reason == asking.BECAUSE_EACH_ON_ONE_ROW} == keys[which]
            for budget in (1, draw.randint(2, path.stat().st_size), 1 << 40):
                monkeypatch.setattr(reading, "GROUP_BYTES", 1)
                monkeypatch.setattr(reading, "WALK_BYTES", budget)
                grouped = reading.read_table(f"{path}", in_groups=True)
                cuts += len(reading.column_walks(grouped)) > 1
                assert _asked_of(grouped, document, settings) == expected, (which, order, budget)
                monkeypatch.undo()
            if which == "second-pass":
                # The key and the dates in one group, the person column in the other, one walk.
                asked, calls = _asked_in_two_groups(path, document, settings, monkeypatch)
                # Asked within the walk, the key's group gave no answer; asked again alone, it did.
                assert (0, 2, False, True) in calls and (0, 2, True, False) in calls, calls
                assert asked == expected, calls
    assert cuts >= 8


def _fixed_per_person(draw: random.Random, people: int, low: float, high: float, logarithmic: bool, decimals: int) -> "tuple[list[str], list[str]]":
    """A measurement fixed per person, drawn over ``low`` to ``high``, ten rows a person."""
    persons: "list[str]" = []
    column: "list[str]" = []
    for person in range(people):
        value = 10 ** draw.uniform(math_log(low), math_log(high)) if logarithmic else draw.uniform(low, high)
        written = f"{value:.{decimals}f}" if decimals else f"{int(value)}"
        for _row in range(10):
            persons += [f"S{100000 + person}"]
            column += [written]
    return persons, column


def math_log(value: float) -> float:
    """The base-ten logarithm, for the log-uniform control."""
    import math

    return math.log10(value)


@pytest.mark.parametrize("people", [1000, 2000])
def test_a2_measurements_fixed_per_person_over_a_wide_range_are_asked_and_narrow_ones_are_not(people: int) -> None:
    """Skeptic 1 of lane ID-ROOM4, item 7 (accepted, LANE ID-ROOM4 RULINGS 4, item 7): the class the people arm asks.

    A number fixed per person and drawn over a range about fifty times the people or wider -- an
    income of 20,000 to 250,000, a weight in grams of 45,000 to 140,000 (at 1,000 people; at 2,000 it
    stands at arm (a)'s line), a cost in cents of 100,000 to 99,999,999 -- is almost unique to a
    person, the quasi-identifier the question exists for: the people arm reaches it ('nearly' or
    'different') where the rows arm does not, one question more for the person and no fidelity lost at
    table level. A log-uniform viral load, steps a day, platelets in thousands and a birth weight in
    grams are reached by neither. Red on the class moved either way.
    """
    draw = random.Random(48905 + people)
    reached_by_people: "dict[str, bool]" = {}
    reached_by_rows: "dict[str, bool]" = {}
    for name, low, high, logarithmic, decimals, role in (
        ("income", 20000, 250000, False, 0, taxonomy.ROLE_COUNT),
        ("grams", 45000, 140000, False, 0, taxonomy.ROLE_COUNT),
        ("cents", 100000, 99999999, False, 0, taxonomy.ROLE_COUNT),
        ("viral", 20, 10000000, True, 0, taxonomy.ROLE_COUNT),
        ("steps", 1000, 20000, False, 0, taxonomy.ROLE_COUNT),
        ("platelets", 150, 450, False, 0, taxonomy.ROLE_COUNT),
        ("birth_grams", 2500, 4500, False, 0, taxonomy.ROLE_COUNT),
    ):
        persons, column = _fixed_per_person(draw, people, low, high, logarithmic, decimals)
        settings = taxonomy.Settings(person_columns=("pid",))
        present, _absent = taxonomy.split_missing(column, settings)
        people_of = asking._people_of([{"name": "pid"}, {"name": "c"}], [persons, column], settings)
        holders = asking._holders_of(column, present, people_of, "c", settings)
        reached_by_people[name] = asking._each_on_one_person(present, holders, role, False, "c")
        reached_by_rows[name] = asking._whole_numbers_each_on_one_row(present, role, False, "c")
    # A range near fifty times the people stands at arm (a)'s line of one value in a hundred shared:
    # the weight in grams over 95,000 values is reached at 1,000 people and stands at the line at 2,000.
    expected = {
        "income": True, "grams": people == 1000, "cents": True,
        "viral": False, "steps": False, "platelets": False, "birth_grams": False,
    }
    assert {name: reached_by_people[name] for name in expected if name != "grams" or people == 1000} == {
        name: expected[name] for name in expected if name != "grams" or people == 1000
    }
    assert not any(reached_by_rows.values())


def test_a2_the_question_and_its_hold_follow_in_the_producer(a_table: reading.Table) -> None:
    """The key is put HX5's question with the people's words, offering `identifier`, and held until answered.

    A table of a person column and a second key on three rows a person, described and asked as
    `synthtwin profile` asks it with the person declared. Each answer is worded as it writes (skeptic
    1's item 8: the question offers keep, code and identifier). Red on the people arm removed (no
    question; the key is read as a number and published).
    """
    persons = [f"S{100000 + person}" for person in range(300) for _row in range(3)]
    second = [f"P{500000 + person}" for person in range(300) for _row in range(3)]
    read = _table(a_table, {"pid": persons, "pkey": second})
    settings = taxonomy.Settings(person_columns=("pid",))
    described = profile.build_document(read, settings, ["pid"], subjects=["pid"])
    asked, _split = asking.questions_and_splits_for(described, read.columns, settings, ["pid"])
    found = [question for question in asked if question.name == "pkey"]
    assert len(found) == 1 and found[0].reason == asking.BECAUSE_EACH_ON_ONE_ROW
    assert asking.on_one_persons_rows(found[0]) and asking.offers_identifier(found[0])
    assert "the rows of one person" in found[0].shape
    assert "inside the range the description publishes" in found[0].shape and "measurement" not in found[0].shape
    assert [choice.answer for choice in found[0].choices] == ["keep", "code", "identifier"]
    assert asking.unanswered_identities(asked, described) == ("pkey",)


def test_a2_only_its_own_answer_releases_the_key(a_table: reading.Table) -> None:
    """Skeptic 1 of lane ID-ROOM4, item 1 (LANE ID-ROOM4 RULINGS 4, item 1): the people's question is its own.

    A `keep` given to the person question (the zoo's truthful answer for a key beside its patient) or
    to any other question leaves the key held while its own question is put; a `keep` given to that
    question, in the file or kept from a round before (`asking.PEOPLE_KEY_KEPT_SAW`), releases it; the
    kept answer is written back with those words, so the next round reads it as that question's. Red
    on the mutant that passes the kept answers through unfiltered (19,990 real keys at 20,000 rows) and
    on the marker of the carried answer dropped (the key held again a round after its answer).
    """
    persons = [f"S{100000 + person}" for person in range(300) for _row in range(3)]
    second = [f"P{500000 + person}" for person in range(300) for _row in range(3)]
    read = _table(a_table, {"pid": persons, "pkey": second})
    settings = taxonomy.Settings(person_columns=("pid",))
    described = profile.build_document(read, settings, ["pid"], subjects=["pid"])
    asked, _split = asking.questions_and_splits_for(described, read.columns, settings, ["pid"])
    assert asking.kept_beside_own_questions(("pkey", "other"), asked, ()) == ("other",)
    assert asking.kept_beside_own_questions(("pkey", "other"), asked, ("pkey",)) == ("pkey", "other")
    assert asking.unanswered_identities(asked, described, asking.kept_beside_own_questions(("pkey",), asked, ())) == ("pkey",)
    # The file's two ways of saying `keep`: to the person question, and to the people's own question.
    own = [question for question in asked if question.name == "pkey"][0]
    entry = {
        "column": "pkey", "what_synthtwin_saw": own.shape, "read_as_now": "identifier", "your_answer": "keep",
        "answers_you_can_give": [{"answer": choice.answer, "means": choice.means} for choice in own.choices],
    }
    person = {
        "column": "pkey", "what_synthtwin_saw": "its values repeat", "read_as_now": "identifier", "your_answer": "keep",
        "answers_you_can_give": [
            {"answer": "keep", "means": "not a person"}, {"answer": "identifier", "means": "the people the rows are about"},
        ],
    }
    by_person = asking.answers_in({"asked": [person], "checklist": {"columns": []}}, "q.json")
    by_own = asking.answers_in({"asked": [entry], "checklist": {"columns": []}}, "q.json")
    assert by_person.identities_kept == ("pkey",) and by_person.people_keys_kept == ()
    assert by_own.identities_kept == ("pkey",) and by_own.people_keys_kept == ("pkey",)
    kept = asking.answered_before(asking.Given(columns=("pid", "pkey"), identities_kept=("pkey",), people_keys_kept=("pkey",)))
    assert kept[0]["what_synthtwin_saw"] == asking.PEOPLE_KEY_KEPT_SAW
    again = asking.answers_in({"asked": [], "checklist": {"columns": []}, asking.ANSWERED_BEFORE: kept}, "q.json")
    assert again.people_keys_kept == ("pkey",)


# -- the 20,000-row cases, kept to the writers' own tables ------------------------------------------


def test_the_driver_excuses_only_the_carries_exact_misses_and_needs_a_finished_validation(tmp_path: pathlib.Path) -> None:
    """K-HZ-39's driver reads its evidence exactly (Codex's review of lane ID-ROOM4, items 7 and 8; LANE ID-ROOM4 RULINGS 6 (7), (8)).

    A miss is excused only where its mode, column and fact are one of carry C2's eight or C2b's three:
    the same census facts on the person table's second key (1,000 keys twenty times each where 2,000
    ten times each are published) count, and so does a C2 fact on another column of C2's own mode. A
    validation that did not run to its end -- a handled refusal with no quality report -- is no evidence:
    the driver prints no KPI line. Red on the driver's old exception (any held column, any fact carrying
    a word of C2's) and on an absent report read as an empty list of misses.
    """
    carried = [[name, f"x {said}"] for mode, name, said in tables.C2_MISSES]
    assert tables.misses_outside_the_carries("codes-identifier", tables.CODES_UNREPRESENTABLE, carried) == 0
    census = [["pkey", "distinct.n_distinct [identifier.n_distinct]"],
              ["pkey", "distinct.n_distinct_by_occurrences [identifier.n_distinct_by_occurrences]"]]
    assert tables.misses_outside_the_carries("persons-declared", tables.KEY_COLUMNS, census) == 2
    assert tables.misses_outside_the_carries("codes-identifier", ("e5",), [["e5", "distinct.n_distinct [identifier.n_distinct]"]]) == 1
    assert tables.misses_outside_the_carries("persons-declared", tables.KEY_COLUMNS, [["hr", "x [universal.n_numeric]"]]) == 0
    with tables.nobody_at_the_keyboard():
        refused = cli.main(
            ["validate", f"{tmp_path / 'absent-profile.json'}", "--twin", f"{tmp_path / 'absent-twin.csv'}",
             "--out-dir", f"{tmp_path}"],
            small_tables_refused=False,
        )
    assert refused in (1, 2)
    seen = {"validated": refused, "misses": tables.missed_facts(tmp_path / "absent-twin-quality.txt")}
    assert seen["misses"] is None and not tables.validation_completed(seen)
    assert not tables.validation_completed({"validated": 0, "misses": None})
    assert tables.validation_completed({"validated": 3, "misses": [["e5", "x"]]})
    assert tables.validation_completed({"validated": 0, "misses": []})


def test_the_driver_reads_in_every_mode_columns_of_that_modes_own_table() -> None:
    """K-HZ-39's driver counts, in every mode, columns that mode's table holds (repair 2 of lane ID-ROOM4).

    Repair 2's reproduction modes begin `codes-` as the code table's do, and read by that prefix they
    were taken for the code table's columns: the driver's first run on repair 2's head stopped at the
    first of them (`KeyError`), measuring nothing. Each of the driver's modes (`--person`'s too) has its
    held columns read against its own table's header, and every reproduction mode holds a column. Red on
    the prefix read first.
    """
    for mode in tables.DRIVER_MODES + ("persons-person",):
        which = tables.MODES[mode][0]
        header, _body = tables.table_of(which, 2000)
        held = tables.held_in(mode)
        assert set(held) <= set(header), (mode, held, header)
    for mode, held in tables.REPAIRED_HELD.items():
        assert tables.held_in(mode) == held and held, mode


def test_a1_at_the_table_floor_the_code_table_writes_no_real_code(tmp_path: pathlib.Path) -> None:
    """The code table at 20,000 rows, unanswered, through profile, generate and validate: 0 real codes.

    Its slim form (`made_up_key_tables.SLIM`): every column the writer's grammar reaches keeps its
    block with NF139 and its twin, each cell one letter or figure longer than its longest value, writes
    0 twin cells equal to a real code exactly, case-folded or by merged key; validate exits 0 (the two
    lengths an AUTHORIZED-DEVIATION, nothing missed); nothing real stands in any file or on the screen;
    the questions file says why; e5seven (codes off the writer's start) and the decimal column keep
    their readings. The whole table in every mode is the driver's. Red on the dry run removed (20,000
    real codes in e5) and on step 8 removed.
    """
    seen = tables.run(tmp_path, "codes-slim-unanswered", 20000)
    assert seen["exits"] == [0, 0, 0]
    columns = seen["columns"]
    for name in ("e5", "E5", "e6", "neg", "paren"):
        assert columns[name]["role"] == taxonomy.ROLE_UNREPRESENTABLE, name
        assert columns[name]["equal"] == columns[name]["folded"] == columns[name]["merged"] == 0, name
    assert columns["e5seven"]["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert columns["numoor"]["role"] == taxonomy.ROLE_CONTINUOUS
    assert seen["real_in_files_and_screen"] == 0 and seen["misses"] == []
    questions = (tmp_path / "codes-slim-questions.json").read_text(encoding="utf-8")
    assert "made-up spellings" in questions and "one letter or figure longer" in questions
    described = json.loads((tmp_path / "codes-slim-profile.json").read_text(encoding="utf-8"))
    evidence = {block["name"]: block["detection_evidence"] for block in described["columns"]}
    assert all(evidence[name] == generation.SPELLED_WIDER_EVIDENCE for name in ("e5", "E5", "e6", "neg", "paren"))
    assert evidence["e5seven"] != generation.SPELLED_WIDER_EVIDENCE


def test_a1_at_the_table_floor_a_code_one_person_holds_is_written_apart_with_the_person_question_open(
    tmp_path: pathlib.Path,
) -> None:
    """Skeptic 1 of lane ID-ROOM4, item 2, at 20,000 rows and 1,000 people, nothing declared.

    One code a person in the writer's grammar, each on the twenty rows of ONE person, and one code for
    every three people: counted in the subjects the description is counted in (the person question
    open on the person key), both are written apart and their twins write 0 cells equal to a real
    code; validate exits 0; nothing real in any file. Red on the holders counted in rows (20,000 real
    codes) and on the subjects reduced to the declared person columns.
    """
    seen = tables.run(tmp_path, "people-codes-unanswered", 20000)
    assert seen["exits"] == [0, 0, 0]
    columns = seen["columns"]
    for name in ("code", "code3"):
        assert columns[name]["role"] == taxonomy.ROLE_UNREPRESENTABLE, name
        assert columns[name]["equal"] == columns[name]["folded"] == columns[name]["merged"] == 0, name
    assert seen["real_in_files_and_screen"] == 0 and seen["misses"] == []


def test_a2_at_the_table_floor_the_peoples_own_question_holds_until_it_is_answered(tmp_path: pathlib.Path) -> None:
    """The person table at 20,000 rows and 2,000 people in the four modes of skeptic 1's item 1 (its slim form).

    Nothing declared; the person question answered as the zoo answers it (the person key `identifier`,
    the second keys `keep`); the people's own question then answered `identifier`: 0 twin cells equal
    to a real key in each. That question answered `keep` releases them, as RULING D5 says: the twin then
    draws inside the published range (19,990, 19,999 and 19,990 cells measured). Nothing real stands in
    any file or on the screen. Red on the mutant that lets the person question's `keep` release the keys
    and on the held key joined to the person columns.
    """
    seen = tables.run_own_question(tmp_path, 20000)
    for mode in ("nothing", "person-keep", "own-identifier"):
        run = seen[mode]
        assert run["exits"] == [0, 0], mode
        for name in tables.SECOND_KEYS:
            counted = run["columns"][name]
            assert counted["role"] == taxonomy.ROLE_IDENTIFIER, (mode, name)
            assert counted["equal"] == counted["folded"] == counted["merged"] == 0, (mode, name)
    # The held keys are no person columns: the people stay counted by the person key alone (red on the
    # held key joined to the person columns). Answered `identifier`, a key that repeats is a declared
    # identifier and counts people as P4-D340 has it (lane EZ-a's `--person` settles which one names them).
    assert seen["person-keep"]["person_columns"] == ["pid"]
    # ...and the file names the held reading for each key's own question (skeptic 1's item 1 (4)).
    assert seen["own_read_as_now"] == {name: "identifier" for name in tables.SECOND_KEYS}
    released = seen["own-keep"]["columns"]
    assert all(released[name]["role"] == taxonomy.ROLE_AFFIXED for name in tables.SECOND_KEYS)
    assert [released[name]["equal"] for name in tables.SECOND_KEYS] == [19990, 19999, 19990]
    assert seen["real_in_files_and_screen"] == 0
