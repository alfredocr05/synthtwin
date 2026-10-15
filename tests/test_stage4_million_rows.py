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
import math
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
    facts, layout, values, reader, side = _placement_inputs(folder, strata, tail)
    codes = {
        generation._dense_side_placed.__code__,
        generation._dense_free.__code__,
        generation._dense_value.__code__,
        generation._dense_census_kept.__code__,
        generation._serves_width.__code__,
    }
    placed: "list[list[float] | None]" = []

    def run() -> None:
        placed.extend([generation._dense_side_placed(facts, layout, values, reader, side)])

    lines = numbers_and_codes._lines_run(codes, run)
    found = placed[0]
    assert found is not None, "premise: the side is placed"
    return lines, found


def _placement_inputs(
    folder: pathlib.Path, strata: int, tail: int
) -> "tuple[contract.NumericFacts, generation._NumericLayout, list[float], contract.TailReader, contract.TailSide]":
    """`_placement_lines`'s division, values, reader and tail."""
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
    return facts, layout, values, reader, side


def test_rule_4_reads_the_tail_and_no_more_up_to_a_million_strata(tmp_path: pathlib.Path) -> None:
    """A million one-cell strata, a tail of 10,000: the placement runs the same lines as on 100,000, under 60 a tail stratum.

    The placement walks in from the outside to the tail's first stratum,
    reads the run, and weighs every count of far strata from running sums
    once each, so its work is the tail's strata and not the column's, and
    not the square of the far strata it weighs: here 5,000 of them, and
    10,000 at the doubled tail. Its sum is met to a step. The lines
    counted are Python's, so a copy of the column would pass unseen as
    one line: what the placement allocates is held to the tail in
    `test_rule_4_copies_no_column` (Codex's review of lane S4c, item 6).
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
    """G2's dense tail at 8,000 rows -- whole, in tenths, and low -- at seed 0: each twin's miss of the published mean distance in half grid steps; and rule 4's lines as its tail doubles and its lines and allocated bytes as its strata grow tenfold."""
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
    # AND WHAT IT ALLOCATES, which the lines cannot show: a copy of the
    # column is one line (Codex's review of lane S4c, item 6).
    small_peak, _kept = _placement_peak(folder / "small-peak", 100000, 10000)
    large_peak, _kept = _placement_peak(folder / "large-peak", 1000000, 10000)
    found["placement_allocated_growth_10x_strata"] = round(large_peak / small_peak, 2)
    found["placement_allocated_bytes_1m_strata_10000_tail"] = large_peak
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


def _twenty_row_tail(
    far: "list[float]",
    boundary: float = 1000.0,
    low: bool = False,
    band: str = generation._BAND_POSITIVE,
    pair: "tuple[float, float]" = (5131 / 20, (5023279 / 20) ** 0.5),
) -> "tuple[object, generation._NumericLayout, list[float], contract.TailReader, contract.TailSide]":
    """A hundred one-cell strata whose high tail of twenty is a run of fifteen from the boundary and the five ``far`` beyond it.

    The pair is the one five far cells at 1,000, 1,001, 1,002, 1,003 and
    1,005 steps would give: a mean distance of 5,131 / 20 and a mean
    square of 5,023,279 / 20. With ``low`` the tail is the low one, the
    run and the five ``far`` below the boundary; ``band`` is the five far
    strata's sign band and ``pair`` the published mean distance and
    root-mean-square distance.
    """
    described_facts = _numeric_facts(100, 100)
    object.__setattr__(described_facts, "percentiles", contract.NumberLadder.__new__(contract.NumberLadder))
    object.__setattr__(described_facts.percentiles, "minimum", None)
    object.__setattr__(described_facts.percentiles, "maximum", None)
    object.__setattr__(described_facts, "field_widths", {})
    object.__setattr__(described_facts, "pad_widths", {})
    object.__setattr__(described_facts, "thousands_marks", {})
    values = [boundary - 1000.0 + place for place in range(80)]
    values += [boundary + 1 + place for place in range(15)]
    values += [boundary + distance for distance in far]
    bands = [generation._BAND_POSITIVE] * 95 + [band] * 5
    if low:
        values = [2.0 * boundary - value for value in reversed(values)]
        bands = list(reversed(bands))
    layout = generation._NumericLayout(
        sizes=tuple([1] * 100),
        starts=tuple(range(100)),
        bands=tuple(bands),
        raw_budgets=(0, 0, 0, 0),
        folded_budgets=(0, 0, 0, 0),
    )
    reader = dataclasses.replace(_HIGH, low=low, rows=20, boundary=boundary, numbers=100, dense_grid=0)
    side = contract.TailSide.__new__(contract.TailSide)
    for name, value in (("rows", 20), ("mean_distance", pair[0]), ("rms_distance", pair[1])):
        object.__setattr__(side, name, value)
    return described_facts, layout, values, reader, side


def test_rule_4_places_the_far_strata_where_the_pair_says_and_leaves_a_tail_that_meets_it() -> None:
    """Twenty rows: five far strata go to 1,000 to 1,003 and 1,005 steps out -- the remainder on the outermost -- and a tail already summing to the mean stays."""
    facts, layout, values, reader, side = _twenty_row_tail([300.0, 400.0, 500.0, 600.0, 700.0])
    before = list(values)
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None
    assert placed is values, "written in place: no copy of the column (Codex's review of lane S4c, item 6)"
    assert [value - 1000.0 for value in placed[95:]] == [1000.0, 1001.0, 1002.0, 1003.0, 1005.0]
    assert placed[:95] == before[:95], "the run and everything inside it stay"
    facts, layout, values, reader, side = _twenty_row_tail([995.0, 1000.0, 1002.0, 1005.0, 1009.0])
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]


def test_rule_4_leaves_a_side_as_it_stood_where_a_rule_before_it_would_break() -> None:
    """Each case `_dense_side_placed` keeps a side in, beside the same side placed: an end, a band, the width census, a mean the far strata cannot reach.

    Skeptic 1 of lane S4c measured every one of these guards surviving
    its own mutant; each assertion here is red on one of them.
    """
    far = [300.0, 400.0, 500.0, 600.0, 700.0]
    facts, layout, values, reader, side = _twenty_row_tail(far)
    assert generation._dense_side_placed(facts, layout, values, reader, side) is not None  # type: ignore[arg-type]
    # A PUBLISHED END: the side stays where the block names its maximum.
    # Each case below starts again from the side as it stood, because a
    # placed side is written into the values in place.
    facts, layout, values, reader, side = _twenty_row_tail(far)
    object.__setattr__(facts.percentiles, "maximum", 1705.0)  # type: ignore[attr-defined]
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]
    # THE SIGN BANDS: below a boundary at -1,010 the far strata would go
    # to -10 to -5, past one at -995 to 5 to 10; a stratum stays in its
    # band, and none is placed in the zero band.
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=-1010.0, band=generation._BAND_NEGATIVE)
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None and placed[95:] == [-10.0, -9.0, -8.0, -7.0, -5.0], placed[95:]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=-1010.0)
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None, "positive"  # type: ignore[arg-type]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=-995.0)
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None and placed[95:] == [5.0, 6.0, 7.0, 8.0, 10.0], placed[95:]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=-995.0, band=generation._BAND_NEGATIVE)
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None, "negative"  # type: ignore[arg-type]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=-995.0, band=generation._BAND_ZERO)
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None, "zero"  # type: ignore[arg-type]
    # The low side, mirrored: above a boundary at 1,010 its far strata go
    # to 10 down to 5, and a negative band keeps them where they stood.
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=1010.0, low=True)
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None and placed[:5] == [5.0, 7.0, 8.0, 9.0, 10.0], placed[:5]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=1010.0, low=True, band=generation._BAND_NEGATIVE)
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]
    # THE WIDTH CENSUS: every number four figures wide; the far strata at
    # 9,300 to 9,700 would go to 10,000 and past it.
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=9000.0)
    object.__setattr__(facts, "field_widths", {"5": 100})
    assert generation._dense_side_placed(facts, layout, values, reader, side) is not None  # type: ignore[arg-type]
    facts, layout, values, reader, side = _twenty_row_tail(far, boundary=9000.0)
    object.__setattr__(facts, "field_widths", {"4": 100})
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]
    # A MEAN THE FAR STRATA CANNOT REACH PAST THE RUN: 170 / 20 steps, the
    # run alone summing to 120 of them.
    facts, layout, values, reader, side = _twenty_row_tail(far, pair=(170 / 20, 10.0))
    assert generation._dense_side_placed(facts, layout, values, reader, side) is None  # type: ignore[arg-type]


def test_rule_4_takes_the_fewest_far_strata_on_a_tie() -> None:
    """A mean distance of 842 / 20 and a root-mean-square of 76 leave four and five far strata missing `m rms**2` by the same 10,590: four are taken.

    The four stand at 175 to 178 steps and the fifth continues the run
    at 16.
    """
    facts, layout, values, reader, side = _twenty_row_tail([300.0, 400.0, 500.0, 600.0, 700.0], pair=(842 / 20, 76.0))
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None
    assert [value - 1000.0 for value in placed[95:]] == [16.0, 175.0, 176.0, 177.0, 178.0], placed[95:]


def test_one_grid_is_every_number_s_and_a_listed_withheld_or_flat_tail_is_never_dense() -> None:
    """`contract.tail_grid` and `contract._dense_grid`, the cases skeptic 1 of lane S4c found no test asking."""
    tenths = _numeric_facts(40, 40)
    object.__setattr__(tenths, "integer_valued", False)
    object.__setattr__(tenths, "fraction_widths", {"1": 40})
    assert contract.tail_grid(tenths) == 1
    object.__setattr__(tenths, "fraction_widths", {"1": 39})
    assert contract.tail_grid(tenths) == -1, "one width, but not every number used carries it"
    facts = _numeric_facts(40, 40)
    out = dataclasses.replace(_HIGH, steps=(101.0, 102.0, 103.0, 130.0))
    assert contract._dense_grid(out, facts, 8.0) == 0, "premise: this staircase is dense"
    for changed in (
        dataclasses.replace(out, listed=(130.0,), counts=(1,)),
        dataclasses.replace(out, withheld=True),
        dataclasses.replace(out, flat=True),
    ):
        assert contract._dense_grid(changed, facts, 8.0) == -1, changed


def test_the_twin_report_reads_a_dense_tail_s_mean_against_the_hull(tmp_path: pathlib.Path) -> None:
    """G2's dense tail at 80,000 rows: the twin's report covers the published mean distance and the twin's own only through the dense window.

    `generation._tail_approximations` draws the hull the checker draws.
    Measured on lane S4c's head 238e465: the report's window ran 1,174.99
    to 2,316.06 around a published 1,180.48 and a twin's 1,179.48, and
    G12.13's rank window alone, from 1,187.91, held neither (at 64,000
    rows it still held both).
    """
    described = _described_tail(tmp_path, "report80000", _dense_tail(80000))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    published = facts.tails.high.mean_distance
    assert published is not None
    rank_windows: "list[tuple[tuple[float, float], tuple[float, float]]]" = []
    drawn = generation._tail_window_of

    def recorded(*arguments: object, **keywords: object) -> "tuple[tuple[float, float], tuple[float, float]]":
        nonlocal rank_windows
        window = drawn(*arguments, **keywords)  # type: ignore[arg-type]
        rank_windows += [window]
        return window

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_tail_window_of", recorded)
        twin = generation.generate(described.loaded, 0)
    records = [record for record in twin.outcomes[0].approximations if record.fact == "tails.high.mean_distance"]
    assert len(records) == 1 and rank_windows, (records, rank_windows)
    record = records[0]
    achieved = float(record.achieved.replace(",", ""))
    assert rank_windows[-1][0][0] > max(published, achieved), ("premise: the rank window alone holds neither", rank_windows[-1])
    assert record.inside and record.covers_published, record
    assert float(record.lowest.replace(",", "")) <= min(published, achieved), record


# -- Codex's review of lane S4c ------------------------------------------------


def _codex_twin(folder: pathlib.Path, stem: str, cells: "list[str]", floor: "int | None" = 11) -> "tuple[kpi_shapes.Described, str, list[str]]":
    """Codex's scenarios: ``cells`` declared a measurement, described at ``floor``, loaded and generated at seed 0."""
    described = kpi_shapes.describe(folder, stem, numbers_and_codes._table({"value": cells}), floor, measured=["value"])
    twin = kpi_shapes.twin_text(described, 0)
    return described, twin, [cell.strip('"') for cell in twin.split("\n")[1:] if cell]


def _twin_without_rule_4(described: kpi_shapes.Described) -> str:
    """The twin with G6.6.8's rule 4 withdrawn, every other pass as it stands."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_tail_pair_met", lambda _facts, _layout, _rungs, values: values)
        return kpi_shapes.twin_text(described, 0)


def _high_reader(described: kpi_shapes.Described) -> contract.TailReader:
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    return ladder.high


def test_rule_4_keeps_what_the_width_and_mark_censuses_count(tmp_path: pathlib.Path) -> None:
    """Codex's item 1: five-figure fields stay five figures, and eleven grouped cells stay eleven.

    On 6121d55 the run, continued under ten thousand, wrote `7988` and
    `7990` in four figures where every source cell has five, and tenths
    grouped from `1,000.0` came back with nine grouped cells against
    eleven, both spelling checks WITHHELD under the floor. The placement
    is now refused where a width demand could take fewer of its cells,
    or the cells reaching a thousand number otherwise, and the twin is
    the one rule 4 leaves as it stood.
    """
    cells = [format(place, "05d") for place in range(7989)] + [str(10000 + 1000 * place) for place in range(11)]
    described, twin, written = _codex_twin(tmp_path / "width", "width", cells)
    assert _high_reader(described).dense_grid == 0, "premise: the high side is dense"
    assert [cell for cell in written if len(cell) != 5] == []
    assert twin == _twin_without_rule_4(described)
    cells = [format(place / 10, ".1f") for place in range(7989)] + [format(1000 + 100 * place, ",.1f") for place in range(11)]
    described, twin, written = _codex_twin(tmp_path / "marks", "marks", cells)
    assert _high_reader(described).dense_grid == 1, "premise: the high side is dense"
    assert sum("," in cell for cell in written) == 11
    outcome = kpi_shapes.measure(described, twin, "twin.csv")
    for subcheck in ("spelling.group_separator", "spelling.thousands_marks"):
        assert _verdict(outcome, subcheck)[0] == validation.HELD, subcheck
    assert twin == _twin_without_rule_4(described)


def test_rule_4_s_census_rule_is_the_oracle_s(tmp_path: pathlib.Path) -> None:
    """`_dense_census_kept` and the oracle's `census_kept` on the twenty-row tail: a width demand losing cells, one gaining them, the marks census, and a separator published alone.

    With the separator alone, five far cells of a thousand or more that
    would become four are refused, and none that would become five are
    taken, which the marks census refuses (the verifier of Codex's
    review of lane S4c).
    """
    far = [300.0, 400.0, 500.0, 600.0, 700.0]
    cases = [
        (9000.0, (5131 / 20, (5023279 / 20) ** 0.5), {"4": 100}, {}, "", False),
        (9000.0, (5131 / 20, (5023279 / 20) ** 0.5), {"5": 100}, {}, "", True),
        (900.0, (842 / 20, 76.0), {}, {",": 5}, "", False),
        (900.0, (842 / 20, 76.0), {}, {}, "", True),
        (900.0, (842 / 20, 76.0), {}, {}, ",", False),
        (0.0, (5131 / 20, (5023279 / 20) ** 0.5), {}, {}, ",", True),
        (0.0, (5131 / 20, (5023279 / 20) ** 0.5), {}, {",": 5}, ",", False),
        (1000.0, (5131 / 20, (5023279 / 20) ** 0.5), {}, {",": 100}, "", True),
    ]
    for boundary, pair, widths, marks, separator, taken in cases:
        facts, layout, values, reader, side = _twenty_row_tail(far, boundary=boundary, pair=pair)
        object.__setattr__(facts, "field_widths", widths)
        object.__setattr__(facts, "thousands_marks", marks)
        object.__setattr__(facts, "group_separator", separator)
        before = list(values)
        placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
        assert (placed is not None) == taken, (boundary, widths, marks, separator)
        assert _oracle_placed(before, boundary, pair, widths, marks, separator) == (None if placed is None else list(placed))


def _oracle_placed(
    values: "list[float]",
    boundary: float,
    pair: "tuple[float, float]",
    widths: "dict[str, int]",
    marks: "dict[str, int]",
    separator: str = "",
    figures: int = 0,
) -> "list[float] | None":
    """The oracle's `dense_side_placed` on `_twenty_row_tail`'s high side."""
    from tools.reference import make_generation_reference_vectors as oracle

    column = {
        "percentiles": {"min": None, "max": None},
        "integer_valued": True,
        "field_widths": widths,
        "pad_widths": {},
        "thousands_marks": marks,
        "group_separator": separator,
    }
    reader = {"percent": 95, "boundary": boundary}
    published = {"rows": 20, "mean_distance": pair[0], "rms_distance": pair[1]}
    placed = oracle.dense_side_placed(  # type: ignore[attr-defined]
        column, list(values), [1] * 100, ["positive"] * 100, reader, published, figures
    )
    return None if placed is None else list(placed)


def test_a_staircase_near_the_largest_double_reads_its_mean(tmp_path: pathlib.Path) -> None:
    """Codex's item 2: integers 1 to 89 beside eleven near `2e307`, at the default floor, generate; the mean is read without overflowing.

    On 6121d55 `generate` raised OverflowError in `math.fsum`, which
    adds the staircase's distances before dividing by their count.
    """
    cells = [str(place) for place in range(1, 90)] + [repr(2e307 * (1 + place / 11)) for place in range(11)]
    described, twin, _written = _codex_twin(tmp_path, "huge", cells, None)
    outcome = kpi_shapes.measure(described, twin, "twin.csv")
    assert kpi_shapes.missed(outcome) == []
    from fractions import Fraction

    from tools.reference import make_generation_reference_vectors as oracle

    distances = [2e307 * (1 + place / 11) for place in range(11)]
    exact = float(sum(Fraction(distance) for distance in distances) / 11)
    assert contract._finite_mean(distances) == exact
    assert oracle.staircase_mean(distances) == exact  # type: ignore[attr-defined]
    small = [1.0, 2.0, 4.5]
    assert contract._finite_mean(small) == oracle.staircase_mean(small) == 2.5  # type: ignore[attr-defined]
    assert not math.isfinite(contract._finite_mean([1.0, math.inf]))


def test_a_stand_in_passed_over_leaves_the_sum_within_a_step(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: a far run crossing `9999.0` lands on the published distance sum, not two steps past it.

    On 6121d55 the high tail's 80 rows, boundary 8743.601 on tenths,
    summed to 6563.42 against a published 6563.22: the run skipped the
    stand-in, every stratum after it a step further out, and the
    remainder only made up a shortfall.
    """
    cells = [f"{value / 10:.1f}" for value in range(79517, 87512)] + ["9998.5", "9998.7", "9999.3", "9999.8", "10000.0"]
    described, twin, written = _codex_twin(tmp_path, "skip", cells)
    reader = _high_reader(described)
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    side = facts.tails.high
    assert reader.dense_grid == 1 and side.mean_distance is not None, "premise: a dense tail on tenths"
    tail = sorted(float(cell) for cell in written)[len(written) - side.rows :]
    reached = sum(value - reader.boundary for value in tail)
    assert abs(reached - side.mean_distance * side.rows) <= 0.1 + 1e-6, reached
    assert "9999.0" not in written, "the stand-in is still passed over"
    # The same on the twenty-row tail, product and oracle: from 8,998
    # the far strata would stand at 1,000, 1,002 to 1,005 steps, past
    # `9,999`; laid a step nearer and the remainder put outward, they sum
    # to the published 5,011.
    far = [300.0, 400.0, 500.0, 600.0, 700.0]
    pair = (5131 / 20, (5023279 / 20) ** 0.5)
    facts_twenty, layout, values, reader_twenty, side_twenty = _twenty_row_tail(far, boundary=8998.0, pair=pair)
    before = list(values)
    placed = generation._dense_side_placed(facts_twenty, layout, values, reader_twenty, side_twenty)  # type: ignore[arg-type]
    assert placed is not None
    assert [value - 8998.0 for value in placed[95:]] == [999.0, 1000.0, 1002.0, 1003.0, 1007.0], placed[95:]
    assert _oracle_placed(before, 8998.0, pair, {}, {}) == list(placed)


def test_pieces_are_written_in_utf_8_only(tmp_path: pathlib.Path) -> None:
    """Codex's item 4: pieces in UTF-16, UTF-32 or UTF-8 with a signature are refused before anything is written.

    On 6121d55 each piece carried its own byte-order mark, so
    `["one\\n", "two\\n"]` in UTF-16 read back as `"one\\n\\ufefftwo\\n"`.
    """
    pieces = ["one\n", "two\n"]
    target = tmp_path / "parts.txt"
    writing.write_text_file(target, "untouched")
    for encoding in ("utf-16", "utf-8-sig", "utf-32", "utf-16-le", "utf-7", "latin-1"):
        with pytest.raises(ValueError):
            writing.write_text_file(target, "", encoding=encoding, pieces=pieces)
        assert target.read_text(encoding="utf-8") == "untouched", encoding
    whole = tmp_path / "whole.txt"
    writing.write_text_file(whole, "".join(pieces) + "ó", encoding="utf-8")
    for encoding in ("utf-8", "UTF-8", "utf_8", "UTF8"):
        writing.write_text_file(target, "", encoding=encoding, pieces=pieces + ["ó"])
        assert target.read_bytes() == whole.read_bytes(), encoding


def test_q_is_weighed_before_the_remainder_as_the_method_says() -> None:
    """Codex's item 5: the method says `q`'s squares are weighed before the remainder, as `_dense_side_placed` weighs them.

    Codex's twenty-row tail: a mean distance of 3,133 / 20 and a mean
    square of 2,602,123 / 20 put the far strata at 16, 17 and 992 to 995
    steps, `q` three, whose completed squares miss by 359,800 where a
    `q` of four at 16 and 747 to 753 would miss by 355,104. 6121d55's
    method said `q` was the count whose squares stand nearest.
    """
    facts, layout, values, reader, side = _twenty_row_tail(
        [300.0, 400.0, 500.0, 600.0, 700.0], pair=(3133 / 20, (2602123 / 20) ** 0.5)
    )
    placed = generation._dense_side_placed(facts, layout, values, reader, side)  # type: ignore[arg-type]
    assert placed is not None
    assert [value - 1000.0 for value in placed[95:]] == [16.0, 17.0, 992.0, 993.0, 995.0], placed[95:]
    method = pathlib.Path(__file__).resolve().parents[1] / "docs" / "spec" / "generation-method-v1.md"
    words = " ".join(method.read_text(encoding="utf-8").split())
    assert "with its far strata where the mean first puts them -- before a stand-in passed over or the remainder moves them -- stand nearest `m rms**2`" in words


def test_rule_4_copies_no_column(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: the placement allocates the same at 1,000,000 strata as at 100,000 with the same tail, and returns the list it was handed.

    On 6121d55 `list(values)` copied the column: eight bytes a stratum
    more at every size, which the Python lines counted in
    `test_rule_4_reads_the_tail_and_no_more_up_to_a_million_strata` show
    as one line.
    """
    peaks: "list[int]" = []
    same: "list[bool]" = []
    for strata in (100000, 1000000):
        peak, kept = _placement_peak(tmp_path / f"{strata}", strata, 10000)
        peaks += [peak]
        same += [kept]
    assert peaks[1] < peaks[0] + 262144, peaks
    assert peaks[1] < 4 * 1000000, peaks
    assert same == [True, True]


def _placement_peak(folder: pathlib.Path, strata: int, tail: int) -> "tuple[int, bool]":
    """The bytes rule 4's placement allocates at its peak on `_placement_inputs`' division, and whether it hands back the list it was given."""
    facts, layout, values, reader, side = _placement_inputs(folder, strata, tail)
    tracemalloc.start()
    try:
        placed = generation._dense_side_placed(facts, layout, values, reader, side)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    return peak, placed is values


# -- the verifier of Codex's review of lane S4c ----------------------------------


def test_a_separator_published_alone_keeps_its_grouped_cells(tmp_path: pathlib.Path) -> None:
    """Tenths beside eleven grouped from `1,000.0` and one bare `2100.0`: the marks census is refused, the comma published alone, and every grouped cell stays.

    The twin groups every cell of a thousand or more where the block
    publishes a separator, so on 19d0dd5 the run continued under a
    thousand wrote ten grouped cells at seeds 0 and 4 and
    `spelling.group_separator` fell under the floor, WITHHELD; 50a52d6
    wrote eleven and held it. A placement that leaves fewer placed cells
    reaching a thousand is now refused, and the twin is the one rule 4
    leaves as it stood.
    """
    cells = [format(place / 10, ".1f") for place in range(7988)]
    cells += [format(1000 + 100 * place, ",.1f") for place in range(11)] + ["2100.0"]
    described = kpi_shapes.describe(tmp_path, "alone", numbers_and_codes._table({"value": cells}), 11, measured=["value"])
    block = described.document["columns"][0]
    assert block["group_separator"] == "," and not block.get("thousands_marks"), "premise: the separator alone"
    assert _high_reader(described).dense_grid == 1, "premise: the high side is dense"
    for seed in (0, 4):
        twin = kpi_shapes.twin_text(described, seed)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_tail_pair_met", lambda _facts, _layout, _rungs, values: values)
            assert twin == kpi_shapes.twin_text(described, seed), seed
        outcome = kpi_shapes.measure(described, twin, f"twin-{seed}.csv")
        assert _verdict(outcome, "spelling.group_separator")[0] == validation.HELD, seed


def test_a_grid_past_the_largest_double_stays_as_it_stood(tmp_path: pathlib.Path) -> None:
    """Cells of 320 figures after the point, dense on the high side: `generate` writes the twin rule 4 leaves as it stood, and nothing is missed.

    Ten to the 309th is no double, so on 19d0dd5 the placement's scale
    raised OverflowError in `generate` and in the oracle; 50a52d6
    generated the profile clean. A grid of more than 308 figures now
    leaves the side as it stood, in product and oracle alike.
    """
    cells = ["0." + format(place, "0320d") for place in range(1, 7990)]
    cells += ["0." + format(10000 + 1000 * place, "0320d") for place in range(11)]
    described, twin, _written = _codex_twin(tmp_path, "fine", cells)
    assert _high_reader(described).dense_grid == 320, "premise: the high side is dense on a grid of 320 figures"
    assert kpi_shapes.missed(kpi_shapes.measure(described, twin, "twin.csv")) == []
    assert twin == _twin_without_rule_4(described)
    far = [300.0, 400.0, 500.0, 600.0, 700.0]
    facts, layout, values, reader, side = _twenty_row_tail(far)
    before = list(values)
    fine = dataclasses.replace(reader, dense_grid=309)
    assert generation._dense_side_placed(facts, layout, values, fine, side) is None  # type: ignore[arg-type]
    assert _oracle_placed(before, 1000.0, (5131 / 20, (5023279 / 20) ** 0.5), {}, {}, "", 309) is None
