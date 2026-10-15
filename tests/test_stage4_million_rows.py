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

import pathlib
import sys
import tracemalloc

import pytest

import fixtures
import kpi_shapes
import test_stage4_numbers_and_codes as numbers_and_codes
from synthtwin import cli, parsing, quality, validation, writing

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
        patch.setattr(sys, "stdout", open(tmp_path / "screen.txt", "w", encoding="utf-8"))  # noqa: SIM115
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
