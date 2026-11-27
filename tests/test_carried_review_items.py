"""Gate file of lane LEDGER: carried items of the outside reviews of batches 4y, 4z and 4zz, closed where cheap and real.

WHAT IT HOLDS (each clause red on its mutant):

* Batch 4y's item 11: a keyed level's event gap is rounded to the nearest minute on both sides of nought -- a gap of
  -60 minutes reads -60 and one of -1 reads -1, not -59 and 0 (an event written at its anchor's minute); every gap at
  or above nought reads as it did (mutant: `int(x + 0.5)` again).
* Batch 4y's item 12: an unlinked block whose key's last run of figures is 309 or more figures long takes a key of its
  own drawn in whole numbers, where `float(10 ** width)` raised OverflowError; a run of 308 figures or fewer is drawn
  as it always was, byte for byte (mutants: the float draw at every width; the whole-number draw at every width).
* Batch 4z's items 7, 9 and 10, the real-range pass (`generation._inside_ranged`): a cell past the real end whose
  every draw rounds past it again is never written past it (mutant: the rounded fallback taken unread); a padded
  cell drawn again keeps its width, `0084` four figures (mutant: no padding); two spellings of one value past the
  end, `11` and `11.0`, take one new value, each in its own decimals (mutant: a new value a spelling).
* Batch 4z's item 15: the health data zoo counts a walk drawn from the record only where generate succeeded and the
  twin's report opens with a drawn twin's head, not wherever the first describe wrote a record (mutant: the record's
  existence alone).
* Batch 4zz's item 17: where the dates zone's ties deal the file's sort column again, the rows are sorted again by it
  (mutant: no sort after the ties).
* Batch 4zz's item 16: an SPSS column of codes 1, 1.5 and 2.25 written `1.00`, `1.50` and `2.25` keeps all three value
  labels, each code counted by its value (mutant: codes counted by spelling, which kept the third alone).
"""

from __future__ import annotations

from synthtwin import inside_keyed, inside_links


def test_an_event_gap_before_its_anchor_rounds_to_the_nearest_minute() -> None:
    assert inside_keyed._gap_at([-60, -60, -60], 0.4) == -60
    assert inside_keyed._gap_at([-1, -1], 0.9) == -1
    assert inside_keyed._gap_at([-61, -60], 0.5) == -60  # -60.5 rounds half up, as 59.5 rounds to 60
    assert inside_keyed._gap_at([-3, -2], 0.2) == -3  # -2.8
    # At or above nought, the same minute as before.
    assert inside_keyed._gap_at([0, 10], 0.25) == 3  # 2.5
    assert inside_keyed._gap_at([60, 60], 0.7) == 60
    assert inside_keyed._gap_at([1, 2], 0.49) == 1


def _key_of(width: int) -> "tuple[str, str]":
    taken = "K" + "7" * width
    found = inside_links._own_key(taken, bound=1, seed=11, block=3, spellings={taken: True}, merged={}, other_bound=1)
    return taken, found


def test_a_wide_key_of_its_own_is_drawn_in_whole_numbers() -> None:
    taken, found = _key_of(310)
    assert found != taken and len(found) == len(taken) and found[:1] == "K"
    assert found[1:].isdigit()
    # The whole-number draw keeps the share's leading figures as the float draw would have.
    share = inside_links._uniform(11, 7, (3 << 8) + 0)
    assert found[1:16] == f"{int(share * 1e15):015d}"


def test_a_narrow_key_of_its_own_is_drawn_as_it_always_was() -> None:
    for width in (1, 6, 15, 17, 40, 308):
        taken, found = _key_of(width)
        share = inside_links._uniform(11, 7, (3 << 8) + 0)
        expected = "K" + f"{int(share * float(10 ** width)):0{width}d}"[-width:]
        assert found == expected, width


# -- batch 4z's items 7, 9 and 10: the real-range pass (`generation._inside_ranged`) -----------------------------


def _ranged(cells: "list[str]", points: "list[float]", monkeypatch) -> "list[str]":  # type: ignore[no-untyped-def]
    import types

    from synthtwin import contract, generation, twinstore

    monkeypatch.setattr(generation, "_range_held", lambda _column: False)
    column = types.SimpleNamespace(name="x", role=contract.ROLE_CONTINUOUS)
    profile = types.SimpleNamespace(columns=[column])
    finished = [twinstore.held_column(list(cells))]
    zones = {"marginals": {"x": {"kind": "number", "quantiles": list(points)}}}
    generation._inside_ranged(profile, zones, finished, {"x": 0}, 0)  # type: ignore[arg-type]
    return twinstore.column_cells(finished[0])


def test_a_rounded_fallback_past_the_real_end_is_never_written(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Item 10: the outer grid points round to `0.3` at one decimal, past the real greatest value 0.26."""
    points = [0.1 + 0.16 * k / 1000 for k in range(1001)]
    out = _ranged(["0.2"] * 19999 + ["1.0"], points, monkeypatch)
    assert "0.3" not in out
    for cell in out:
        assert cell == "1.0" or points[0] <= float(cell) <= points[-1], cell


def test_a_padded_cell_drawn_again_keeps_its_width(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Item 7: a four-figure padded column's `0084`, under the real least value 100, came back `128`."""
    points = [100.0 + 400.0 * k / 1000 for k in range(1001)]
    out = _ranged(["0300"] * 19999 + ["0084"], points, monkeypatch)
    new = out[-1]
    assert new != "0084" and len(new) == 4 and new.isdigit() and 100 <= int(new) <= 500, new


def test_two_spellings_of_one_value_take_one_value(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Item 9: `11` and `11.0` past a real greatest value of 10 each drew a value of their own (`10`, `9.9`)."""
    points = [10.0 * k / 1000 for k in range(1001)]
    out = _ranged(["5.0"] * 19998 + ["11", "11.0"], points, monkeypatch)
    assert float(out[-2]) == float(out[-1]) <= 10.0, out[-2:]
    assert "." not in out[-2] and out[-1][-2:-1] == "." and out[-1][:-2] == out[-2], out[-2:]
    assert len({float(cell) for cell in out}) == 2


# -- batch 4z's item 15: a record written is no twin drawn (`health_zoo.run_table`) -------------------------------


def _walked(tmp_path, monkeypatch, generate_exit: int, report: "str | None") -> bool:  # type: ignore[no-untyped-def]
    import types

    import health_zoo
    from synthtwin import inside

    folder = tmp_path / "walk"

    def walk(table, place, _n, _seed, _refused):  # type: ignore[no-untyped-def]
        place.mkdir(parents=True, exist_ok=True)
        private = inside.default_places().private
        private.mkdir(parents=True, exist_ok=True)
        (private / f"t-profile-0{inside.SUFFIX}").write_text("record", encoding="utf-8", newline="\n")
        if report is not None:
            (place / f"{table.name}-twin-report.txt").write_text(report, encoding="utf-8", newline="\n")
        return {"steps": {"generate": {"exit": generate_exit, "error": ""}}}

    monkeypatch.setattr(health_zoo, "_walk_table", walk)
    table = types.SimpleNamespace(name="t")
    found = health_zoo.run_table(table, folder, 20000, 0, False, tmp_path / "beside")  # type: ignore[arg-type]
    return bool(found["inside_record"])


def test_a_record_written_is_no_twin_drawn(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from synthtwin import cli

    head = cli._INSIDE_REPORT_HEAD + ", which stays on this computer.\n"
    assert not _walked(tmp_path / "a", monkeypatch, 1, None)  # generate failed after the record was written
    assert not _walked(tmp_path / "b", monkeypatch, 0, "This report describes the twin table.\n")  # the description's twin
    assert _walked(tmp_path / "c", monkeypatch, 0, head)


# -- batch 4zz's item 17: the rows sorted again where the ties moved the sort column (`cli._gaps_tied_again`) -----


def _tied(monkeypatch, sort_column: int) -> "list[str]":  # type: ignore[no-untyped-def]
    import dataclasses
    import types

    from synthtwin import dialect, generation, inside_dates, twinstore

    rows = 200
    ends = [f"2024-01-{1 + row // 10:02d}" for row in range(rows)]  # sorted ascending, as the draw left them
    dealt = list(reversed(ends))  # the ties deal them again out of order

    @dataclasses.dataclass(frozen=True)
    class Held:
        held_columns: "tuple[object, ...]"
        names: "tuple[str, ...]"
        n_rows: int
        outcomes: "tuple[object, ...]"

    twin = Held((twinstore.held_column([f"{row}" for row in range(rows)]), twinstore.held_column(ends)),
                ("visit", "ended_at"), rows, ())
    order = dialect.RowOrder(sort_column, dialect.ASCENDING, dialect.COLLATION_TEXT)
    form = types.SimpleNamespace(row_order=order, columns=(types.SimpleNamespace(sequence_start=-1),) * 2)
    loaded = types.SimpleNamespace(columns=(), n_rows=rows, source=types.SimpleNamespace(dialect=form))
    monkeypatch.setattr(inside_dates, "tied", lambda _zone: True)
    monkeypatch.setattr(inside_dates, "tie_dates", lambda _zone: ["ended_at"])
    monkeypatch.setattr(inside_dates, "tie_columns", lambda _zone: [])
    monkeypatch.setattr(inside_dates, "tied_again", lambda *_args: {"ended_at": list(dealt)})
    monkeypatch.setattr(generation, "every_hole_spelling", lambda _loaded: ())
    from synthtwin import cli

    out = cli._gaps_tied_again(twin, loaded, {"zones": {"dates": {}}}, 0)
    return twinstore.column_cells(out.held_columns[1])


def test_a_sorted_twin_stays_sorted_after_the_ties(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    after = _tied(monkeypatch, 2)
    assert after == sorted(after)
    # A file sorted by no column keeps the ties' order as dealt.
    unsorted = _tied(monkeypatch, 0)
    assert unsorted != sorted(unsorted)


# -- batch 4zz's item 16: a number's value label counted by its value (`profile._published_native`) ---------------


def test_a_numbers_value_labels_are_counted_by_value(tmp_path) -> None:  # type: ignore[no-untyped-def]
    import json

    import pytest

    pandas = pytest.importorskip("pandas")
    pyreadstat = pytest.importorskip("pyreadstat")
    from synthtwin import cli

    codes = [1.0, 1.5, 2.25] * 140
    frame = pandas.DataFrame({"dose_band": codes, "sbp": [float(100 + index % 60) for index in range(len(codes))]})
    source = tmp_path / "visits.sav"
    pyreadstat.write_sav(frame, str(source), variable_display_width={"dose_band": 8},
                         variable_value_labels={"dose_band": {1.0: "Low", 1.5: "Middle", 2.25: "High"}},
                         variable_format={"dose_band": "F8.2"})
    assert cli.main(["profile", str(source)]) == 0
    block = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))["source"]["native"]
    # Each of the three codes is held by 140 cells, written `1.00`, `1.50` and `2.25`: all three labels stand.
    labels = json.dumps(block["columns"])
    for text in ("Low", "Middle", "High"):
        assert text in labels, labels[:600]
