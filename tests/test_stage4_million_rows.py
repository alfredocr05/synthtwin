"""Stage 4 lane S4c: numbers at a million rows (plans P4-D390 and P4-D377).

Two items, routed from lane S4b-num's first skeptic:

1. THE QUALITY REPORT IS NEVER MADE WHOLE. Validating a register of
   997,770 rows took 1,323 MB, about 760 MB of it the report's join: its
   halves, joined level by level, each left its own size class mapped.
   `quality.report_pieces` hands the same text over in pieces of at most
   `quality._PIECE_LINES` lines, and `synthtwin validate` prints and
   writes them in turn (`cli._say_pieces`, `writing.write_text_file`'s
   ``pieces``). Pinned here by what can be counted without a clock: the
   pieces add up to `quality.quality_report`'s text, the screen and the
   file are never handed a text longer than a piece, and the bytes the
   command holds past what it held when the outcome was measured stay
   under a bound per character of the report.
2. G2'S DENSE TAIL MEETS ITS PUBLISHED MEAN DISTANCE (the second half of
   this file).
"""

from __future__ import annotations

import dataclasses
import pathlib
import sys
import tracemalloc

import pytest

import fixtures
import kpi_shapes
import test_stage4_numbers_and_codes as numbers_and_codes
from synthtwin import cli, contract, generation, parsing, quality, validation, writing

# -- 1. the quality report in pieces ------------------------------------------


def _pieces_of(loaded: object, outcome: validation.Outcome) -> "list[str]":
    return quality.report_pieces(loaded, outcome)  # type: ignore[arg-type]


def test_the_pieces_add_up_to_the_report(tmp_path: pathlib.Path) -> None:
    """Registers of 40 and 300 codes, met and damaged, and grown to 9,000 checks: the pieces are the report."""
    for codes in (40, 300):
        for damaged in (False, True):
            loaded, outcome = numbers_and_codes._register(tmp_path, codes, damaged)
            whole = quality.quality_report(loaded, outcome)  # type: ignore[arg-type]
            assert "".join(_pieces_of(loaded, outcome)) == whole, (codes, damaged)
    loaded, outcome = numbers_and_codes._register(tmp_path, 40, True)
    for count in (1, 2, 997, 9000):
        grown = numbers_and_codes._with_checks(outcome, count)
        pieces = _pieces_of(loaded, grown)
        assert "".join(pieces) == quality.quality_report(loaded, grown), count  # type: ignore[arg-type]
        for piece in pieces:
            assert piece.endswith("\n"), count
            assert piece.count("\n") <= quality._PIECE_LINES, count
    assert len(pieces) > 2, "premise: the grown report takes several pieces"


def test_a_piece_holds_at_most_its_lines_and_every_line_once() -> None:
    """The piece rule alone: 0, 1, the cap, one past it and two caps and one lines."""
    cap = quality._PIECE_LINES
    for count in (0, 1, cap, cap + 1, 2 * cap + 1):
        lines = [f"line {index}" for index in range(count)]
        pieces = quality._lines_pieces(list(lines))
        assert len(pieces) == -(-count // cap), count
        assert "".join(pieces) == "".join(line + "\n" for line in lines), count


def _validate_register(
    folder: pathlib.Path, count: int, spy: "dict[str, int]", traced: "list[int]", trace: bool = False
) -> "tuple[int, str, str]":
    """Run `synthtwin validate` on the damaged 40-code register with its outcome grown to ``count`` checks.

    Records in ``spy`` the longest text handed to the screen and to the
    file writer, and in ``traced`` the bytes `tracemalloc` saw held at
    the moment the outcome was handed back and the most held after it,
    where ``trace`` is set. Returns the exit code, the file written and the report expected.
    """
    cells: "list[str]" = []
    for place in range(40):
        cells += [str(1000001 + place)] * (1 if place % 25 == 7 else 11)
    arms = ["a" if place % 3 else "b" for place in range(len(cells))]
    table = numbers_and_codes._table
    described = kpi_shapes.describe(folder, "register", table({"code": cells, "arm": arms}), 11, codes=["code"])
    kept = [place for place in range(len(cells)) if place % 5]
    measured = fixtures.write(
        folder, "register-measured.csv", table({"code": [cells[one] for one in kept], "arm": [arms[one] for one in kept]})
    )
    loaded = described.loaded
    outcome = validation.measure(loaded, str(measured))
    grown = numbers_and_codes._with_checks(outcome, count)
    profile = folder / "register-profile.json"
    out = folder / f"out{count}"
    out.mkdir()

    def measured_again(*_arguments: object, **_keywords: object) -> validation.Outcome:
        if trace:
            traced[:] = [tracemalloc.get_traced_memory()[0]]
            tracemalloc.reset_peak()
        return grown

    shipped_print = print
    shipped_write = writing.write_text_file

    def printed(*arguments: object, **keywords: object) -> None:
        for argument in arguments:
            spy["screen"] = max(spy["screen"], len(f"{argument}"))
        shipped_print(*arguments, **keywords)  # type: ignore[call-overload]

    def written(target: pathlib.Path, text: str, *arguments: object, **keywords: object) -> None:
        longest = len(text)
        pieces = arguments[3] if len(arguments) > 3 else keywords.get("pieces")
        if isinstance(pieces, list):
            for piece in pieces:
                longest = max(longest, len(piece))
        spy["file"] = max(spy["file"], longest)
        shipped_write(target, text, *arguments, **keywords)  # type: ignore[arg-type]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(validation, "measure", measured_again)
        patch.setattr(cli, "print", printed, raising=False)
        patch.setattr(writing, "write_text_file", written)
        if trace:
            tracemalloc.start()
        try:
            code = cli.main(["validate", str(profile), "--twin", str(measured), "--out-dir", str(out)])
            if trace:
                traced += [tracemalloc.get_traced_memory()[1]]
        finally:
            if trace:
                tracemalloc.stop()
    files = sorted(out.glob("*"))
    assert len(files) == 1, files
    expected = parsing.visible_lines(quality.quality_report(loaded, grown))  # type: ignore[arg-type]
    return code, files[0].read_text(encoding="utf-8"), expected


def test_validate_hands_the_screen_and_the_file_no_text_longer_than_a_piece(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """6,000 checks, about 13,000 lines: the file is the report, and nothing longer than a piece is printed or written.

    As 50a52d6 shipped it the whole report was one text, printed whole
    and written whole: its longest text handed over was the report.
    """
    spy = {"screen": 0, "file": 0}
    traced: "list[int]" = []
    code, written, expected = _validate_register(tmp_path, 6000, spy, traced)
    assert code == 3
    assert written == expected
    shown = capsys.readouterr().out
    assert shown.startswith(expected + "\n"), "the screen shows the report as `_say` showed it whole"
    piece = 0
    for one in quality._lines_pieces(expected.split("\n")[:-1]):
        piece = max(piece, len(one))
    assert len(expected) > 8 * piece, "premise: the report is many pieces long"
    assert spy["screen"] <= piece, (spy, piece, len(expected))
    assert spy["file"] <= piece, (spy, piece, len(expected))


def test_validate_holds_under_two_and_a_half_bytes_a_character_of_its_report_past_the_outcome(
    tmp_path: pathlib.Path,
) -> None:
    """6,000 checks: what validate holds past the measured outcome stays under 2.5 times the report's length.

    Read off `tracemalloc` from the moment the outcome is handed back:
    the pieces and the file's bytes stand together at the most, 2.12
    times the report's 4.3 million characters here. As 50a52d6 shipped
    it two levels of the join, and then the text and its crossings of
    the display boundary, stood together: 3.00 times. What a freed size
    class leaves mapped is not seen by `tracemalloc`; it is what the
    pieces keep the command from making (plan P4-D390).
    """
    spy = {"screen": 0, "file": 0}
    traced: "list[int]" = []
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(sys, "stdout", open(tmp_path / "screen.txt", "w", encoding="utf-8", newline="\n"))  # noqa: SIM115
        try:
            code, written, expected = _validate_register(tmp_path, 6000, spy, traced, True)
        finally:
            sys.stdout.close()
    assert code == 3 and written == expected
    held = traced[1] - traced[0]
    assert held < 2.5 * len(expected), (held, len(expected), held / len(expected))


def test_the_pieces_are_written_as_the_text_would_be(tmp_path: pathlib.Path) -> None:
    """`write_text_file` with pieces writes the bytes of the pieces added together, and refuses a newline it would have to translate."""
    pieces = ["one\n", "twó\n", "", "thrée\nfour\n"]
    whole = tmp_path / "whole.txt"
    parts = tmp_path / "parts.txt"
    writing.write_text_file(whole, "".join(pieces))
    writing.write_text_file(parts, "", pieces=pieces)
    assert parts.read_bytes() == whole.read_bytes()
    writing.write_text_file(parts, "", newline="", pieces=pieces)
    assert parts.read_bytes() == whole.read_bytes()
    with pytest.raises(ValueError):
        writing.write_text_file(parts, "", newline="\r\n", pieces=pieces)
    assert parts.read_bytes() == whole.read_bytes(), "a refused write leaves the file alone"


def test_the_screen_shows_the_pieces_as_say_shows_the_whole(capsys: pytest.CaptureFixture[str]) -> None:
    """`_say_pieces` prints the bytes `_say` prints for the pieces added together, display controls shown."""
    pieces = ["a\x1b[2Jb\n", "c\n", "d‮e\n"]
    cli._say("".join(pieces))
    whole = capsys.readouterr().out
    cli._say_pieces(pieces)
    assert capsys.readouterr().out == whole
    assert "\x1b" not in whole and "‮" not in whole


# -- 2. G2's dense tail meets its published mean distance ---------------------


def _dense_tail(rows: int, tenths: bool = False, low: bool = False) -> "list[str]":
    """G2's dense tail (Codex's review of lane G2, item 3): consecutive grid points up to `999999` beside five far ones.

    ``rows`` cells: whole numbers from ``1000005 - rows`` to `999999` and
    five at ``999999 + floor(1.56 rows) + j``. With ``tenths`` every value
    is a tenth of that, written with one figure after the point; with
    ``low`` the run climbs from `100000` and the five stand below it.
    """
    if low:
        values = [100000 + place for place in range(rows - 5)]
        values += [100000 - (rows * 156) // 100 - 1 - place for place in range(5)]
    else:
        values = [place for place in range(1000005 - rows, 1000000)]
        values += [999999 + (rows * 156) // 100 + place for place in range(5)]
    if tenths:
        return [f"{value // 10}.{value % 10}" for value in values]
    return [f"{value}" for value in values]


def _described_tail(folder: pathlib.Path, stem: str, cells: "list[str]") -> kpi_shapes.Described:
    return kpi_shapes.describe(
        folder, stem, numbers_and_codes._table({"value": cells}), 11, measured=["value"]
    )


def _tail_mean_from_published(described: kpi_shapes.Described, twin: str, low: bool) -> "tuple[float, float, float]":
    """The twin's tail mean distance from the PUBLISHED boundary, the published one, and half a grid step."""
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None
    side = facts.tails.low if low else facts.tails.high
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder)
    reader = ladder.low if low else ladder.high
    assert side is not None and reader is not None and side.mean_distance is not None
    cells = sorted(float(cell.strip('"')) for cell in twin.split("\n")[1:] if cell)
    tail = cells[: side.rows] if low else cells[len(cells) - side.rows :]
    distances = [reader.boundary - cell if low else cell - reader.boundary for cell in tail]
    step = 1.0 if reader.dense_grid == 0 else 0.1
    return sum(distances) / side.rows, side.mean_distance, step / 2.0


def _verdict(outcome: validation.Outcome, subcheck: str) -> "tuple[str, str]":
    for check in outcome.checks:
        if check.subcheck == subcheck:
            return check.verdict, " ".join([check.published, check.achieved, *check.note])
    raise AssertionError(subcheck)


@pytest.mark.parametrize(
    ("rows", "tenths", "low"),
    [(8000, False, False), (8000, True, False), (8000, False, True)],
)
def test_a_dense_tail_meets_its_published_mean_distance(
    tmp_path: pathlib.Path, rows: int, tenths: bool, low: bool
) -> None:
    """The dense side's mean distance, from the published boundary, is the published one to half a grid step; nothing missed.

    As 50a52d6 built it the staircase pushed each crowded row one grid
    point past the row before and nothing gave it back: at 8,000 rows
    the high tail's twin stood at 1,095.7 against a published 820.4, the
    tenths at 84.5 against 82.0 and the low tail at 844.4 against 820.5
    (and at 16,000 rows 1,166.9 against 860.5), and the checker's
    window, drawn from that staircase, did not reach the published value.
    """
    described = _described_tail(tmp_path, f"tail{rows}{tenths}{low}", _dense_tail(rows, tenths, low))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None and ladder.high is not None
    dense, other = (ladder.low, ladder.high) if low else (ladder.high, ladder.low)
    assert dense.dense_grid == (1 if tenths else 0), "premise: the crowded side reads as dense"
    assert other.dense_grid == -1, "the other side's staircase meets its mean"
    side = facts.tails.low if low else facts.tails.high  # type: ignore[union-attr]
    assert side is not None
    for seed in (0, 4):
        twin = kpi_shapes.twin_text(described, seed)
        reached, published, half = _tail_mean_from_published(described, twin, low)
        assert abs(reached - published) <= half, (seed, reached, published)
        # The sum, not only the mean: within half a grid step over the rows.
        assert abs(reached - published) * side.rows <= half + 1e-6, (seed, reached, published)
        outcome = kpi_shapes.measure(described, twin, f"twin{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], seed
        name = "low" if low else "high"
        verdict, detail = _verdict(outcome, f"tails.{name}.mean_distance")
        assert verdict in (validation.HELD, validation.WITHIN_BOUND), (seed, verdict)
        assert "does NOT reach" not in detail, "the window reaches the published value"


def test_the_checker_draws_the_dense_window_beside_the_staircase_s(tmp_path: pathlib.Path) -> None:
    """The dense side's window reaches the published mean distance and still holds the twin the staircase alone writes.

    With rule 4 withdrawn the twin's tail stands where the staircase put
    it, 1.3 times the published mean distance out, inside G12.13's rank
    window as before; the hull the checker now draws reaches the
    published value too, where 50a52d6's window stopped short of it. And
    the real column itself, measured against its own description, is
    held exactly.
    """
    cells = _dense_tail(2000)
    described = _described_tail(tmp_path, "tail2000", cells)

    def withdrawn(
        _facts: object, _layout: object, _rungs: object, values: "list[float]"
    ) -> "list[float]":
        return values

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_tail_pair_met", withdrawn)
        staircase = kpi_shapes.twin_text(described, 0)
    reached, published, _step = _tail_mean_from_published(described, staircase, False)
    assert reached > 1.25 * published, "premise: the staircase stands well past the published mean"
    outcome = kpi_shapes.measure(described, staircase, "staircase.csv")
    verdict, detail = _verdict(outcome, "tails.high.mean_distance")
    assert verdict == validation.WITHIN_BOUND, verdict
    assert "does NOT reach" not in detail, detail
    real = kpi_shapes.measure(described, numbers_and_codes._table({"value": cells}), "real.csv")
    assert kpi_shapes.missed(real) == []
    assert _verdict(real, "tails.high.mean_distance")[0] == validation.HELD


@pytest.mark.parametrize("seed", [0, 4])
def test_a_tail_that_is_not_dense_keeps_its_twin_byte_for_byte(tmp_path: pathlib.Path, seed: int) -> None:
    """Six columns whose tails do not crowd their grid: no side is dense, and rule 4 changes no byte of the twin."""
    shapes: "dict[str, list[str]]" = {
        "readings": [f"{1000 + place % 900}" for place in range(1500)] + ["99900"],
        "lognormal": [f"{round(2.718281828 ** (3 + (place * 7919 % 1000) / 400.0), 2):.2f}" for place in range(2000)],
        "ages": [f"{18 + (place * 37) % 80}" for place in range(3000)],
        "halves": [f"{(place * 13) % 400 / 2:.1f}" for place in range(4000)],
        "spread": [f"{place * place}" for place in range(1, 1200)],
        "codes": [f"{(place * 7) % 5000:05d}" for place in range(2500)],
    }
    for stem, cells in shapes.items():
        described = _described_tail(tmp_path / stem, stem, cells)
        facts = described.loaded.columns[0].facts
        assert isinstance(facts, contract.NumericFacts)
        ladder = contract.tail_ladder(facts)
        if isinstance(ladder, contract.ShapedLadder):
            for reader in (ladder.low, ladder.high):
                assert reader is None or reader.dense_grid == -1, stem
        twin = kpi_shapes.twin_text(described, seed)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_tail_pair_met", lambda _f, _l, _r, values: values)
            assert kpi_shapes.twin_text(described, seed) == twin, stem


def _placement_lines(folder: pathlib.Path, strata: int, tail: int) -> "tuple[int, list[float]]":
    """The lines rule 4's placement runs on a division of ``strata`` one-cell strata whose high tail is ``tail`` cells.

    The tail is a run of consecutive whole numbers from the boundary,
    half its strata, and as many outer strata seven apart; the block, its
    ladder's reader and its tail are the
    8,000-row dense tail's, given this many rows and a mean distance the
    run alone cannot reach.
    """
    described = _described_tail(folder, "tail8000", _dense_tail(8000))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    boundary = float(10 * strata)
    values = [float(place) for place in range(strata - tail)]
    values += [boundary + 1 + place for place in range(tail // 2)]
    values += [boundary + tail + 7 * place for place in range(tail - tail // 2)]
    layout = generation._NumericLayout(
        sizes=tuple([1] * strata),
        starts=tuple(range(strata)),
        bands=tuple([generation._BAND_POSITIVE] * strata),
        raw_budgets=(0, 0, 0, 0),
        folded_budgets=(0, 0, 0, 0),
    )
    reader = dataclasses.replace(ladder.high, rows=tail, boundary=boundary, numbers=strata)
    side = dataclasses.replace(facts.tails.high, rows=tail, mean_distance=tail / 2.0 + 200.0, rms_distance=4.0 * tail)
    codes = {
        generation._dense_side_placed.__code__,
        generation._dense_free.__code__,
        generation._dense_value.__code__,
    }
    placed: "list[list[float] | None]" = []

    def run() -> None:
        placed.extend([generation._dense_side_placed(facts, layout, values, reader, side)])

    lines = numbers_and_codes._lines_run(codes, run)
    found = placed[0]
    assert found is not None, "premise: the side is placed"
    return lines, found


def test_rule_4_reads_the_tail_and_no_more_up_to_a_million_strata(tmp_path: pathlib.Path) -> None:
    """A million one-cell strata, a tail of 10,000: the placement runs the same lines as on 100,000, under 60 a tail stratum.

    The placement walks in from the outside to the tail's first stratum,
    reads the run, and weighs every count of far strata from running sums
    once each, so its work is the tail's strata and not the column's, and
    not the square of the far strata it weighs: here 5,000 of them, and
    10,000 at the doubled tail. Its sum is met to a step.
    """
    small, _values = _placement_lines(tmp_path / "small", 100000, 10000)
    large, found = _placement_lines(tmp_path / "large", 1000000, 10000)
    assert large == small, (small, large)
    assert large < 60 * 10000, large
    boundary = 10.0 * 1000000
    tail = found[len(found) - 10000 :]
    reached = sum(value - boundary for value in tail)
    assert abs(reached - 10000 * (10000 / 2.0 + 200.0)) <= 1.0, reached
    doubled, _values = _placement_lines(tmp_path / "doubled", 1000000, 20000)
    assert doubled < 2.5 * large, (large, doubled)


def test_a_stand_in_number_is_passed_over_unless_the_block_holds_it() -> None:
    """`_dense_free`: `9999` and `-999` are stepped past outward on both grids, and kept where the block holds them."""
    assert generation._dense_free(9999, 1, 1, ()) == 10000
    assert generation._dense_free(-999, -1, 1, ()) == -1000
    assert generation._dense_free(99990, 1, 10, ()) == 99991
    assert generation._dense_free(9999, 1, 1, (9999.0,)) == 9999
    assert generation._dense_free(9998, 1, 1, ()) == 9998


# -- the measures `K-S4-06` and `K-S4-07` read (tests/test_kpi_ledger.py) -----


def report_measures(folder: pathlib.Path) -> "dict[str, float]":
    """6,000 checks through `synthtwin validate`: bytes held past the outcome per report character, and the longest text handed over per piece."""
    spy = {"screen": 0, "file": 0}
    traced: "list[int]" = []
    folder.mkdir(parents=True, exist_ok=True)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(sys, "stdout", open(folder / "screen.txt", "w", encoding="utf-8", newline="\n"))  # noqa: SIM115
        try:
            _code, written, expected = _validate_register(folder, 6000, spy, traced, True)
        finally:
            sys.stdout.close()
    assert written == expected
    piece = 0
    for one in quality._lines_pieces(expected.split("\n")[:-1]):
        piece = max(piece, len(one))
    return {
        "report_held_bytes_per_character": round((traced[1] - traced[0]) / len(expected), 2),
        "longest_text_handed_over_per_piece": round(max(spy["screen"], spy["file"]) / piece, 2),
    }


def dense_tail_measures(folder: pathlib.Path) -> "dict[str, float]":
    """G2's dense tail at 8,000 rows -- whole, in tenths, and low -- at seed 0: each twin's miss of the published mean distance in half grid steps; and rule 4's lines as its tail doubles and as its strata grow tenfold."""
    found: "dict[str, float]" = {}
    for key, tenths, low in (("high", False, False), ("tenths", True, False), ("low", False, True)):
        described = _described_tail(folder / key, key, _dense_tail(8000, tenths, low))
        reached, published, half = _tail_mean_from_published(described, kpi_shapes.twin_text(described, 0), low)
        found[f"mean_distance_miss_in_half_steps_8000_{key}"] = round(abs(reached - published) / half, 3)
    small, _values = _placement_lines(folder / "small", 100000, 10000)
    large, _values = _placement_lines(folder / "large", 1000000, 10000)
    doubled, _values = _placement_lines(folder / "doubled", 1000000, 20000)
    found["placement_lines_growth_2x_tail"] = round(doubled / large, 2)
    found["placement_lines_growth_10x_strata"] = round(large / small, 2)
    found["placement_lines_1m_strata_10000_tail"] = large
    return found


def test_a_dense_side_s_twin_that_already_meets_its_mean_stays_byte_for_byte(tmp_path: pathlib.Path) -> None:
    """The low dense tail at 2,000 rows: its twin's mean already stands within half a step, and rule 4 moves nothing."""
    described = _described_tail(tmp_path, "low2000", _dense_tail(2000, False, True))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None
    assert ladder.low.dense_grid == 0, "premise: a dense side"
    for seed in (0, 4):
        twin = kpi_shapes.twin_text(described, seed)
        reached, published, half = _tail_mean_from_published(described, twin, True)
        assert abs(reached - published) <= half, "premise: already met"
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_tail_pair_met", lambda _f, _l, _r, values: values)
            assert kpi_shapes.twin_text(described, seed) == twin, seed


def _numeric_facts(distinct: int, used: int) -> contract.NumericFacts:
    """A whole-valued block's facts carrying only what `contract._dense_grid` reads."""
    facts = contract.NumericFacts.__new__(contract.NumericFacts)
    for name, value in (
        ("integer_valued", True),
        ("n_distinct_values", distinct),
        ("n_used_in_statistics", used),
        ("fraction_widths", {}),
    ):
        object.__setattr__(facts, name, value)
    return facts


_HIGH = contract.TailReader(
    low=False, percent=99, boundary=100.0, rows=4, numbers=40, flat=False, power=3,
    blend=0.5, reach=10.0, end=130.0, listed=(), counts=(),
)


def test_which_staircases_are_dense() -> None:
    """`contract._dense_grid` on staircases made to measure: pushed out, held at the end, pulled in, on a column that repeats."""
    facts = _numeric_facts(40, 40)
    out = dataclasses.replace(_HIGH, steps=(101.0, 102.0, 103.0, 130.0))
    assert contract._dense_grid(out, facts, 8.0) == 0, "pushed outward: 9.0 against 8.0"
    assert contract._dense_grid(out, facts, 8.6) == -1, "within half a step"
    assert contract._dense_grid(out, facts, 10.0) == -1, "further in than the published mean"
    held = dataclasses.replace(_HIGH, steps=(101.0, 102.0, 130.0, 130.0))
    assert contract._dense_grid(held, facts, 5.0) == -1, "rows held together at the end"
    assert contract._dense_grid(out, _numeric_facts(39, 40), 8.0) == -1, "a column that repeats a number"


def test_the_dense_window_moves_with_the_boundary_rung_s_own() -> None:
    """`contract.dense_tail_mean_window`, each side, a boundary window lopsided either way."""
    side = contract.TailSide.__new__(contract.TailSide)
    object.__setattr__(side, "mean_distance", 50.0)
    high = dataclasses.replace(_HIGH, dense_grid=0)
    assert contract.dense_tail_mean_window(high, side, 90.0, 101.0) == (48.0, 61.0)
    low = dataclasses.replace(high, low=True)
    assert contract.dense_tail_mean_window(low, side, 90.0, 101.0) == (39.0, 52.0)
    tenths = dataclasses.replace(high, dense_grid=1)
    window = contract.dense_tail_mean_window(tenths, side, 99.5, 100.25)
    assert window is not None and abs(window[0] - 49.65) < 1e-9 and abs(window[1] - 50.6) < 1e-9
    assert contract.dense_tail_mean_window(dataclasses.replace(high, dense_grid=-1), side, 90.0, 101.0) is None


def test_at_100000_rows_the_checker_s_window_reaches_the_published_mean_only_through_the_dense_window(
    tmp_path: pathlib.Path,
) -> None:
    """G2's dense tail at 100,000 rows: G12.13's rank window misses the published 1,280.5; the hull reaches it.

    The window alone, as `validate` draws it: no twin is written. The
    rank window ran 1,401.5 to 2,459.6 on 50a52d6.
    """
    described = _described_tail(tmp_path, "tail100000", _dense_tail(100000))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    side = facts.tails.high
    assert side.mean_distance is not None
    ladder = validation._filled_ladder(facts)
    window = validation._tail_window(facts, 11, ladder, side, False)[0]
    assert window[0] <= side.mean_distance <= window[1], window
    assert window[0] > side.mean_distance - 10.0, window
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(validation, "_dense_mean_window", lambda *_arguments: None)
        plain = validation._tail_window(facts, 11, ladder, side, False)[0]
    assert plain[0] > side.mean_distance, ("premise: the rank window alone misses the value", plain)
    assert window[1] == plain[1], "the hull keeps the rank window's far end"


def _twenty_row_tail(far: "list[float]") -> "tuple[object, generation._NumericLayout, list[float], contract.TailReader, contract.TailSide]":
    """A hundred one-cell strata whose high tail of twenty is a run of fifteen from the boundary and the five ``far`` beyond it.

    The pair is the one five far cells at 1,000, 1,001, 1,002, 1,003 and
    1,005 steps would give: a mean distance of 5,131 / 20 and a mean
    square of 5,023,279 / 20.
    """
    described_facts = _numeric_facts(100, 100)
    object.__setattr__(described_facts, "percentiles", contract.NumberLadder.__new__(contract.NumberLadder))
    object.__setattr__(described_facts.percentiles, "minimum", None)
    object.__setattr__(described_facts.percentiles, "maximum", None)
    object.__setattr__(described_facts, "field_widths", {})
    object.__setattr__(described_facts, "pad_widths", {})
    boundary = 1000.0
    values = [float(place) for place in range(80)]
    values += [boundary + 1 + place for place in range(15)]
    values += [boundary + distance for distance in far]
    layout = generation._NumericLayout(
        sizes=tuple([1] * 100),
        starts=tuple(range(100)),
        bands=tuple([generation._BAND_POSITIVE] * 100),
        raw_budgets=(0, 0, 0, 0),
        folded_budgets=(0, 0, 0, 0),
    )
    reader = dataclasses.replace(_HIGH, rows=20, boundary=boundary, numbers=100, dense_grid=0)
    side = contract.TailSide.__new__(contract.TailSide)
    for name, value in (("rows", 20), ("mean_distance", 5131 / 20), ("rms_distance", (5023279 / 20) ** 0.5)):
        object.__setattr__(side, name, value)
    return described_facts, layout, values, reader, side


def test_rule_4_places_the_far_strata_where_the_pair_says_and_leaves_a_tail_that_meets_it() -> None:
    """Twenty rows: five far strata go to 1,000 to 1,003 and 1,005 steps out -- the remainder on the outermost -- and a tail already summing to the mean stays."""
    facts, layout, values, reader, side = _twenty_row_tail([300.0, 400.0, 500.0, 600.0, 700.0])
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None
    assert [value - 1000.0 for value in placed[95:]] == [1000.0, 1001.0, 1002.0, 1003.0, 1005.0]
    assert placed[:95] == values[:95], "the run and everything inside it stay"
    facts, layout, values, reader, side = _twenty_row_tail([995.0, 1000.0, 1002.0, 1005.0, 1009.0])
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]
