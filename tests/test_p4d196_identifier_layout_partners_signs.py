"""Plan P4-D196: a declared identifier's layouts beside partners and signs.

THE REPRODUCTIONS (final skeptic of stage 2's close, MAJOR).

- `fold`: 300 record numbers `S1000` upward, about a tenth written again as
  a legacy lower-case `s` number, beside five-figure numbers and `S-NN-A`.
  Every cell wears a named layout, and `@%%%%` came back 212 of 214 at
  seeds 1 and 4: two fold-collision partners were handed to `S-NN-A`
  identities, whose partner wears no named layout, so two identities that
  should have worn `@%%%%` wore something else.
- `signs`: 200 record numbers `P###` beside `-##` and `+###`, publishing
  `{"+%%%": 38, "@%%%": 121}`. `+%%%` came back 37: only the packing with
  the sign family open packs the census, and a packing reaching for the
  sign the first answer did without was never taken -- though a named
  layout that is a sign before a number proves the table held such cells
  (plan P4-D156).

Every test is a round trip: describe with the column declared, generate,
describe the twin, and validate the twin and the real table.
"""

import pathlib
import random

import pytest

from tests.test_stage2_round_trip import _round_trip


def _shapes() -> "dict[str, list[str]]":
    """The skeptic's columns, drawn from one stream in the skeptic's order."""
    draw = random.Random(21)
    fold: "list[str]" = []
    for index in range(300):
        pick = draw.random()
        if pick < 0.7:
            fold += [f"S{1000 + index}"]
        elif pick < 0.8:
            fold += [f"s{1000 + index - draw.randrange(1, 5)}"]
        elif pick < 0.9:
            fold += [f"{draw.randrange(10000, 99999)}"]
        else:
            fold += [f"S-{draw.randrange(10, 99)}-A"]
    # The barcodes the skeptic drew next are drawn and set aside.
    for _index in range(400):
        pick = draw.random()
        if pick < 0.5:
            for _place in range(8):
                draw.choice("0123456789abcdef")
        elif pick < 0.8:
            draw.randrange(100000, 999999)
        else:
            draw.randrange(1000, 9999)
    signs: "list[str]" = []
    for _index in range(200):
        pick = draw.random()
        if pick < 0.6:
            signs += [f"P{draw.randrange(100, 999)}"]
        elif pick < 0.8:
            signs += [f"-{draw.randrange(1, 99)}"]
        else:
            signs += [f"+{draw.randrange(100, 999)}"]
    return {"fold": fold, "signs": signs}


def _layout_misses(folder: pathlib.Path) -> "list[str]":
    report = folder / "check-twin" / "real-twin-quality.txt"
    return [
        line.strip()
        for line in report.read_text(encoding="utf-8").splitlines()
        if "layout_forms" in line and line.strip().endswith("MISSED")
    ]


@pytest.mark.parametrize("seed", ["1", "4"])
def test_a_signed_layout_the_census_proves_is_held(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Mutation: the sign family refused again, and `+%%%` comes back one short."""
    cells = _shapes()["signs"]
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / seed, cells, ("--identifier", "value"), seed=seed
    )
    assert first["role"] == "identifier"
    published = first["layout_forms"]
    assert any(key[:1] == "+" for key in published), published
    for key in published:
        assert second["layout_forms"].get(key) == published[key], (
            seed, key, second["layout_forms"]
        )
    assert twin_exit == 0, (seed, _layout_misses(tmp_path / seed))
    assert real_exit == 0


@pytest.mark.parametrize("seed", ["1", "4"])
def test_partners_do_not_take_the_cells_no_layout_is_named_for(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The fold column: the shortfall falls from two cells to at most one.

    STILL SHORT BY ONE, AND THE REPORT NAMES IT: the identity carrying the
    published longest length can wear only `S-NN-A`, and G9.3 hands it a
    partner, which no packing of layouts moves. Mutation: the unnamed quota
    withdrawn, and `@%%%%` comes back 212 of 214 again.
    """
    cells = _shapes()["fold"]
    first, second, written, _twin_exit, real_exit = _round_trip(
        tmp_path / seed, cells, ("--identifier", "value"), seed=seed
    )
    assert real_exit == 0
    published = first["layout_forms"]
    assert "(withheld)" not in published
    assert sum(published.values()) == len(cells)
    held: "dict[str, int]" = {}
    for cell in written:
        key = "".join(
            "@" if "A" <= mark <= "Z" else "&" if "a" <= mark <= "z"
            else "%" if "0" <= mark <= "9" else mark
            for mark in cell
        )
        held[key] = (held[key] if key in held else 0) + 1
    assert second["n_distinct_folded"] == first["n_distinct_folded"]
    short = sum(
        max(0, published[key] - (held[key] if key in held else 0))
        for key in published
    )
    assert short <= 1, (seed, published, held)
    report = (tmp_path / seed / "real-twin-report.txt").read_text(encoding="utf-8")
    for key in published:
        if key in held and held[key] == published[key]:
            continue
        assert f"layout_forms.{key}" in report, key
    assert len(written) == len(cells)
