"""The repair pass after the final skeptic of the merged Codex repairs.

The skeptic read the merge of the four repairs of the final Codex round
(a7ae404) end to end and found one BLOCKER and six MAJOR items the
round had not reached. Each is pinned here by its own reproduction and,
where the rule it repairs is a function of its own, by the MUTANT that
takes the rule back out, so a witness that stops exercising its rule
turns this file red rather than staying green on nothing.

- **P4-D175** the form census asks two more totals a reader holds:
  `n_not_numeric`, against the forms no number is written in, and
  `n_code_alphabet` less `n_all_digits`, against the forms of the code
  alphabet;
- **P4-D181** a form is never named at a count of one, whatever the floor;
- **P4-D176** a saturated grid is filled on every written grid, not only
  on the integers;
- **P4-D177** a stratum left in an empty stretch of a column that writes
  no cell point-free may take either edge of the stretch;
- **P4-D178** a column whose published rungs and mode are exactly its
  levels takes those levels;
- **P4-D179** a column of several widths holds as many cells on each
  narrower grid as its census counts there;
- the width census `pad_widths` leaves no complement of one beside
  `n_numeric`: the carried item of plan P4-D148, closed by plan P4-D221
  (stage 2 closed by the owner rulings of 2026-09-17).

Every table is built by seeded neutral code at runtime (plan D13).
"""

import collections
import importlib.util
import pathlib
import random

import pytest

import fixtures
from synthtwin import contract, errors, generation, parsing, profile, reading, taxonomy
from tests.test_final_review_labels import _both_pass, _column, _round_trip


def _described(
    folder: pathlib.Path,
    columns: "dict[str, list[str]]",
    floor: int = 1,
    codes: "list[str] | None" = None,
) -> "tuple[dict, contract.Profile]":
    """The real reader, producer and loader, in this process."""
    folder.mkdir(parents=True, exist_ok=True)
    names = list(columns)
    size = len(columns[names[0]])
    rows = [[columns[name][index] for name in names] for index in range(size)]
    path = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(names, rows))
    table = reading.read_table(str(path), first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), [], codes
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, "t-profile.json", document))
    )
    return document, loaded


def _beside(cells: "list[str]") -> "dict[str, list[str]]":
    """A column under test and a column of labels beside it."""
    return {
        "value": cells,
        "other": [f"row{index % 7}" for index in range(len(cells))],
    }


def _codes(draw: random.Random, count: int) -> "list[str]":
    return [
        "".join(draw.choice("abcdefghjkmnp") for _letter in range(3))
        + "-"
        + str(draw.randrange(100, 1000))
        for _row in range(count)
    ]


def _figures(draw: random.Random) -> "list[str]":
    return [str(draw.randrange(10000, 99999)) for _row in range(400)]


def _refused(
    folder: pathlib.Path, document: dict, census: "dict[str, int]"
) -> str:
    for column in document["columns"]:
        if column["name"] == "value":
            column["shape_forms"] = census
    edited = fixtures.write_profile(folder, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    return str(refused.value)


# ------------------- P4-D175, two more totals beside the form census


@pytest.mark.parametrize("floor", [1, 11])
def test_a_text_cell_of_another_shape_is_not_left_over_beside_numbers(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """400 figures, 399 codes and one sentence: `n_not_numeric` is 400.

    Before P4-D175 the census published `{"&&&-%%%": 399}` beside it, and
    400 - 399 named the one row written otherwise. The same table with a
    four-hundredth code in the sentence's place still publishes the form.
    """
    draw = random.Random(9)
    figures = _figures(draw)
    codes = _codes(draw, 400)
    document, _loaded = _described(
        tmp_path / "one", _beside(figures + codes[:399] + ["hello world"]), floor
    )
    column = document["columns"][0]
    assert (column["role"], column["n_not_numeric"]) == ("free_text", 400)
    assert column["shape_forms"] == {}
    adjacent, _loaded = _described(
        tmp_path / "adjacent", _beside(figures + codes), floor
    )
    assert adjacent["columns"][0]["shape_forms"] == {"&&&-%%%": 400}


def test_a_declared_code_of_another_shape_is_not_left_over(
    tmp_path: pathlib.Path,
) -> None:
    """The long-tail role carries no code-alphabet total, only `n_not_numeric`."""
    draw = random.Random(9)
    cells = [str(index) for index in range(400)] + _codes(draw, 399) + ["hello"]
    document, _loaded = _described(tmp_path, _beside(cells), 11, ["value"])
    column = document["columns"][0]
    assert column["role"] == "long_tail_labels"
    assert column["shape_forms"] == {}


def test_the_text_total_is_the_rule_that_holds_the_code_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: no form is ever known not to be a number."""
    monkeypatch.setattr(parsing, "form_never_a_number", lambda _key: False)
    draw = random.Random(9)
    cells = [str(index) for index in range(400)] + _codes(draw, 399) + ["hello"]
    document, _loaded = _described(tmp_path, _beside(cells), 11, ["value"])
    assert document["columns"][0]["shape_forms"] == {"&&&-%%%": 399}


@pytest.mark.parametrize("floor", [1, 11])
def test_a_code_cell_that_is_a_number_is_not_left_over(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """`n_code_alphabet` less `n_all_digits` is 400 beside 399 code forms.

    The four-hundredth cell is a signed number thirty figures long: inside
    the code alphabet, not figures alone, not text, and too long for a
    form, so no other total names it.
    """
    draw = random.Random(9)
    cells = _figures(draw) + _codes(draw, 399) + ["-" + "1234567890" * 3]
    document, _loaded = _described(tmp_path, _beside(cells), floor)
    column = document["columns"][0]
    assert (column["n_code_alphabet"], column["n_all_digits"]) == (800, 400)
    assert column["n_not_numeric"] == 399
    assert column["shape_forms"] == {}


def test_the_skeptic_s_table_round_trips_with_no_form_left_over(
    tmp_path: pathlib.Path,
) -> None:
    """The reproduction as written, through the command line, both files."""
    draw = random.Random(9)
    cells = _figures(draw) + _codes(draw, 399) + ["hello"]
    result = _round_trip(tmp_path, {"value": cells}, ("--smallest-group", "11"))
    assert _column(result)["shape_forms"] == {}
    _both_pass(result)


def test_the_loader_refuses_a_text_total_left_one_over(
    tmp_path: pathlib.Path,
) -> None:
    draw = random.Random(9)
    cells = _figures(draw) + _codes(draw, 399) + ["hello world"]
    document, _loaded = _described(tmp_path, _beside(cells), 11)
    said = _refused(tmp_path, document, {"&&&-%%%": 399})
    assert "SF3" in said and "n_not_numeric" in said


def test_the_loader_refuses_a_code_total_less_figures_left_one_over(
    tmp_path: pathlib.Path,
) -> None:
    draw = random.Random(9)
    cells = _figures(draw) + _codes(draw, 399) + ["-" + "1234567890" * 3]
    document, _loaded = _described(tmp_path, _beside(cells), 11)
    said = _refused(tmp_path, document, {"&&&-%%%": 399})
    assert "SF3" in said and "n_all_digits" in said


def test_no_number_is_written_in_a_form_the_rule_calls_text() -> None:
    """The key rule against the reader it stands for, cell by cell."""
    for text in ("12", "-1.5", "+3", "(4.5)", "1,234.5", "1e5", "-2.5E-3", "7.", ".5"):
        if parsing.parse_number(text) is None:
            continue
        form = parsing.shape_form(text)
        if form:
            assert not parsing.form_never_a_number(form), (text, form)
    for key in ("@@@-%%%", "%%/%%", "@%%.%", "%@%@", "@@", "%%@", "%-@%"):
        assert parsing.form_never_a_number(key), key
    for key in ("%%", "-%.%", "%@%", "%.%&-%", "(%,%%%.%)"):
        assert not parsing.form_never_a_number(key), key


# ------------------------ P4-D181, never a named form of one cell


def test_a_form_of_one_cell_is_never_named_at_the_default_floor(
    tmp_path: pathlib.Path,
) -> None:
    """799 codes and one of another shape, at a floor of one.

    It published `{"&&&-%%%%%": 799, "@@-%%%%%%": 1}` on a role that
    publishes no value. The form of one is not named, and the form of 799
    beside it is then one short of `n_present`, so it is taken back too.
    """
    draw = random.Random(3)
    cells = [
        "".join(draw.choice("abcdefghjkmnp") for _letter in range(3))
        + "-"
        + str(draw.randrange(10000, 99999))
        for _row in range(799)
    ] + ["ab-000001"]
    document, _loaded = _described(tmp_path, _beside(cells), 1)
    column = document["columns"][0]
    assert column["role"] == "free_text"
    assert column["shape_forms"] == {}
    said = _refused(tmp_path, document, {"&&&-%%%%%": 799, "@@-%%%%%%": 1})
    assert "SF1" in said


# ---------------------- P4-D176, a saturated grid of tenths is filled


def _tenths() -> "list[str]":
    return [f"{(index + 1) / 10:.1f}" for index in range(120)]


def _numbers_held(twin: generation.Twin) -> int:
    return len({float(cell) for cell in twin.columns[0] if cell})


def test_a_saturated_grid_of_tenths_holds_every_number(
    tmp_path: pathlib.Path,
) -> None:
    """0.1 to 12.0 publishes 120 numbers between ends holding 120 tenths."""
    draw = random.Random(41)
    _document, loaded = _described(
        tmp_path,
        {"value": _tenths(), "id": [str(draw.randint(1000, 9999)) for _row in range(120)]},
    )
    for seed in (4, 0, 1):
        assert _numbers_held(generation.generate(loaded, seed)) == 120, seed


def test_the_tenths_are_filled_by_the_grid_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the fill stands aside on every grid but the integers.

    SINCE THE CARRIED NUMBERS PASS OF 2026-09-18 THE FILL IS STATED
    TWICE: column-wide in `_saturated_integers` (plans P4-D147 and
    P4-D176) and band by band in `_saturated_bands`. This column is of
    one sign, so its one band is the whole column and the band fill is
    the same fill -- withdrawn from the column-wide statement alone, the
    band fill wrote all 120 numbers and this mutant stopped biting. So it
    withdraws the fill on a written grid in both statements, which is
    what the rule it pins means.

    AND SINCE THE REPAIR PASS OF 2026-09-19 THE PUSH OF G6.5a ENDS AT THE
    SAME ASSIGNMENT: on a grid with no spare point the one collision the
    walks leave is pushed to the one free tenth, and the strata take the
    120 tenths in order -- measured, the same 120 cells as the fill. So
    the push is withdrawn on a written grid as well. Each of the three
    statements is held up ALONE elsewhere, by a test whose mutant
    withdraws it and nothing else:
    `tests/test_carried_numbers.py::test_the_column_wide_fill_is_what_holds_it`,
    `test_the_push_is_what_holds_the_nearly_full_band` beside it, and the
    frozen cases `saturated_grid_alone`, `saturated_band` and
    `pushed_along_band`.
    """
    shipped = generation._saturated_integers
    shipped_bands = generation._saturated_bands
    shipped_push = generation._pushed_apart

    def integers_only(layout, rungs, values, figures, facts):  # type: ignore[no-untyped-def]
        if figures > 0:
            return None
        return shipped(layout, rungs, values, figures, facts)

    def bands_on_integers_only(column, facts, layout, rungs, values, figures):  # type: ignore[no-untyped-def]
        if figures > 0:
            return values
        return shipped_bands(column, facts, layout, rungs, values, figures)

    def push_on_integers_only(facts, layout, rungs, moved, texts, held, figures, keep_whole):  # type: ignore[no-untyped-def]
        if figures > 0:
            return (moved, texts, held)
        return shipped_push(facts, layout, rungs, moved, texts, held, figures, keep_whole)

    monkeypatch.setattr(generation, "_saturated_integers", integers_only)
    monkeypatch.setattr(generation, "_saturated_bands", bands_on_integers_only)
    monkeypatch.setattr(generation, "_pushed_apart", push_on_integers_only)
    draw = random.Random(41)
    _document, loaded = _described(
        tmp_path,
        {"value": _tenths(), "id": [str(draw.randint(1000, 9999)) for _row in range(120)]},
    )
    assert _numbers_held(generation.generate(loaded, 4)) == 119


def test_a_decimal_comma_grid_of_tenths_round_trips(tmp_path: pathlib.Path) -> None:
    """Files review item 16's twin, which still missed its distinct count."""
    cells = [text.replace(".", ",") for text in _tenths()]
    result = _round_trip(
        tmp_path, {"value": cells}, ("--decimal-comma", "value")
    )
    assert _column(result)["n_distinct_values"] == 120
    _both_pass(result)


def _oracle():  # type: ignore[no-untyped-def]
    """The independent oracle, loaded from its path (it is not a package)."""
    path = fixtures.REPO_ROOT / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ladder(loaded: contract.Profile) -> "list[float]":
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    return list(generation._merged_rungs(facts))


def test_the_oracle_fills_the_grid_of_tenths_as_the_twin_does(
    tmp_path: pathlib.Path,
) -> None:
    """The method's reading of P4-D176, against the shipped twin's numbers."""
    draw = random.Random(41)
    _document, loaded = _described(
        tmp_path,
        {"value": _tenths(), "id": [str(draw.randint(1000, 9999)) for _row in range(120)]},
    )
    filled = _oracle().saturated_grid(120, 1, 120, ["positive"] * 120, _ladder(loaded))
    twin = generation.generate(loaded, 4)
    assert filled == sorted({float(cell) for cell in twin.columns[0] if cell})
    assert _oracle().saturated_grid(120, 0, 120, ["positive"] * 120, _ladder(loaded)) is None


# ------------------------ P4-D178, the published levels themselves


_ELEVEN = ["0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "4.0", "5.0", "10.0", "12.5", "20.0"]
_SIX = ["2.0", "3.0", "5.0", "7.5", "10.0", "15.0"]


def _foreign_numbers(
    loaded: contract.Profile, source: "list[str]", seeds: "tuple[int, ...]"
) -> "dict[int, dict[str, int]]":
    """Per seed, the cells the twin wrote at a number the source never held."""
    held = set(source)
    found: "dict[int, dict[str, int]]" = {}
    for seed in seeds:
        twin = generation.generate(loaded, seed)
        foreign = collections.Counter(
            cell for cell in twin.columns[0] if cell and cell not in held
        )
        if foreign:
            found[seed] = dict(foreign)
    return found


def test_a_column_of_eleven_quantities_keeps_its_levels(
    tmp_path: pathlib.Path,
) -> None:
    """2,000 quantities of eleven levels, every seed, every level exact.

    Measured before P4-D178: `1.3` 199 times, `2.9` 195 times and `1.7`
    201 times in three twins of eight, each in place of a level the source
    held, with validation at exit 0.
    """
    draw = random.Random(20260917)
    cells = [draw.choice(_ELEVEN) for _row in range(2000)]
    _document, loaded = _described(tmp_path, {"value": cells})
    assert _foreign_numbers(loaded, cells, tuple(range(8))) == {}


def test_the_oracle_reads_the_eleven_levels_as_the_twin_does(
    tmp_path: pathlib.Path,
) -> None:
    """The method's reading of P4-D178: the rungs twice named, the ends, the mode."""
    draw = random.Random(20260917)
    cells = [draw.choice(_ELEVEN) for _row in range(2000)]
    _document, loaded = _described(tmp_path, {"value": cells})
    facts = loaded.columns[0].facts
    placeholder = [0.25 + place for place in range(11)]
    levels = _oracle().saturated_levels(
        11, 1, placeholder, ["positive"] * 11, _ladder(loaded), facts.mode,
        False, False,
    )
    assert levels == sorted(float(level) for level in _ELEVEN)
    twin = generation.generate(loaded, 4)
    assert levels == sorted({float(cell) for cell in twin.columns[0] if cell})


def test_the_quantities_keep_their_levels_by_the_levels_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generation, "_saturated_levels", lambda *_args: None)
    draw = random.Random(20260917)
    cells = [draw.choice(_ELEVEN) for _row in range(2000)]
    _document, loaded = _described(tmp_path, {"value": cells})
    assert _foreign_numbers(loaded, cells, (1, 4)) != {}


# --------------- P4-D177, either edge of a stretch, where no cell is plain


def test_a_rare_level_beside_six_does_not_move_a_level_off_its_number(
    tmp_path: pathlib.Path,
) -> None:
    """Six discounts and one written twice: the levels rule stands aside.

    A stratum drawn inside the published stretch 7.5 to 10.0 could not
    take 10.0, because 10 has a point-free spelling and the stratum's
    value did not, although no cell of the column is written point-free;
    it went to 7.4 or 10.1 instead.
    """
    draw = random.Random(1)
    cells = [draw.choice(_SIX) for _row in range(1500)] + ["11.0", "11.0"]
    _document, loaded = _described(tmp_path, {"value": cells})
    assert _foreign_numbers(loaded, cells, tuple(range(8))) == {}


def test_the_rare_level_is_kept_by_the_edge_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: every column is treated as writing a cell point-free.

    RE-ARMED AT THE CARRIED NUMBERS PASS OF 2026-09-18. G6.5a's band fill
    now reaches this column first: its seven numbers on the grid of
    tenths, outside the six published empty pairs, are exactly its seven
    strata, so they take them before G6.7 runs and the edge rule is never
    asked -- the mutant moved nothing. The band fill is withdrawn here so
    that the edge rule is again what keeps the level, and that is asserted
    first: with the band fill gone and the edge rule shipped, no foreign
    number is written; with the edge rule mutated as well, one is.
    """
    shipped = generation._cleared_value

    def as_if_point_free(*arguments):  # type: ignore[no-untyped-def]
        return shipped(*arguments[:13], True)

    monkeypatch.setattr(
        generation,
        "_saturated_bands",
        lambda column, facts, layout, rungs, values, figures: values,
    )
    draw = random.Random(1)
    cells = [draw.choice(_SIX) for _row in range(1500)] + ["11.0", "11.0"]
    _document, loaded = _described(tmp_path, {"value": cells})
    assert _foreign_numbers(loaded, cells, (1, 4, 7)) == {}
    monkeypatch.setattr(generation, "_cleared_value", as_if_point_free)
    assert _foreign_numbers(loaded, cells, (1, 4, 7)) != {}


def test_the_edge_rule_keeps_a_rare_level_with_nothing_patched_off(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The edge rule of P4-D177 acting unaided, on the shipped path.

    The repair skeptic's MINOR finding of 2026-09-19: the test above bites
    only with the band fill patched off, because its column is band
    saturated and the band fill reaches it first. This column is not:
    six discounts from 2.5 to 15.0 beside a rare level 11.0 written twice.
    Nothing is withdrawn for the first assertion -- the band fill is
    watched and does not act -- and the twin writes no number the source
    never held; with the edge rule mutated, it writes one at every seed.
    """
    acted: "list[int]" = []
    shipped_bands = generation._saturated_bands

    def watched(column, facts, layout, rungs, values, figures):  # type: ignore[no-untyped-def]
        given = shipped_bands(column, facts, layout, rungs, values, figures)
        if given != values:
            acted.append(1)
        return given

    monkeypatch.setattr(generation, "_saturated_bands", watched)
    draw = random.Random(1)
    levels = ["2.5", "3.0", "5.0", "7.5", "10.0", "15.0"]
    cells = [draw.choice(levels) for _row in range(1500)] + ["11.0", "11.0"]
    _document, loaded = _described(tmp_path, {"value": cells})
    assert _foreign_numbers(loaded, cells, (1, 4, 7)) == {}
    assert acted == []
    shipped = generation._cleared_value

    def as_if_point_free(*arguments):  # type: ignore[no-untyped-def]
        return shipped(*arguments[:13], True)

    monkeypatch.setattr(generation, "_cleared_value", as_if_point_free)
    moved = _foreign_numbers(loaded, cells, (1, 4, 7))
    assert sorted(moved) == [1, 4, 7]


# -------------- P4-D179, the widths a shortest-round-trip export writes


def _two_place_readings() -> "list[str]":
    draw = random.Random(20260917)
    return [repr(round(max(0.3, draw.gauss(1.1, 0.35)), 2)) for _row in range(2000)]


def _thousandths() -> "list[str]":
    draw = random.Random(5)
    return [repr(round(draw.gauss(10, 2), 3)) for _row in range(1200)]


def _mixed_places() -> "list[str]":
    draw = random.Random(11)
    return [
        repr(round(draw.gauss(10, 3), draw.choice((1, 2, 3))))
        for _row in range(400)
    ]


def _written_widths(twin: generation.Twin) -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for cell in twin.columns[0]:
        if "." in cell:
            width = f"{len(cell.split('.')[1])}"
            counted[width] = counted.get(width, 0) + 1
    return counted


def _widths_met(loaded: contract.Profile, document: dict, seed: int) -> bool:
    twin = generation.generate(loaded, seed)
    return _written_widths(twin) == document["columns"][0]["fraction_widths"]


def test_two_places_written_by_the_shortest_round_trip_keep_both_widths(
    tmp_path: pathlib.Path,
) -> None:
    """`1.1` beside `1.23`: every seed writes both widths exactly.

    Measured before P4-D179 on the skeptic's two-place column: 168 to 178
    one-place cells against 182 at every seed, in CSV and in a workbook.
    """
    document, loaded = _described(tmp_path, {"value": _two_place_readings()})
    assert len(document["columns"][0]["fraction_widths"]) == 2
    for seed in (1, 4, 7):
        assert _widths_met(loaded, document, seed), seed


@pytest.mark.parametrize(
    ("rule", "replacement"),
    [
        (
            "_pinned_width_order",
            lambda quotas, _need, _size: sorted(quotas, reverse=True),
        ),
    ],
)
def test_the_two_widths_are_kept_by_each_rule(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    rule: str,
    replacement: object,
) -> None:
    """The mutant: a pinned value takes the widest width."""
    monkeypatch.setattr(generation, rule, replacement)
    document, loaded = _described(tmp_path, {"value": _two_place_readings()})
    assert not _widths_met(loaded, document, 4)


def test_the_exchange_has_no_witness_left_on_these_shapes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`_widths_exchanged` stopped biting at landing 3.3, and this says so.

    THE MUTANT WAS THE FIRST HALF OF THE TEST ABOVE: withdraw the
    exchange -- hand the values back untouched -- and the two-place
    column's twin missed its own `fraction_widths` at every seed. It
    does not any more. The tail rule places the rows beyond each
    boundary on their own grid points and derives the two ends from the
    published facts (contract 6.7a, method G5.3b), so the values the
    width stages are handed already carry both widths and the exchange
    finds nothing to do on this column.

    FOUR SHAPES WERE SEARCHED FOR A WITNESS and none was found: the
    skeptic's own 2,000 two-place readings, 600 wider ones, 1,500 at a
    hundred, and 400 of mixed places -- the last of which misses its
    census with the rule AND without it, so it is no witness either.
    The rule stays: what it states is still true of the construction,
    and a case that needs it may arrive with the next shape. What is
    pinned here is the measurement itself, in the form the suite reads
    -- the mutant is applied and the twin still meets the census -- so
    a later change that gives the rule work again turns this red and is
    read rather than missed.
    """
    document, loaded = _described(tmp_path, {"value": _two_place_readings()})
    assert _widths_met(loaded, document, 4)
    monkeypatch.setattr(
        generation,
        "_widths_exchanged",
        lambda _column, _facts, _layout, values: values,
    )
    assert _widths_met(loaded, document, 4), (
        "the exchange has a witness again: put this case back in the "
        "parametrized mutant above, where it was until landing 3.3"
    )


def test_three_places_keep_every_width_and_every_number(
    tmp_path: pathlib.Path,
) -> None:
    """1,200 readings of nearly all different values: moves, not exchanges."""
    document, loaded = _described(tmp_path, {"value": _thousandths()})
    wanted = document["columns"][0]["n_distinct_values"]
    for seed in (1, 4, 7):
        twin = generation.generate(loaded, seed)
        assert _written_widths(twin) == document["columns"][0]["fraction_widths"]
        assert _numbers_held(twin) == wanted, seed


def test_three_places_need_the_moves(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        generation, "_widths_exchanged", lambda _c, _f, _l, values: values
    )
    document, loaded = _described(tmp_path, {"value": _thousandths()})
    assert not _widths_met(loaded, document, 4)


def test_a_snap_never_writes_one_number_as_another(tmp_path: pathlib.Path) -> None:
    """Mixed places: the count of different numbers holds where a snap runs."""
    document, loaded = _described(tmp_path, {"value": _mixed_places()})
    wanted = document["columns"][0]["n_distinct_values"]
    for seed in (4, 7):
        assert _numbers_held(generation.generate(loaded, seed)) == wanted, seed


def test_the_numbers_are_kept_apart_by_the_snap_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: a snap may land on a number another value holds."""
    monkeypatch.setattr(generation, "_snaps_onto", lambda *_arguments: False)
    document, loaded = _described(tmp_path, {"value": _mixed_places()})
    wanted = document["columns"][0]["n_distinct_values"]
    assert _numbers_held(generation.generate(loaded, 4)) < wanted


def test_the_two_place_readings_twin_passes_its_own_description(
    tmp_path: pathlib.Path,
) -> None:
    """Through the command line, the twin and the real table both at exit 0."""
    result = _round_trip(tmp_path, {"value": _two_place_readings()}, ("--smallest-group", "11"))
    _both_pass(result)


# ------------- the width census of pads, asked again (P4-D148, P4-D221)


@pytest.mark.parametrize("floor", [1, 11])
def test_a_pad_census_one_short_repeats_a_count_the_styles_already_print(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """799 padded codes and one unpadded, at floors of one and eleven.

    `pad_widths {"5": 799}` beside `n_numeric` 800 left one cell, and the
    skeptic read that as a count of one this census gives up. It gave up
    nothing the description did not already print: `numeric_styles`
    pooled that one cell as `{"(withheld)": 1}`, the older pooled count of
    one plan P4-D148 carried to the owner, and this test pinned that the
    two agreed so the day the pool stopped printing one the pad census
    would be asked again.

    THAT DAY IS PLAN P4-D221 (stage 2 closed by the owner rulings of
    2026-09-17), which pooled the whole map; since plan P4-D222 the one
    cell is counted into `leading_zero` at the commonest padded width, and
    no count the column prints leaves one cell over.
    """
    cells = [f"0{1000 + index}" for index in range(799)] + ["12345"]
    document, _loaded = _described(tmp_path, _beside(cells), floor)
    column = document["columns"][0]
    assert column["numeric_styles"] == {"leading_zero": 800}
    assert column["pad_widths"] == {"5": 800}
    for census in ("numeric_styles", "pad_widths", "field_widths"):
        printed = sum(column[census].values())
        assert printed in (0, column["n_numeric"]), (census, column[census])
