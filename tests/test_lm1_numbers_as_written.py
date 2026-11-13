"""P4-D475 (lane LM1): numbers written as the source wrote them -- a label's bound, and the return of magnitudes.

THE DEFECT, measured at the owner's table floor of 20,000 rows on the
base 820d55c3 with the commands a person types (the zoo's run_table:
profile, the answers rounds, generate seed 0, validate): a column of
numbers beside the label `<20` (`hiv_rna`: `TND`, `<20` and loads of 20
or more) wrote 72 loads below 20 on its low tail (`3` on 12 cells), a
form the real never writes, because the tail ran past the bound the
label sets.

THE RULE. A label of a column of numbers and labels that names a bound
-- `<20`, `<=0.5`, `>1000000`, `>=90`, `90+` -- bounds the numbers beside
it: the fitted tail end the description withholds is drawn inside the
bound (`contract.label_bounds`, method G5.3b). The bound is moved inward
onto the grid the numbers are written on, so `<20.5` beside whole
numbers holds them at 21 and no `20` is written, and the label is read
in the column's decimal grammar, so `<0,5` bounds a decimal-comma column
(Codex's review of the lane, items 8 and 9).

THE WITHDRAWAL (LANE LM1 RULINGS 5). The exponent form and census of a
column of magnitudes the lane built were reviewed and withdrawn, and
columns of magnitudes past a double's range write as the base did. The
gate PROVES THE RETURN against digests computed on 820d55c3: a generated
sweep of such columns (every repetition pattern, exponents beside and
across a double's edge, signs, widths, declared missing spellings), the
codes written like `4E0815` left blank and answered `measurement`, and
the zoo's `instrument_magnitudes` at the table floor through the shipped
command. The class check over every role that publishes nothing stays.

THE GATE: unit cases and generated cases at the library's small path,
each rule red on its mutant, and two cases at 20,000 rows, one a writer:
the zoo's magnitudes through the shipped command, and Codex's column
beside `<20.5` through the library.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import contract, generation, parsing, profile, reading, rendering, taxonomy, validation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fixtures  # noqa: E402
import health_zoo  # noqa: E402

SETTINGS = taxonomy.Settings()
SEED = 0


def _document(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", settings: taxonomy.Settings = SETTINGS, **options: object
) -> "dict":
    path = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, rows))
    return profile.build_document(reading.read_table(str(path)), settings, ["sample_id"], **options)  # type: ignore[arg-type]


def _loaded(folder: pathlib.Path, document: "dict") -> contract.Profile:
    written = fixtures.write_profile(folder, "t-profile.json", document)
    return contract.load_profile(str(written))


def _block(document: "dict", name: str) -> "dict":
    return next(column for column in document["columns"] if column["name"] == name)


def _twin(described: contract.Profile) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(rendering.twin_csv(generation.generate(described, SEED)))))
    return {rows[0][place]: [row[place] for row in rows[1:]] for place in range(len(rows[0]))}


def _measured(folder: pathlib.Path, described: contract.Profile, cells: "dict[str, list[str]]") -> validation.Outcome:
    header = list(cells)
    rows = [[cells[name][row] for name in header] for row in range(len(cells[header[0]]))]
    path = fixtures.write(folder, "twin.csv", fixtures.rows_to_csv(header, rows))
    return validation.measure(described, str(path))


def _facts(described: contract.Profile, name: str) -> contract.CompoundFacts:
    facts = next(column for column in described.columns if column.name == name).facts
    assert isinstance(facts, contract.CompoundFacts), type(facts).__name__
    return facts


def _numbers_in(cells: "list[str]", decimal_comma: bool = False) -> "list[float]":
    found = []
    for cell in cells:
        value = parsing.parse_number(parsing.written_with_a_decimal_comma(cell) if decimal_comma else cell)
        if value is not None:
            found += [value]
    return found


# -- a label that names a bound bounds the numbers beside it --------------------


@pytest.mark.parametrize(
    "spelling, expected",
    [
        ("<20", ("low", 20.0, False)), ("< 20", ("low", 20.0, False)), ("<=0.5", ("low", 0.5, True)),
        (">1000000", ("high", 1000000.0, False)), (">=90", ("high", 90.0, True)), ("90+", ("high", 90.0, True)),
        ("TND", None), ("+", None), ("<", None), ("<abc", None), ("NEG", None),
    ],
)
def test_a_label_names_its_bound(spelling: str, expected: object) -> None:
    """The five spellings of a bound, and labels that name none."""
    assert contract._bound_of_label(spelling, False) == expected


def test_a_generated_sweep_of_bound_labels_reads_each_bound() -> None:
    """5,000 generated labels: each of the five spellings of a bound, with and without a space, at whole and decimal numbers, in either decimal grammar; a word or a figure-free label names none."""
    draw = random.Random(4750)
    for _each in range(5_000):
        value = draw.randint(0, 100_000) / (10 ** draw.randint(0, 3))
        number = f"{value:g}"
        comma = draw.random() < 0.3
        written = number.replace(".", ",") if comma else number
        kind = draw.randrange(6)
        space = " " if draw.random() < 0.3 else ""
        if kind == 0:
            assert contract._bound_of_label(f"<{space}{written}", comma) == ("low", float(number), False)
        elif kind == 1:
            assert contract._bound_of_label(f"<={space}{written}", comma) == ("low", float(number), True)
        elif kind == 2:
            assert contract._bound_of_label(f">{space}{written}", comma) == ("high", float(number), False)
        elif kind == 3:
            assert contract._bound_of_label(f">={space}{written}", comma) == ("high", float(number), True)
        elif kind == 4:
            assert contract._bound_of_label(f"{written}+", comma) == ("high", float(number), True)
        else:
            word = "".join(draw.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _letter in range(draw.randint(1, 6)))
            assert contract._bound_of_label(draw.choice((word, f"<{word}", f"{word}+", f">={word}")), comma) is None


def test_a_label_is_read_in_its_columns_decimal_grammar() -> None:
    """Codex's item 9 at the unit level: `<0,5` names 0.5 on a decimal-comma column and nothing on a column of points."""
    assert contract._bound_of_label("<0,5", True) == ("low", 0.5, False)
    assert contract._bound_of_label("<=1.234,5", True) == ("low", 1234.5, True)
    assert contract._bound_of_label("<0,5", False) is None
    assert contract._bound_of_label("<0.5", False) == ("low", 0.5, False)


@pytest.mark.parametrize(
    "value, low, strict, figures, expected",
    [
        (20.5, True, False, -2, 21.0), (20.0, True, False, -2, 20.0), (20.0, True, True, -2, 21.0),
        (0.5, True, True, 2, 0.51), (0.505, True, False, 2, 0.51), (0.505, True, True, 2, 0.51),
        (90.0, False, True, -2, 89.0), (90.0, False, True, 1, 89.9), (89.95, False, True, 1, 89.9),
        (1000000.5, False, False, -2, 1000000.0), (20.5, True, False, -1, 20.5), (0.5, True, True, -1, None),
    ],
)
def test_a_bound_moves_inward_onto_the_grid_its_numbers_are_written_on(
    value: float, low: bool, strict: bool, figures: int, expected: object
) -> None:
    """Codex's item 8 at the unit level: a bound between two grid points goes to the inner one, a strict one a step further inside."""
    assert contract._on_the_label_grid(value, low, strict, figures) == expected


def test_a_generated_sweep_of_bounds_lands_inside_on_the_grid() -> None:
    """5,000 generated bounds on grids of 0 to 4 places: each lands on the grid, on the bound's own side, within one step of it."""
    draw = random.Random(4756)
    for _each in range(5_000):
        figures = draw.choice((-2, 0, 1, 2, 3, 4))
        places = 0 if figures == -2 else figures
        value = draw.randint(0, 10_000_000) / (10 ** draw.randint(0, 6))
        low = draw.random() < 0.5
        strict = draw.random() < 0.5
        placed = contract._on_the_label_grid(value, low, strict, figures)
        assert placed is not None
        step = 10.0 ** -places
        scaled = placed / step
        assert abs(scaled - round(scaled)) < 1e-3, (value, figures, placed)
        slack = step * 1e-9 + abs(value) * 1e-12
        if low:
            assert placed > value - slack and (placed > value + slack or not strict), (value, strict, figures, placed)
            assert placed <= value + step + slack, (value, strict, figures, placed)
        else:
            assert placed < value + slack and (placed < value - slack or not strict), (value, strict, figures, placed)
            assert placed >= value - step - slack, (value, strict, figures, placed)


def _loads(n: int, seed: int, label: str = "<20", least: int = 20) -> "list[list[str]]":
    """A result field: `TND`, ``label``, or a load of ``least`` or more drawn from a long tail."""
    draw = random.Random(seed)
    rows = []
    for index in range(n):
        roll = draw.random()
        load = "TND" if roll < 0.35 else label if roll < 0.5 else f"{min(10_000_000, least + int(draw.lognormvariate(8.0, 2.0)))}"
        rows += [[f"S{100000 + index}", load]]
    return rows


def _below(cells: "list[str]", bound: float) -> int:
    return sum(1 for value in _numbers_in(cells) if value < bound)


def test_the_numbers_beside_a_lower_bound_stay_at_it_or_above(tmp_path: pathlib.Path) -> None:
    """`<20` beside the loads: the twin's low tail is drawn from 20 up, its published facts still met."""
    rows = _loads(4000, 21)
    document = _document(tmp_path, ["sample_id", "load"], rows)
    block = _block(document, "load")
    assert block["role"] == "numbers_with_labels"
    described = _loaded(tmp_path, document)
    assert _facts(described, "load").numbers.label_bounds == (20.0, None)
    twin = _twin(described)
    assert _below(twin["load"], 20.0) == 0
    outcome = _measured(tmp_path, described, twin)
    missed = [check for check in outcome.checks if check.verdict == validation.MISSED and check.column == "load"]
    assert not missed, [(check.fact, check.subcheck) for check in missed]


def test_mutant_without_the_bound_the_tail_runs_past_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RED ON ITS MUTANT: with no bound read, the derived end stands below 20 and the twin writes loads under it."""
    monkeypatch.setattr(contract, "label_bounds", lambda *arguments: (None, None))
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "load"], _loads(4000, 21)))
    assert _below(_twin(described)["load"], 20.0) > 0


def test_the_numbers_beside_a_bound_between_grid_points_stay_inside_it(tmp_path: pathlib.Path) -> None:
    """Codex's item 8 at the table floor, the compound writer's one 20,000-row case: `<20.5` beside whole numbers of 21 and more holds them at 21, and the twin writes no `20`.

    Red on the code before the move (repair 1's head 5f03c2db), which
    held the end at 20.5 and wrote it `20` on 11 cells, and on the mutant
    that keeps a bound between grid points as it stands (the case below).
    """
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "load"], _loads(20000, 21, "<20.5", 21)))
    assert _facts(described, "load").numbers.label_bounds == (21.0, None)
    assert _below(_twin(described)["load"], 20.5) == 0


def test_mutant_a_bound_kept_between_grid_points_is_written_outside_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED ON ITS MUTANT: the bound kept at 20.5 is spelled `20` by the whole-number writer."""
    monkeypatch.setattr(contract, "_on_the_label_grid", lambda value, low, strict, figures: value + 1.0 if strict else value)
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "load"], _loads(4000, 21, "<20.5", 21)))
    assert _facts(described, "load").numbers.label_bounds == (20.5, None)
    assert _below(_twin(described)["load"], 20.5) > 0


def _comma_levels(n: int, seed: int) -> "list[list[str]]":
    """A declared decimal-comma column: `<0,5`, a thin low tail from 0,51 and a bulk from 1,5, two decimals."""
    draw = random.Random(seed)
    rows = []
    for index in range(n):
        roll = draw.random()
        if roll < 0.15:
            cell = "<0,5"
        elif roll < 0.152:
            cell = f"{draw.uniform(0.51, 0.9):.2f}".replace(".", ",")
        else:
            cell = f"{draw.uniform(1.5, 20.0):.2f}".replace(".", ",")
        rows += [[f"S{100000 + index}", cell]]
    return rows


def test_the_numbers_beside_a_decimal_comma_bound_stay_at_it_or_above(tmp_path: pathlib.Path) -> None:
    """Codex's item 9: `<0,5` on a declared decimal-comma column bounds its numbers at 0,5; no twin number under it.

    Red on the code before the grammar was forwarded (repair 1's head
    5f03c2db): no bound was read, and the twin wrote `0,29`.
    """
    described = _loaded(
        tmp_path, _document(tmp_path, ["sample_id", "level"], _comma_levels(4000, 9), forced_decimal_commas=["level"])
    )
    assert _facts(described, "level").numbers.label_bounds == (0.5, None)
    made = _numbers_in(_twin(described)["level"], decimal_comma=True)
    assert made and min(made) >= 0.5, min(made)


def test_a_label_the_published_numbers_cross_names_no_bound(tmp_path: pathlib.Path) -> None:
    """Grades `1+` to `4+` beside readings up to 300 name no bound: the published rungs stand past it."""
    draw = random.Random(31)
    rows = [
        [f"S{index}", draw.choice(("1+", "2+", "3+", "4+")) if draw.random() < 0.3 else f"{draw.randint(5, 300)}"]
        for index in range(2000)
    ]
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "protein"], rows))
    facts = next(column for column in described.columns if column.name == "protein").facts
    if isinstance(facts, contract.CompoundFacts):
        assert facts.numbers.label_bounds == (None, None)


def _ages(n: int, seed: int, label: str) -> "list[list[str]]":
    """Ages to one decimal, a normal bulk clipped below 90, every age of 90 or more written as ``label``."""
    draw = random.Random(seed)
    rows = []
    for index in range(n):
        age = draw.gauss(62.0, 13.0)
        rows += [[f"S{100000 + index}", label if age >= 90.0 else f"{max(age, 18.0):.1f}"]]
    return rows


@pytest.mark.parametrize("label", ["90+", ">=90"])
def test_the_numbers_beside_a_top_code_label_stay_below_it(tmp_path: pathlib.Path, label: str) -> None:
    """The high side of a label's bound, strict: ages beside `90+` or `>=90` bound at 89.9, no twin number of 90 or more.

    Red on the mutant that returns the derived end past the high bound
    (skeptic 1's M3) and on the one that reads a strict high bound as met
    at it, `90.0` written beside `90+` (M4).
    """
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "age_reading"], _ages(4000, 7, label)))
    bounds = _facts(described, "age_reading").numbers.label_bounds
    assert bounds[1] is not None and bounds[1] < 90.0, bounds
    made = _numbers_in(_twin(described)["age_reading"])
    assert made and max(made) < 90.0, max(made)


def _mostly_whole_ages(n: int, seed: int) -> "list[list[str]]":
    """Ages beside `90+`, seven in ten written whole and three to one decimal, so the forms map asks for point-free cells."""
    draw = random.Random(seed)
    rows = []
    for index in range(n):
        age = draw.gauss(70.0, 11.0)
        if age >= 90.0:
            cell = "90+"
        elif draw.random() < 0.3:
            cell = f"{max(age, 18.0):.1f}"
        else:
            cell = f"{int(max(age, 18.0))}"
        rows += [[f"S{100000 + index}", cell]]
    return rows


def test_a_bound_moves_onto_the_grid_the_end_is_placed_on(tmp_path: pathlib.Path) -> None:
    """Where the forms map asks for point-free cells (method G5.3b step 4) the end stands on the whole numbers, and the bound goes there too.

    Ages written mostly whole beside `90+`: the half's own grid is tenths,
    so the bound reads 89.9, but step 4 places the end on the whole
    numbers, and the bound moved onto that grid holds it at 89, a whole
    number, as step 4 asks. Red on the mutant that moves the bound onto
    the half's own grid alone (I8b), whose twin ends at 89.9.
    """
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "age_reading"], _mostly_whole_ages(4000, 1)))
    facts = _facts(described, "age_reading")
    assert facts.numbers.label_bounds == (None, 89.9), facts.numbers.label_bounds
    assert contract._point_free_demand(facts.numbers) > contract._pointed_demand(facts.numbers)
    made = _numbers_in(_twin(described)["age_reading"])
    assert made and max(made) == 89.0, max(made)


def _small_fractions(n: int, seed: int) -> "list[list[str]]":
    """Numbers to two decimals above 0.5, a thin low tail from 0.51, beside the label `<=0.5`."""
    draw = random.Random(seed)
    rows = []
    for index in range(n):
        roll = draw.random()
        if roll < 0.15:
            cell = "<=0.5"
        elif roll < 0.152:
            cell = f"{draw.uniform(0.51, 0.9):.2f}"
        else:
            cell = f"{draw.uniform(1.5, 20.0):.2f}"
        rows += [[f"S{100000 + index}", cell]]
    return rows


def test_the_numbers_beside_a_strict_lower_bound_stay_above_it(tmp_path: pathlib.Path) -> None:
    """The low side, strict: `<=0.5` bounds the numbers at 0.51, a step of the published width inside, no twin number at 0.5 or less.

    Red on the mutant that reads a strict low bound as met at it (M5):
    its twin writes `0.5` beside `<=0.5`.
    """
    described = _loaded(tmp_path, _document(tmp_path, ["sample_id", "level"], _small_fractions(4000, 17)))
    assert _facts(described, "level").numbers.label_bounds == (0.51, None)
    made = _numbers_in(_twin(described)["level"])
    assert made and min(made) > 0.5, min(made)


def test_a_label_whose_bound_the_tail_crosses_names_no_bound(tmp_path: pathlib.Path) -> None:
    """`<20` beside loads whose low tail reaches below 20: the published reach crosses the bound, so no side is kept.

    Red on the mutant without the tail-reach check (M7), which keeps the
    bound and holds the derived end at 20 against a tail the description
    says lies below it.
    """
    draw = random.Random(23)
    rows = []
    for index in range(4000):
        roll = draw.random()
        if roll < 0.2:
            cell = "<20"
        elif roll < 0.204:
            cell = f"{draw.randint(2, 12)}"
        else:
            cell = f"{draw.randint(40, 900)}"
        rows += [[f"S{100000 + index}", cell]]
    facts = _facts(_loaded(tmp_path, _document(tmp_path, ["sample_id", "load"], rows)), "load")
    assert facts.numbers.tails is not None and facts.numbers.tails.low is not None
    assert facts.numbers.label_bounds[0] is None, facts.numbers.label_bounds


def test_k_hz_28_counts_the_numbers_past_a_labels_bound() -> None:
    """K-HZ-28 sees the defect it is listed for (skeptic 1 item 9, the statistics check item 3).

    A twin `12` beside `<20` wears the form of a real `40`, and a twin `91`
    beside `90+` that of a real `89`, so a count of forms alone read 0
    for both; with the column's bound each is counted, once. Red on the
    mutant that counts forms alone.
    """
    loads = ["TND", "<20", "40", "125", "2500"]
    assert health_zoo.numbers_written_differently(loads, ["12", "40", "<20", "3"], ("at least", 20.0)) == 2
    assert health_zoo.numbers_written_differently(loads, ["12", "40", "<20", "3"]) == 1
    ages = ["45", "89", "90+", "67"]
    assert health_zoo.numbers_written_differently(ages, ["91", "88", "90+", "90"], ("below", 90.0)) == 2
    assert health_zoo.numbers_written_differently(ages, ["91", "88", "90+", "90"]) == 0


# -- the class of roles that publish nothing (LANE LM1 RULINGS 2 (2), 5 (2)) ----------


def _figure_runs(text: str) -> "set[str]":
    """Every run of figures in ``text`` of four figures or more once its leading noughts are taken off."""
    runs: "set[str]" = set()
    current = ""
    for character in text + " ":
        if "0" <= character <= "9":
            current += character
            continue
        stripped = current.lstrip("0")
        if len(stripped) >= 4:
            runs.add(stripped)
        current = ""
    return runs


def _nothing_publishing_cells(draw: random.Random, role: str) -> "tuple[list[str], bool]":
    """600 generated cells that reach ``role``, every run of figures in them of four figures or more."""
    if role == taxonomy.ROLE_UNREPRESENTABLE:
        places = draw.randint(0, 3)
        marker = draw.choice(("E", "e"))
        plus = "+" if draw.random() < 0.5 else ""
        pool = []
        for _each in range(draw.randint(10, 40)):
            sign = "-" if draw.random() < 0.2 else ""
            tail = "".join(f"{draw.randint(0, 9)}" for _figure in range(places))
            body = f"{draw.randint(1, 9)}" + (f".{tail}" if places else "")
            pool += [f"{sign}{body}{marker}{plus}{draw.randint(1000, 9999)}"]
        return [pool[index % len(pool)] for index in range(600)], False
    if role == taxonomy.ROLE_IDENTIFIER:
        prefix = draw.choice(("REC", "P", "ACC-", ""))
        return [f"{prefix}{draw.randint(1000000, 9999999)}" for _each in range(600)], True
    words = ("seen", "again", "noted", "stable", "reviewed", "plan")
    return [
        " ".join(draw.choice(words) for _word in range(draw.randint(2, 6))) + f" {draw.randint(100000, 9999999)}"
        for _each in range(600)
    ], False


def test_a_role_publishing_nothing_publishes_no_figures_of_its_cells() -> None:
    """GENERATED over every role of `ROLES_PUBLISHING_NOTHING` and every key its blocks carry.

    LANE LM1 RULINGS 2 (2) and 5 (2): a role stays in the class only if
    every key the contract lets its block carry (`contract._role_keys`) and
    every key a generated block of it carries is one the publication class
    keeps (`KEYS_THAT_CARRY_NO_VALUE`), and no such key carries the
    figures of a cell. 90 generated columns, each of 600 cells whose runs
    of figures are four figures or more, so no count of the block can be
    one. The literal prefix of every cell (`layout_prefixes`) is the
    owner's ruling of 2026-09-17 and is not asked here. Red on 9629b831
    and on repair 1's head 5f03c2db, where the census of the exponents a
    column of magnitudes writes reached the role's blocks: the four
    figures after the `E` of every code (lane LM1's withdrawn census).
    """
    for role in taxonomy.ROLES_PUBLISHING_NOTHING:
        for key in contract._role_keys(role):
            assert key in taxonomy.KEYS_THAT_CARRY_NO_VALUE, (role, key)
    draw = random.Random(4752)
    reached: "dict[str, int]" = {role: 0 for role in taxonomy.ROLES_PUBLISHING_NOTHING}
    for case in range(90):
        role = sorted(taxonomy.ROLES_PUBLISHING_NOTHING)[case % len(taxonomy.ROLES_PUBLISHING_NOTHING)]
        cells, forced = _nothing_publishing_cells(draw, role)
        described = taxonomy.profile_column("column", 1, cells, len(cells), SETTINGS, forced)
        if described.role != role:
            continue
        reached[role] += 1
        block = profile._column_block(described)
        real: "set[str]" = set()
        for cell in set(cells):
            real |= _figure_runs(cell)
        for key in described.details:
            assert key in taxonomy.KEYS_THAT_CARRY_NO_VALUE, (role, key)
            if key == "layout_prefixes":
                continue
            found = _figure_runs(json.dumps(block[key], sort_keys=True)) & real
            assert not found, (role, key, sorted(found)[:3])
    assert all(reached[role] >= 20 for role in reached), reached


# -- the return: magnitudes past a double's range write as the base did -------------

# The sweep's own digests, computed on 820d55c3 (the lane's base) by this
# file's `_sweep_digests` with nothing else changed, each over one table's
# 40 columns of magnitudes: every column's description block, its twin
# cells at seed 0 and the verdicts validate gives it.
_BASE_SWEEP_DIGESTS = (
    "02cec1f8a790e93e40c583433947bf1798af8a0687a8995cbe51654b8d54109a",
    "5404f45ac54a1dc298f911c93c2f05c171c85e26852ac43f21ce97865860c18a",
    "aba08a8f9d51462c70d2f05d07ec2d012d4fcd46c5b46fb268b9bceea2d34014",
    "c45f5903dfa466b78affce91fa1d75491b64e2391d5b3d40e09517eba29f2902",
    "25c4839c03318e996fa723aa2b6e19a8bd9c7a70a35d343276dbf577dadff8e5",
    "37af9e62d78c181cf79ab198e923f47b33817cd60bc915205f4fc689e83152aa",
    "ddac01e2cd3c2d9f0dbd29fdefca8c4aca1d571655c94054ed618f6dc4a7b5bb",
    "c8ac7731532196d81ffdd219c29c836fcf37c83efe89aa30563915978d4367eb",
    "a1c70970e7234429da712ac090e0c3ef704a026bc388ff845bb5b46e241e6375",
    "2aa7c3b51a66c6e0e6e9392b4889afa7d2163cdb1db804113c14fa208c9e31a3",
)

# ...and the codes written like `4E0815`, left blank and answered
# `measurement`, computed the same way on 820d55c3.
_BASE_CODE_DIGESTS = (
    "6b3410e7cc363c0f0b034eb416324c06b2ccc421d33d7960f053655022ae693d",
    "6b3410e7cc363c0f0b034eb416324c06b2ccc421d33d7960f053655022ae693d",
)

# ...and the files the zoo's `instrument_magnitudes` writes at 20,000 rows
# through the shipped command (its run_table), each file's own digest.
# Every file is 820d55c3's but the description written before any answer,
# whose digest is the merged line's (batch 4s, step 7): lane CZ-A2's
# reading keeps a run of figures glued to a withheld label off the real
# runs by its opening (plan P4-D469), so the held `sample_id` keeps its
# six figures off the real `S500000` to `S519999` by `Z9%%%%%` where
# 820d55c3 wrote `Z%%%%%%`, ONE value of that file. Measured at this
# size: a twin generated from that description wrote 444 of 20,000 cells
# holding the six figures of a real `sample_id` (`Z512345` beside the real
# `S512345`) on 820d55c3's reading and none on the merged line's; no twin
# cell equals a real one either way, and the answered description, the
# questions file and the twin are 820d55c3's byte for byte.
_BASE_ZOO_DIGESTS: "dict[str, str]" = {
    "instrument_magnitudes-profile-unanswered.json": "863aed59954ecf79562e58f5d1d26acbb7a6bd9acd0dc9b72116f36e9f71a4ef",
    "instrument_magnitudes-profile.json": "ddbd93a698ea68a52b0531d3c6e542f16e76134e2be5c83abdefd1c8f9df7bc7",
    "instrument_magnitudes-profile.txt": "a5a7b7f7af7a7f21d3b8d8539837e7266a2ff77438aaef7fec6dfa13c0a90be3",
    "instrument_magnitudes-questions.json": "d7a1949b70aa1178ccd129c8fefc6c803e412db8502be45163e41daca9c4498b",
    "instrument_magnitudes-twin-quality.txt": "691689f07c8b7d6f36d3fd31daef417947679bd3993e0f5a02227401a591913b",
    "instrument_magnitudes-twin-report.txt": "45031e95f5befbc51856c35e470047bece8eddaca8c8dfb936ac1b21d66a57b4",
    "instrument_magnitudes-twin.csv": "4b07194be4e289e1e43e185652fd99ef4d709924280542b3768ac610d9e44846",
    "instrument_magnitudes.csv": "eb09775694e5497e6e7da9c656c3f6b3fe18b8051bd2f9cacb23625df0fd067e",
}

_SWEEP_TABLES = 10
_SWEEP_COLUMNS = 40
_SWEEP_ROWS = 300


def _spelled(draw: random.Random, shape: "dict[str, object]", exponent: int, negative: bool) -> str:
    places = int(f"{shape['places']}")
    tail = "".join(draw.choice("0123456789") for _figure in range(places))
    body = f"{draw.randint(1, 9)}" + (f".{tail}" if places else "")
    power = f"{abs(exponent)}".rjust(int(f"{shape['width']}"), "0")
    mark = "-" if exponent < 0 else ("+" if shape["plus"] else "")
    return ("-" if negative else "") + body + f"{shape['marker']}" + mark + power


def _magnitude_column(draw: random.Random, missing: str) -> "list[str]":
    """One generated column of magnitudes: its figures, marker, plus, exponent width, side of the range, spread, repetition and signs drawn."""
    shape: "dict[str, object]" = {
        "places": draw.choice((0, 1, 2, 3, 3, 4, 6)),
        "marker": draw.choice(("E", "E", "e")),
        "plus": draw.random() < 0.75,
        "width": draw.choice((3, 3, 3, 4)),
    }
    side = draw.choice(("big", "big", "small", "edge_big", "edge_small", "wide"))
    spread = draw.choice((1, 3, 8, 20, 60))
    repeats = draw.choice(("distinct", "distinct", "zipf", "few"))
    signs = draw.random() < 0.3
    centre = draw.randint(312, 400) if side in ("big", "edge_big") else (
        -draw.randint(330, 400) if side in ("small", "edge_small") else draw.randint(330, 900)
    )
    holdable = draw.choice((0, 3, 15)) if side.startswith("edge") else 0

    def one(exponent: int) -> str:
        return _spelled(draw, shape, exponent, signs and draw.random() < 0.3)

    def exponent() -> int:
        drawn = int(round(draw.gauss(centre, spread)))
        return max(drawn, 309) if centre > 0 else min(drawn, -325)

    if repeats == "distinct":
        cells = [one(exponent()) for _cell in range(_SWEEP_ROWS - holdable)]
    else:
        size = 12 if repeats == "few" else 120
        pool = [one(exponent()) for _value in range(size)]
        weights = [1.0 / (rank + 1) ** (1.3 if repeats == "zipf" else 0.2) for rank in range(size)]
        cells = draw.choices(pool, weights, k=_SWEEP_ROWS - holdable)
    cells += [one(draw.randint(295, 308) if centre > 0 else -draw.randint(290, 307)) for _cell in range(holdable)]
    draw.shuffle(cells)
    if missing and draw.random() < 0.5:
        for place in draw.sample(range(_SWEEP_ROWS), draw.choice((3, 12, 30))):
            cells[place] = missing
    return cells


def _table_digest(document: "dict", described: contract.Profile, twin: "dict[str, list[str]]", outcome: validation.Outcome) -> str:
    """One table's columns of magnitudes: each block as published, its twin cells and validate's verdicts, in order."""
    parts: "list[str]" = []
    for block in document["columns"]:
        name = f"{block['name']}"
        if name == "sample_id":
            continue
        verdicts = sorted((f"{check.fact}", f"{check.subcheck}", f"{check.verdict}") for check in outcome.checks if check.column == name)
        parts += [json.dumps(block, sort_keys=True), "\n".join(twin[name]), json.dumps(verdicts)]
    return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()


def _run_through_the_library(
    folder: pathlib.Path, header: "list[str]", columns: "list[list[str]]", settings: taxonomy.Settings, **options: object
) -> "tuple[dict, contract.Profile, dict[str, list[str]], validation.Outcome]":
    rows = [[f"S{100000 + row}"] + [column[row] for column in columns] for row in range(len(columns[0]))]
    document = _document(folder, ["sample_id"] + header, rows, settings, **options)
    described = _loaded(folder, document)
    twin = _twin(described)
    return document, described, twin, _measured(folder, described, twin)


def _sweep_digests(folder: pathlib.Path) -> "tuple[str, ...]":
    """The generated sweep: 10 tables of 40 columns of magnitudes, 300 rows each, a declared missing spelling on some."""
    draw = random.Random(4757)
    found: "list[str]" = []
    for table in range(_SWEEP_TABLES):
        missing = ("", "NOT DONE", "1.00E+350", "", "-999", "", "N/A", "1e999", "", "NOT DONE")[table]
        settings = taxonomy.Settings(declared_missing_values=(missing,)) if missing else SETTINGS
        columns = [_magnitude_column(draw, missing) for _column in range(_SWEEP_COLUMNS)]
        header = [f"m{place:02d}" for place in range(_SWEEP_COLUMNS)]
        here = folder / f"sweep{table}"
        here.mkdir()
        document, described, twin, outcome = _run_through_the_library(here, header, columns, settings)
        found += [_table_digest(document, described, twin, outcome)]
    return tuple(found)


def _code_columns() -> "tuple[list[str], list[list[str]], set[str]]":
    """The codes the verify of repair 1 measured: `4E0815` ten rows a code, with a plus, a sign before, a sign in the exponent, and `4.1E0815` one a row."""
    count = 600
    columns = [
        [f"{1 + (row // 10) % 9}E{815 + row // 90:04d}" for row in range(count)],
        [f"{1 + (row // 10) % 9}E+{815 + row // 90:04d}" for row in range(count)],
        [f"-{1 + (row // 10) % 9}E{815 + row // 90:04d}" for row in range(count)],
        [f"{1 + (row // 10) % 9}E-{815 + row // 90:04d}" for row in range(count)],
        [f"{1 + row % 9}.{(row // 9) % 10}E{815 + row // 90:04d}" for row in range(count)],
    ]
    real: "set[str]" = set()
    for column in columns:
        real |= set(column)
    return ["code_e", "code_plus", "code_signed", "code_small", "code_point"], columns, real


def _code_digests(folder: pathlib.Path) -> "tuple[tuple[str, ...], int]":
    """Each code column left blank and answered `measurement`: the two tables' digests and the twin cells equal to a real code."""
    header, columns, real = _code_columns()
    found: "list[str]" = []
    equal = 0
    for answered, options in (("blank", {}), ("measurement", {"forced_measurements": header})):
        here = folder / answered
        here.mkdir()
        document, described, twin, outcome = _run_through_the_library(here, header, columns, SETTINGS, **options)
        found += [_table_digest(document, described, twin, outcome)]
        equal += sum(1 for name in header for cell in twin[name] if cell in real)
    return tuple(found), equal


def test_a_generated_sweep_of_magnitude_columns_writes_as_the_base_did(tmp_path: pathlib.Path) -> None:
    """THE RETURN (LANE LM1 RULINGS 5 (2)): 400 generated columns of magnitudes, each block, twin and verdict byte for byte 820d55c3's.

    Red on repair 1's head 5f03c2db, whose exponent form and census
    changed the blocks and twins of the columns written in one form.
    """
    assert _sweep_digests(tmp_path) == _BASE_SWEEP_DIGESTS


def test_codes_written_like_magnitudes_write_as_the_base_did(tmp_path: pathlib.Path) -> None:
    """The verify of repair 1, items 1 and 2: the five code shapes left blank and answered `measurement`, byte for byte 820d55c3's, no twin cell a real code.

    On repair 1's head, answered `measurement`, the census twin wrote
    19,990 of 20,000 cells equal to a real code at the table floor, and
    left blank its hold wrote twins validate refused for three shapes.
    """
    digests, equal = _code_digests(tmp_path)
    assert equal == 0
    assert digests == _BASE_CODE_DIGESTS


def test_the_zoo_magnitudes_write_as_the_base_did_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """THE ONE 20,000-ROW CASE: the zoo's `instrument_magnitudes` through the shipped command, every file it writes byte for byte 820d55c3's but the description written before any answer.

    That description's one moved value is lane CZ-A2's opening of the held
    `sample_id`'s run (plan P4-D469; see `_BASE_ZOO_DIGESTS`). Its three
    analyst checks fail again, as on the base, owned by lane LM2 (plan
    P4-D475).
    """
    table = health_zoo.table_named("instrument_magnitudes")
    health_zoo.run_table(table, tmp_path, health_zoo.KPI_ROWS, health_zoo.seed_of(table), small_tables_refused=True)
    written = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(tmp_path.iterdir()) if path.is_file()}
    assert written == _BASE_ZOO_DIGESTS
